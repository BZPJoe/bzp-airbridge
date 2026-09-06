#include "../firmware/components/remote_builder/model.h"
#include <cassert>
#include <iostream>
using namespace airbridge_builder;
int main(){
  Store s{};assert(valid(s));
  std::strcpy(s.remotes[0],"Test remote");auto &b=s.buttons[0];b.active=true;
  assert(!valid(s));std::strcpy(b.name,"Power");assert(valid(s));
  std::vector<int32_t> p(16);for(unsigned i=0;i<p.size();++i)p[i]=(i%2)?-400:400;
  assert(valid_pulses(p));b.count=p.size();for(unsigned i=0;i<p.size();++i)b.pulses[i]=p[i];
  assert(valid(s));assert(unpack(b)==p);
  b.count=257;assert(!valid(s));b.count=16;b.pulses[1]=400;assert(!valid(s));b.pulses[1]=-400;
  b.remote=4;assert(!valid(s));b.remote=0;b.icon=8;assert(!valid(s));b.icon=0;
  b.active=false;assert(!valid(s));b.active=true;s.magic=0;assert(!valid(s));s.magic=MAGIC;
  std::memset(b.name,'x',sizeof(b.name));assert(!valid(s));
  p[0]=-400;assert(!valid_pulses(p));p[0]=400;p[1]=INT32_MIN;assert(!valid_pulses(p));
  assert(!valid_pulses(std::vector<int32_t>(257,400)));
  std::cout<<"Builder storage and pulse validation passed; store bytes="<<sizeof(Store)<<"\n";
}
