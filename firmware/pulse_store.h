#pragma once
#include <array>
#include <vector>
#include <cstdint>
#include <cstdlib>

namespace airbridge {
constexpr size_t MAX_PULSES = 512;
// Element zero stores length; remaining elements are signed microseconds.
using Frame = std::array<int32_t, MAX_PULSES + 1>;
inline bool valid(const std::vector<int32_t> &p) {
  if (p.size() < 16 || p.size() > MAX_PULSES || p.front() <= 0) return false;
  int64_t total = 0;
  for (size_t i=0; i<p.size(); ++i) {
    const int64_t value = p[i];
    const int64_t duration = value < 0 ? -value : value;
    if (duration < 50 || duration > 30000 || (i && ((p[i]>0)==(p[i-1]>0)))) return false;
    total += duration;
  }
  return total >= 3000 && total <= 500000;
}
inline Frame pack(const std::vector<int32_t> &p) {
  Frame f{};
  if (!valid(p)) return f;
  f[0] = static_cast<int32_t>(p.size());
  for (size_t i=0; i<p.size(); ++i) f[i+1] = p[i];
  return f;
}
inline std::vector<int32_t> unpack(const Frame &f) {
  if (f[0] < 16 || f[0] > static_cast<int32_t>(MAX_PULSES)) return {};
  std::vector<int32_t> p(f.begin()+1, f.begin()+1+f[0]);
  return valid(p) ? p : std::vector<int32_t>{};
}
}

