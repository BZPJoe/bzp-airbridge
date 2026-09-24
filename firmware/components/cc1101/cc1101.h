#pragma once

#include "esphome/core/component.h"
#include "esphome/core/hal.h"
#include "esphome/components/spi/spi.h"
#include "esphome/core/automation.h"
#include "cc1101defs.h"
#include <vector>
#include <driver/gpio.h>
#ifdef USE_ESP32
#include "soc/gpio_reg.h"
#include "soc/soc.h"
#endif

namespace esphome::cc1101 {

enum class CC1101Error { NONE = 0, TIMEOUT, PARAMS, CRC_ERROR, FIFO_OVERFLOW, PLL_LOCK };

class CC1101Listener {
 public:
  virtual void on_packet(const std::vector<uint8_t> &packet, float freq_offset, float rssi, uint8_t lqi) = 0;
};

class CC1101Component final : public Component,
                              public spi::SPIDevice<spi::BIT_ORDER_MSB_FIRST, spi::CLOCK_POLARITY_LOW,
                                                    spi::CLOCK_PHASE_LEADING, spi::DATA_RATE_1MHZ> {
 public:
  CC1101Component();

  void setup() override;
  void loop() override;
  void dump_config() override;
  void configure();

  // Actions
  void begin_tx();
  void begin_rx();
  void reset();
  void set_idle();
  void begin_original_rx() {
    if (reference_active_) return;
    reference_saved_ = state_;
    reference_active_ = true;
    enter_idle_();
    // Original published firmware's modem/analog settings. Keep GDO0
    // high impedance: it shares the ESP's driven TX line, not the RX wire.
    const uint8_t settings[][2] = {
      {0x00,0x0D},{0x01,0x2E},{0x02,0x2E},{0x03,0x07},
      {0x10,0x87},{0x11,0x93},{0x12,0x32},{0x13,0x22},{0x14,0xF8},
      {0x18,0x14},{0x19,0x36},{0x1B,0xC7},{0x1C,0x00},{0x1D,0xB1},
      {0x20,0xF8},{0x21,0x56},{0x22,0x11},{0x2C,0x88},{0x2D,0x31}
    };
    for (const auto &setting : settings) state_.regs()[setting[0]] = setting[1];
    configure();
  }
  // Temporary RX-only comparison with the Flipper CC1101 OOK 270 kHz
  // register profile, adapted for GDO2 reception and our existing frequency.
  void begin_reference_rx() {
    if (reference_active_) return;
    reference_saved_ = state_;
    reference_active_ = true;
    enter_idle_();
    strobe_(Command::RES);
    delay(5);
    read_(Register::IOCFG2, state_.regs(), 47);
    const uint8_t settings[][2] = {
      {0x00,0x0D},{0x01,0x2E},{0x02,0x2E},{0x03,0x47},
      {0x08,0x32},{0x0A,0x00},{0x0B,0x06},
      {0x10,0x67},{0x11,0x32},{0x12,0x30},{0x13,0x00},{0x14,0x00},
      {0x18,0x18},{0x19,0x18},{0x1B,0x03},{0x1C,0x00},{0x1D,0x40},
      {0x20,0xFB},{0x21,0xB6},{0x22,0x11},{0x2C,0x81},{0x2D,0x35}
    };
    for (const auto &setting : settings) state_.regs()[setting[0]] = setting[1];
    for (unsigned i = 0x0D; i <= 0x0F; ++i) state_.regs()[i] = reference_saved_.regs()[i];
    configure();
  }
  void end_reference_rx() {
    if (!reference_active_) return;
    enter_idle_();
    state_ = reference_saved_;
    reference_active_ = false;
    configure();
    begin_rx();
  }
  // Board-specific diagnostic: GDO2 is wired to GPIO3 on Airbridge.
  // TI SWRS061: 0x2F drives low, inversion bit 0x40 drives high.
  // Never enters TX and restores the original output selection afterwards.
  void test_receive_line() {
    uint8_t original;
    this->read_(Register::IOCFG2, &original, 1);
    unsigned lows = 0, highs = 0;
    for (unsigned i = 0; i < 12; ++i) {
      this->write_(Register::IOCFG2, 0x2F);
      delayMicroseconds(500);
      lows += gpio_get_level(GPIO_NUM_3) == 0;
      this->write_(Register::IOCFG2, 0x6F);
      delayMicroseconds(500);
      highs += gpio_get_level(GPIO_NUM_3) == 1;
    }
    this->write_(Register::IOCFG2, 0x2F);
    delayMicroseconds(500);
    this->write_(Register::IOCFG2, original);
    ESP_LOGI("airbridge.rxcheck", "Receive line self-test: IOCFG2=%02X low=%u/12 high=%u/12", original, lows, highs);
  }
  uint8_t diagnostic_state() {
    this->read_(Register::MARCSTATE);
    return this->state_.MARC_STATE;
  }
  float diagnostic_rssi() {
    uint8_t raw;
    this->read_(Register::RSSI, &raw, 1);
    return float(int8_t(raw)) * 0.5f - 74.0f;
  }
  void diagnostic_dump() {
    uint8_t registers[47];
    this->read_(Register::IOCFG2, registers, sizeof(registers));
    for (unsigned i = 0; i < sizeof(registers); i += 8) {
      std::string line;
      for (unsigned j = i; j < sizeof(registers) && j < i + 8; ++j) {
        char value[5];
        snprintf(value, sizeof(value), "%02X ", registers[j]);
        line += value;
      }
      ESP_LOGI("airbridge.radio", "Registers %02X: %s", i, line.c_str());
    }
    uint8_t part, version, packet, calibration;
    this->read_(Register::PARTNUM, &part, 1);
    this->read_(Register::VERSION, &version, 1);
    this->read_(Register::PKTCTRL0, &packet, 1);
    this->read_(Register::FSCAL1, &calibration, 1);
    ESP_LOGI("airbridge.radio", "PART=%02X VERSION=%02X STATE=%02X PKTCTRL0=%02X FSCAL1=%02X", part, version, diagnostic_state(), packet, calibration);
    uint8_t pa[8], front, modem, gdo, freq[3];
    this->read_(Register::PATABLE, pa, 8);
    this->read_(Register::FREND0, &front, 1);
    this->read_(Register::MDMCFG2, &modem, 1);
    this->read_(Register::IOCFG0, &gdo, 1);
    this->read_(Register::FREQ2, freq, 3);
    ESP_LOGI("airbridge.radio", "PA=%02X,%02X FREND0=%02X MDMCFG2=%02X IOCFG0=%02X FREQ=%02X%02X%02X", pa[0], pa[1], front, modem, gdo, freq[0], freq[1], freq[2]);
#if defined(CONFIG_IDF_TARGET_ESP32C3)
    ESP_LOGI("airbridge.radio", "GPIO1 output routing=%08X enable=%08X (RMT sources 51/52)", unsigned(REG_READ(GPIO_FUNC1_OUT_SEL_CFG_REG)), unsigned(REG_READ(GPIO_ENABLE_REG)));
#endif
  }

  // GDO Pin Configuration
  void set_gdo0_pin(InternalGPIOPin *pin) { this->gdo0_pin_ = pin; }

  // Configuration Setters
  void set_output_power(float value);
  void set_rx_attenuation(RxAttenuation value);
  void set_dc_blocking_filter(bool value);

  // Tuner settings
  void set_frequency(float value);
  void set_if_frequency(float value);
  void set_filter_bandwidth(float value);
  void set_channel(uint8_t value);
  void set_channel_spacing(float value);
  void set_fsk_deviation(float value);
  void set_msk_deviation(uint8_t value);
  void set_symbol_rate(float value);
  void set_sync_mode(SyncMode value);
  void set_carrier_sense_above_threshold(bool value);
  void set_modulation_type(Modulation value);
  void set_manchester(bool value);
  void set_num_preamble(uint8_t value);
  void set_sync1(uint8_t value);
  void set_sync0(uint8_t value);

  // AGC settings
  void set_magn_target(MagnTarget value);
  void set_max_lna_gain(MaxLnaGain value);
  void set_max_dvga_gain(MaxDvgaGain value);
  void set_carrier_sense_abs_thr(int8_t value);
  void set_carrier_sense_rel_thr(CarrierSenseRelThr value);
  void set_lna_priority(bool value);
  void set_filter_length_fsk_msk(FilterLengthFskMsk value);
  void set_filter_length_ask_ook(FilterLengthAskOok value);
  void set_freeze(Freeze value);
  void set_wait_time(WaitTime value);
  void set_hyst_level(HystLevel value);

  // Frequency offset compensation and bit synchronization settings
  void set_foc_bs_cs_gate(bool value);
  void set_foc_limit(FocLimit value);
  void set_foc_pre_k(FocPreK value);
  void set_foc_post_k(FocPostK value);
  void set_bs_limit(BsLimit value);
  void set_bs_pre_ki(BsPreKi value);
  void set_bs_pre_kp(BsPreKp value);
  void set_bs_post_ki(BsPostKi value);
  void set_bs_post_kp(BsPostKp value);

  // Packet mode settings
  void set_packet_mode(bool value);
  void set_packet_length(uint8_t value);
  void set_crc_enable(bool value);
  void set_whitening(bool value);

  // Packet mode operations
  CC1101Error transmit_packet(const std::vector<uint8_t> &packet);
  void register_listener(CC1101Listener *listener) { this->listeners_.push_back(listener); }
  Trigger<std::vector<uint8_t>, float, float, uint8_t> *get_packet_trigger() { return &this->packet_trigger_; }

 protected:
  uint16_t chip_id_{0};
  bool initialized_{false};

  float output_power_requested_{10.0f};
  float output_power_effective_{10.0f};
  uint8_t pa_table_[PA_TABLE_SIZE]{};

  CC1101State state_;
  CC1101State reference_saved_{};
  bool reference_active_{false};

  // GDO pin for packet reception
  InternalGPIOPin *gdo0_pin_{nullptr};
  static void IRAM_ATTR gpio_intr(CC1101Component *arg);

  // Packet handling
  void call_listeners_(const std::vector<uint8_t> &packet, float freq_offset, float rssi, uint8_t lqi);
  Trigger<std::vector<uint8_t>, float, float, uint8_t> packet_trigger_;
  std::vector<uint8_t> packet_;
  std::vector<CC1101Listener *> listeners_;

  // Low-level Helpers
  uint8_t strobe_(Command cmd);
  void write_(Register reg);
  void write_(Register reg, uint8_t value);
  void write_(Register reg, const uint8_t *buffer, size_t length);
  void read_(Register reg);
  void read_(Register reg, uint8_t *buffer, size_t length);

  // State Management
  bool wait_for_state_(State target_state, uint32_t timeout_ms = 100);
  bool enter_calibrated_(State target_state, Command cmd);
  void enter_idle_();
  bool enter_rx_();
  bool enter_tx_();
};

// Action Wrappers
template<typename... Ts> class BeginTxAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  void play(const Ts &...x) override { this->parent_->begin_tx(); }
};

