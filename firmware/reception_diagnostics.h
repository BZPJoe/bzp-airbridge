#pragma once
#include "pulse_store.h"
#include "esphome/core/log.h"
namespace airbridge {
struct ReceptionDiagnostics {
  bool active = false;
  unsigned total = 0, valid_count = 0, samples = 0;
  unsigned energy_samples = 0, high_samples = 0;
  float energy_min = 100, energy_max = -200;
  void energy(float rssi, bool high) {
    if (!active) return;
    ++energy_samples;
    high_samples += high;
    energy_min = std::min(energy_min, rssi);
    energy_max = std::max(energy_max, rssi);
    if (energy_samples >= 10) {
      ESP_LOGI("airbridge.rxcheck", "RF energy: min=%.1f max=%.1f dBm GPIO3-high=%u/10 callbacks=%u", energy_min, energy_max, high_samples, total);
      energy_samples = high_samples = 0;
      energy_min = 100; energy_max = -200;
    }
  }
  void dump(const char *label, const std::vector<int32_t>& p) {
    ESP_LOGI("airbridge.rxcheck", "%s length=%u valid=%d", label, unsigned(p.size()), valid(p));
    for (size_t i=0; i<p.size(); i+=24) {
      std::string line;
      for (size_t j=i; j<p.size() && j<i+24; ++j) line += std::to_string(p[j]) + ",";
      ESP_LOGI("airbridge.rxcheck", "%s offset=%u %s", label, unsigned(i), line.c_str());
    }
  }
  void receive(const std::vector<int32_t>& p) {
    if (!active) return;
    ++total;
    if (valid(p)) ++valid_count;
    if (p.size() >= 16 && p.size() <= MAX_PULSES && samples < 6) {
      ++samples;
      dump("received", p);
    }
  }
};
inline ReceptionDiagnostics& rxcheck() { static ReceptionDiagnostics instance; return instance; }
}
