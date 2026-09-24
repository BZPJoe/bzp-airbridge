#pragma once
#include <cstdint>
namespace esphome::airbridge_network {
// RAM only. Boot-held buttons cannot grant access; release, hold, release again.
class PairingGate {
 public:
  void sample(bool pressed, uint32_t now) {
    if (!armed_) { if (!pressed) armed_ = true; return; }
    if (pressed && !pressed_) started_ = now;
    if (!pressed && pressed_ && uint32_t(now - started_) >= 2000) {
      opened_ = now; available_ = true;
    }
    pressed_ = pressed;
  }
  bool consume(uint32_t now) {
    const bool allowed = available_ && uint32_t(now - opened_) < 30000;
    available_ = false;
    return allowed;
  }
 private:
  bool armed_{false}, pressed_{false}, available_{false};
  uint32_t started_{0}, opened_{0};
};
}