template<typename... Ts> class BeginRxAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  void play(const Ts &...x) override { this->parent_->begin_rx(); }
};

template<typename... Ts> class ResetAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  void play(const Ts &...x) override { this->parent_->reset(); }
};

template<typename... Ts> class SetIdleAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  void play(const Ts &...x) override { this->parent_->set_idle(); }
};

template<typename... Ts> class SendPacketAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  void set_data_template(std::function<std::vector<uint8_t>(Ts...)> func) { this->data_func_ = func; }
  void set_data_static(const uint8_t *data, size_t len) {
    this->data_static_ = data;
    this->data_static_len_ = len;
  }

  void play(const Ts &...x) override {
    if (this->data_func_) {
      auto data = this->data_func_(x...);
      this->parent_->transmit_packet(data);
    } else if (this->data_static_ != nullptr) {
      std::vector<uint8_t> data(this->data_static_, this->data_static_ + this->data_static_len_);
      this->parent_->transmit_packet(data);
    }
  }

 protected:
  std::function<std::vector<uint8_t>(Ts...)> data_func_{};
  const uint8_t *data_static_{nullptr};
  size_t data_static_len_{0};
};

template<typename... Ts> class SetSymbolRateAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, symbol_rate)
  void play(const Ts &...x) override { this->parent_->set_symbol_rate(this->symbol_rate_.value(x...)); }
};

