#pragma once
#include "esphome/core/component.h"
#include "esphome/core/hal.h"
#include "pairing_gate.h"
#include <mutex>
#include "esphome/components/wifi/wifi_component.h"
#include "esphome/components/web_server_base/web_server_base.h"

namespace esphome::airbridge_network {
class Network : public Component, public AsyncWebHandler {
 public:
  void set_pairing_key(const std::string &key) { pairing_key_ = key; }
  void set_pairing_pin(GPIOPin *pin) { pairing_pin_ = pin; }
  float get_setup_priority() const override { return setup_priority::AFTER_WIFI; }
  void setup() override { pairing_pin_->setup(); web_server_base::global_web_server_base->add_handler(this); }
  bool canHandle(AsyncWebServerRequest *r) const override {
    return (r->url() == "/airbridge/wifi" || r->url() == "/airbridge/pairing") && r->method() == HTTP_POST;
  }
  void handleRequest(AsyncWebServerRequest *r) override {
    if (r->url() == "/airbridge/pairing") {
      const auto header = r->get_header("X-Airbridge-Request");
      bool allowed = false;
      if (header.has_value() && header.value() == "pairing") {
        std::lock_guard<std::mutex> lock(pairing_mutex_);
        allowed = pairing_gate_.consume(millis());
      }
      auto *response = r->beginResponse(allowed ? 200 : 409, "text/plain",
          allowed ? pairing_key_ : "Hold BOOT for 2 seconds, release, then reveal within 30 seconds.");
      response->addHeader("Cache-Control", "no-store, max-age=0");
      response->addHeader("Pragma", "no-cache");
      response->addHeader("X-Content-Type-Options", "nosniff");
      r->send(response);
      return;
    }
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
    {
      std::lock_guard<std::mutex> lock(pairing_mutex_);
      pairing_gate_.sample(pairing_pin_->digital_read(), millis());
    }
    auto *w = wifi::global_wifi_component;
    if (testing_ && w->is_connected()) {
      const auto next = w->get_sta();
      w->save_wifi_sta(next.get_ssid(), next.get_password());
      cancel_timeout("rollback"); testing_ = false; pending_ = false;
      previous_ = wifi::WiFiAP{};
    }
  }
 protected:
  GPIOPin *pairing_pin_{nullptr};
  std::string pairing_key_;
  PairingGate pairing_gate_;
  std::mutex pairing_mutex_;
  bool pending_{false}, testing_{false};
  wifi::WiFiAP previous_;
};
}
