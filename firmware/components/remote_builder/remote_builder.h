#pragma once
#include "model.h"
#include "esphome/core/component.h"
#include "esphome/core/hal.h"
#include "esphome/components/json/json_util.h"
#include "esphome/components/web_server_base/web_server_base.h"
#include "nvs.h"
#include <atomic>
#include <functional>
#include <memory>
#include <mutex>

namespace esphome::remote_builder {
using namespace airbridge_builder;
class RemoteBuilder : public Component, public AsyncWebHandler {
 public:
  void set_tx_callback(std::function<void(int)> f){tx_=f;}
  void set_busy_callback(std::function<bool()> f){busy_=f;}
  float get_setup_priority() const override {return setup_priority::AFTER_WIFI;}
  void setup() override {
    nvs_handle_t h;
    if(nvs_open("bzp_builder",NVS_READONLY,&h)==ESP_OK) {
      auto loaded=std::make_unique<Store>(); size_t size=sizeof(Store);
      if(nvs_get_blob(h,"store_v2",loaded.get(),&size)==ESP_OK && size==sizeof(Store) && valid(*loaded))store_=*loaded;
      nvs_close(h);
    }
    web_server_base::global_web_server_base->add_handler(this);
  }
  bool canHandle(AsyncWebServerRequest *r) const override {
    return r->url()=="/airbridge/builder" && (r->method()==HTTP_GET || r->method()==HTTP_POST);
  }
  void handleBody(AsyncWebServerRequest *r, uint8_t *data, size_t len, size_t index, size_t total) override {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    // ESP-IDF dispatches HTTP requests serially. Raw JSON avoids the small
    // URL-encoded form limit and is received in bounded chunks.
    if(index==0)body_.clear();
    auto header=r->get_header("X-Airbridge-Request");
    if(total>26000 || !header.has_value() || header.value()!="builder")return;
    if(index==body_.size())body_.append(reinterpret_cast<const char *>(data),len);
  }
  bool learning() const {std::lock_guard<std::recursive_mutex> lock(mutex_);return learning_>=0;}
  bool capture_pending() const {std::lock_guard<std::recursive_mutex> lock(mutex_);return learning() || candidate_slot_>=0;}
  void cancel(){std::lock_guard<std::recursive_mutex> lock(mutex_);learning_=-1;candidate_slot_=-1;candidate_.clear();status_="Ready";}
  std::vector<int32_t> frame(int slot) const {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if(slot<0 || slot>=int(BUTTONS))return {};
    return unpack(store_.buttons[slot]);
  }
  void capture(const std::vector<int32_t> &p) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if(!learning() || !valid_pulses(p))return;
    candidate_=p;candidate_slot_=learning_;learning_=-1;
    status_="Command received — save or discard it";
  }
  void loop() override {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if(learning() && millis()-started_>=20000){cancel();status_="Capture timed out — try again";}
  }
  void handleRequest(AsyncWebServerRequest *r) override {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if(r->method()==HTTP_GET) {
      auto result=json::build_json([this](JsonObject root){
        root["schema"]=2;root["profile"]="433.937MHz ASK/OOK";
        root["status"]=status_;root["learning"]=learning_;root["candidate"]=candidate_slot_;
        root["pending"]=pending_.load();root["revision"]=revision_;root["error"]=error_;
        root["remaining"]=learning()?std::max(0,20-int((millis()-started_)/1000)):0;
        auto remotes=root["remotes"].to<JsonArray>();
        for(auto &name:store_.remotes)remotes.add(name);
        auto buttons=root["buttons"].to<JsonArray>();
        for(unsigned i=0;i<BUTTONS;++i){
          const auto &b=store_.buttons[i]; auto o=buttons.add<JsonObject>();
          o["slot"]=i;o["name"]=b.name;o["remote"]=b.remote;o["icon"]=b.icon;o["order"]=b.order;o["active"]=b.active;
          auto p=o["pulses"].to<JsonArray>();for(unsigned j=0;j<b.count;++j)p.add(b.pulses[j]);
        }
      });
      r->send(200,"application/json",result.c_str());return;
    }
    auto header=r->get_header("X-Airbridge-Request");
    if(!header.has_value() || header.value()!="builder"){body_.clear();r->send(400,"text/plain","Invalid request");return;}
    if(r->contentLength()>26000){body_.clear();r->send(400,"text/plain","Backup too large");return;}
    if(pending_.exchange(true)){r->send(409,"text/plain","Another request is pending");return;}
    std::string payload=std::move(body_);body_.clear();
    if(payload.empty() || payload.size()>26000 || payload.size()!=r->contentLength()){pending_=false;r->send(400,"text/plain","Invalid payload");return;}
    defer([this,payload](){
      std::lock_guard<std::recursive_mutex> lock(mutex_);
      error_.clear();
      bool parsed=json::parse_json(payload,[this](JsonObject root){apply(root);return true;});
      if(!parsed)error_="Invalid JSON";
      ++revision_;pending_=false;
    });
    // The ESPHome IDF adapter does not map HTTP 202. A 200 acknowledgment
    // only queues work; clients must still observe revision/error.
    r->send(200,"text/plain","Accepted");
  }
 protected:
  bool persist(const Store &next){
    nvs_handle_t h;
    esp_err_t result=nvs_open("bzp_builder",NVS_READWRITE,&h);
    if(result==ESP_OK){result=nvs_set_blob(h,"store_v2",&next,sizeof(next));if(result==ESP_OK)result=nvs_commit(h);nvs_close(h);}
    if(result!=ESP_OK){error_="Storage full or unavailable — existing remotes preserved. Export a backup.";return false;}
    store_=next;return true;
  }
  void apply(JsonObject root){
    std::string op=root["op"]|"";
    if(op=="cancel"){cancel();return;}
    if((busy_ && busy_())){error_="Radio busy or Vornado learning active";return;}
    if(op=="replace") {
      if(learning() || candidate_slot_>=0){error_="Save or discard the current capture first";return;}
      auto data=root["data"].as<JsonObject>();
      if(data["schema"]!=2 || std::string(data["profile"]|"")!="433.937MHz ASK/OOK" || data["remotes"].size()!=REMOTES || data["buttons"].size()!=BUTTONS){error_="Unsupported backup schema, capacity, or radio profile";return;}
      auto next=std::make_unique<Store>();
      for(unsigned i=0;i<REMOTES;++i){
        if(!data["remotes"][i].is<const char*>()){error_="Invalid remote name";return;}
        std::string name=data["remotes"][i].as<std::string>();
        if(name.size()>32 || name.find('\0')!=std::string::npos){error_="Names must be at most 32 UTF-8 bytes";return;}
        std::memcpy(next->remotes[i],name.c_str(),name.size()+1);
      }
      for(unsigned i=0;i<BUTTONS;++i){
        auto b=data["buttons"][i].as<JsonObject>(); auto &out=next->buttons[i];
        if(b["slot"]!=int(i) || !b["active"].is<bool>() || !b["name"].is<const char*>() || !b["remote"].is<int>() || !b["icon"].is<int>() || !b["order"].is<int>()){error_="Invalid button record";return;}
        std::string name=b["name"].as<std::string>();
        int remote=b["remote"],icon=b["icon"],order=b["order"];
        if(name.size()>32 || name.find('\0')!=std::string::npos || remote<0 || remote>=int(REMOTES) || icon<0 || icon>7 || order<0 || order>=int(BUTTONS)){error_="Invalid button fields";return;}
        std::memcpy(out.name,name.c_str(),name.size()+1);out.active=b["active"];out.remote=remote;out.icon=icon;out.order=order;
        if(!b["pulses"].is<JsonArray>() || b["pulses"].size()>PULSES){error_="Capture exceeds 256 pulses";return;}
        std::vector<int32_t> pulses;
        for(JsonVariant v:b["pulses"].as<JsonArray>()){
          if(!v.is<int32_t>()){error_="Pulse must be an integer";return;}pulses.push_back(v.as<int32_t>());
        }
        if(!pulses.empty() && (!out.active || !valid_pulses(pulses))){error_="Invalid pulse timings";return;}
        out.count=pulses.size();for(unsigned j=0;j<pulses.size();++j)out.pulses[j]=pulses[j];
      }
      if(!valid(*next)){error_="Buttons require a named remote and label";return;}
      if(persist(*next))status_="Remote layout saved";
      return;
    }
    if(!root["slot"].is<int>()){error_="Select a button";return;}
    int slot=root["slot"];
    if(slot<0 || slot>=int(BUTTONS) || !store_.buttons[slot].active){error_="Button is not configured";return;}
    if(op=="learn"){
      if(learning() || candidate_slot_>=0){error_="Save or discard the current capture first";return;}
      learning_=slot;candidate_.clear();started_=millis();status_="Listening — press the button on your original remote";
    }else if(op=="save"){
      if(candidate_slot_!=slot || !valid_pulses(candidate_)){error_="No candidate for this button";return;}
      auto next=std::make_unique<Store>(store_);auto &b=next->buttons[slot];b.count=candidate_.size();
      for(unsigned i=0;i<candidate_.size();++i)b.pulses[i]=candidate_[i];
      if(persist(*next)){cancel();status_="Command saved to flash";}
    }else if(op=="send"){
      if(learning() || candidate_slot_>=0 || frame(slot).empty()){error_="Finish learning and save this button before sending";return;}
      if(tx_){tx_(slot);status_="Send requested — check Bridge activity for replay result";}
    }else error_="Unknown operation";
  }
  Store store_{};
  std::function<void(int)> tx_;
  std::function<bool()> busy_;
  std::atomic<bool> pending_{false};
  int learning_{-1},candidate_slot_{-1};uint32_t started_{0},revision_{0};
  std::vector<int32_t> candidate_;
  std::string status_{"Ready"},error_;
  std::string body_;
  mutable std::recursive_mutex mutex_;
};
}