template<typename... Ts> class SetFrequencyAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, frequency)
  void play(const Ts &...x) override { this->parent_->set_frequency(this->frequency_.value(x...)); }
};

template<typename... Ts> class SetOutputPowerAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, output_power)
  void play(const Ts &...x) override { this->parent_->set_output_power(this->output_power_.value(x...)); }
};

template<typename... Ts> class SetModulationTypeAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(Modulation, modulation_type)
  void play(const Ts &...x) override { this->parent_->set_modulation_type(this->modulation_type_.value(x...)); }
};

template<typename... Ts> class SetRxAttenuationAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(RxAttenuation, rx_attenuation)
  void play(const Ts &...x) override { this->parent_->set_rx_attenuation(this->rx_attenuation_.value(x...)); }
};

template<typename... Ts>
class SetDcBlockingFilterAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(bool, dc_blocking_filter)
  void play(const Ts &...x) override { this->parent_->set_dc_blocking_filter(this->dc_blocking_filter_.value(x...)); }
};

template<typename... Ts> class SetManchesterAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(bool, manchester)
  void play(const Ts &...x) override { this->parent_->set_manchester(this->manchester_.value(x...)); }
};

template<typename... Ts> class SetFilterBandwidthAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, filter_bandwidth)
  void play(const Ts &...x) override { this->parent_->set_filter_bandwidth(this->filter_bandwidth_.value(x...)); }
};

template<typename... Ts> class SetFskDeviationAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, fsk_deviation)
  void play(const Ts &...x) override { this->parent_->set_fsk_deviation(this->fsk_deviation_.value(x...)); }
};

template<typename... Ts> class SetMskDeviationAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(uint8_t, msk_deviation)
  void play(const Ts &...x) override { this->parent_->set_msk_deviation(this->msk_deviation_.value(x...)); }
};

template<typename... Ts> class SetChannelAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(uint8_t, channel)
  void play(const Ts &...x) override { this->parent_->set_channel(this->channel_.value(x...)); }
};

template<typename... Ts> class SetChannelSpacingAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, channel_spacing)
  void play(const Ts &...x) override { this->parent_->set_channel_spacing(this->channel_spacing_.value(x...)); }
};

template<typename... Ts> class SetIfFrequencyAction final : public Action<Ts...>, public Parented<CC1101Component> {
 public:
  TEMPLATABLE_VALUE(float, if_frequency)
  void play(const Ts &...x) override { this->parent_->set_if_frequency(this->if_frequency_.value(x...)); }
};

}  // namespace esphome::cc1101
