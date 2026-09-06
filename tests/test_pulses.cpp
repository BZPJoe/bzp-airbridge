#include "../firmware/pulse_store.h"
#include <cassert>
#include <iostream>
int main() {
  std::vector<int32_t> valid;
  for (int i=0;i<32;i++) valid.push_back(i%2 ? -500 : 500);
  assert(airbridge::unpack(airbridge::pack(valid)) == valid);
  assert(airbridge::unpack(airbridge::Frame{}).empty());
  auto p=valid; p[3]=500; assert(!airbridge::valid(p));
  p=valid; p[0]=-500; assert(!airbridge::valid(p));
  p=valid; p[0]=0; assert(!airbridge::valid(p));
  p=valid; p[0]=INT32_MIN; assert(!airbridge::valid(p));
  p.resize(513); assert(!airbridge::valid(p));
  auto f=airbridge::pack(valid); f[0]=10000; assert(airbridge::unpack(f).empty());
  f[0]=-1; assert(airbridge::unpack(f).empty());
  p=valid; p[0]=30001; assert(!airbridge::valid(p));
  std::cout << "Pulse validation and storage tests passed\n";
}

