#pragma once
#include "esphome/core/component.h"
#include "esphome/components/wifi/wifi_component.h"
#include "esphome/components/web_server_base/web_server_base.h"

namespace esphome::airbridge_network {
class Network : public Component, public AsyncWebHandler {
 public:
  float get_setup_priority() const override { return setup_priority::AFTER_WIFI; }
  void setup() override { web_server_base::global_web_server_base->add_handler(this); }
  bool canHandle(AsyncWebServerRequest *r) const override {
    return r->url() == "/airbridge/wifi" && r->method() == HTTP_POST;
  }
  void handleRequest(AsyncWebServerRequest *r) override {
    // Custom header rejects ordinary HTML form submissions. This is a trusted-LAN
    // endpoint without login; credentials never enter entities, events, or logs.
    const auto header = r->get_header("X-Airbridge-Request");
    if (!header.has_value() || header.value() != "wifi") {
      r->send(403, "text/plain", "Invalid request"); return;
    }
    if (pending_) { r->send(409, "text/plain", "A network change is already in progress"); return; }
    std::string ssid = r->arg("ssid").c_str(), password = r->arg("password").c_str();
    if (ssid.empty() || ssid.size() > 32 || password.size() < 8 || password.size() > 63) {
      r->send(400, "text/plain", "Use a 1–32 byte network name and an 8–63 character WPA password"); return;
    }
    pending_ = true;
    r->send(202, "text/plain", "Connecting. Reopen http://bzp-airbridge.local on the new network. If connection fails, the previous network will be restored.");
    set_timeout("apply", 500, [this, ssid, password]() {
      auto *w = wifi::global_wifi_component;
      previous_ = w->get_sta();
      // Test in RAM first. A power failure also returns to the saved network.
      wifi::WiFiAP next; next.set_ssid(ssid); next.set_password(password);
      w->disable(); w->set_sta(next); w->enable();
      testing_ = true;
      set_timeout("rollback", 45000, [this]() {
        auto *w = wifi::global_wifi_component;
        testing_ = false;
        w->disable(); w->set_sta(previous_); w->enable();
        previous_ = wifi::WiFiAP{}; pending_ = false;
      });
    });
  }
  void loop() override {
    auto *w = wifi::global_wifi_component;
    if (testing_ && w->is_connected()) {
      const auto next = w->get_sta();
      w->save_wifi_sta(next.get_ssid(), next.get_password());
      cancel_timeout("rollback"); testing_ = false; pending_ = false;
      previous_ = wifi::WiFiAP{};
    }
  }
 protected:
  bool pending_{false}, testing_{false};
  wifi::WiFiAP previous_;
};
}
