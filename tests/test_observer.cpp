#include "../firmware/remote_observer.h"
#include <cassert>
#include <iostream>
int main() {
  std::vector<int32_t> p;
  for(int i=0;i<32;i++) p.push_back(i%2 ? -1000 : 400);
  auto power=airbridge::pack(p), up=power, down=power;
  up[3]=1400; down[5]=1400;
  airbridge::RemoteObserver o;
  assert(o.receive(p,power,up,down,1000)==0);
  assert(o.receive(p,power,up,down,1100)==-1);
  assert(o.receive(p,power,up,down,1400)==-1);
  assert(o.receive(p,power,up,down,1800)==0);
  auto jitter=p; jitter[0]+=60; jitter.back()=-12000;
  assert(airbridge::matches(jitter,power));
  jitter[2]=2000; assert(!airbridge::matches(jitter,power));
  assert(o.receive(p,power,power,down,2200)==-1);
  o.mute(3000); assert(o.receive(p,power,up,down,3100)==-1);
  assert(o.receive(p,power,up,down,3400)==0);
  assert(!airbridge::matches({},power));
  assert(!airbridge::matches(p,{}));
  std::cout << "Observer matching, jitter, ambiguity, repeat and TX suppression passed\n";
}
