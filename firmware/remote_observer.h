#pragma once
#include "pulse_store.h"
namespace airbridge {
// Match the complete frame, ignoring only its receiver-generated trailing idle.
inline bool matches(const std::vector<int32_t>& p, const Frame& f) {
  if (!valid(p)) return false;
  auto q = unpack(f);
  if (q.empty()) return false;
  size_t n = p.size() - (p.back() < 0 ? 1 : 0);
  size_t m = q.size() - (q.back() < 0 ? 1 : 0);
  if (n != m || n < 15) return false;
  for (size_t i=0; i<n; ++i) {
    if ((p[i]>0) != (q[i]>0)) return false;
    int64_t a = std::abs(p[i]), b = std::abs(q[i]);
    // 25% plus 80us accommodates receiver jitter without matching short/long bits.
    if (std::abs(a-b) > b/4 + 80) return false;
  }
  return true;
}
struct RemoteObserver {
  int last = -1;
  uint32_t seen = 0, muted = 0;
  bool has_mute = false;
  void mute(uint32_t now) { muted=now; has_mute=true; last=-1; }
  int receive(const std::vector<int32_t>& p, const Frame& power,
              const Frame& up, const Frame& down, uint32_t now) {
    if (has_mute && uint32_t(now-muted)<350) return -1;
    const Frame* frames[] = {&power,&up,&down};
    int found=-1;
    for (int i=0;i<3;++i) if (matches(p,*frames[i])) {
      if (found>=0) return -1; // Never guess between ambiguous captures.
      found=i;
    }
    if (found<0) return -1;
    bool repeat = found==last && uint32_t(now-seen)<350;
    last=found; seen=now;
    return repeat ? -1 : found;
  }
};
inline RemoteObserver& observer() { static RemoteObserver instance; return instance; }
}
