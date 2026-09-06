#pragma once
#include <array>
#include <cstdint>
#include <cstring>
#include <vector>

namespace airbridge_builder {
constexpr unsigned BUTTONS = 8, REMOTES = 4, PULSES = 256;
constexpr uint32_t MAGIC = 0x425A5002;
struct Button {
  char name[33]{};
  uint8_t remote{0}, icon{0}, order{0};
  bool active{false};
  uint16_t count{0};
  int16_t pulses[PULSES]{};
};
struct Store {
  uint32_t magic{MAGIC};
  char remotes[REMOTES][33]{};
  Button buttons[BUTTONS]{};
};
inline bool valid_pulses(const std::vector<int32_t> &p) {
  if (p.size() < 16 || p.size() > PULSES || p.front() <= 0) return false;
  int64_t total=0;
  for (unsigned i=0;i<p.size();++i) {
    int64_t d=p[i]; if(d<0)d=-d;
    if(d<50 || d>30000 || (i && ((p[i]>0)==(p[i-1]>0))))return false;
    total+=d;
  }
  return total>=3000 && total<=500000;
}
inline std::vector<int32_t> unpack(const Button &b) {
  if(!b.active || b.count<16 || b.count>PULSES)return {};
  std::vector<int32_t> p(b.pulses,b.pulses+b.count);
  return valid_pulses(p)?p:std::vector<int32_t>{};
}
inline bool valid(const Store &s) {
  if(s.magic!=MAGIC)return false;
  for(const auto &r:s.remotes)if(!std::memchr(r,0,sizeof(r)))return false;
  for(const auto &b:s.buttons) {
    if(!std::memchr(b.name,0,sizeof(b.name)) || b.remote>=REMOTES || b.icon>7 || b.order>=BUTTONS)return false;
    if(b.active && (!b.name[0] || !s.remotes[b.remote][0]))return false;
    if(b.count && unpack(b).empty())return false;
  }
  return true;
}
}
