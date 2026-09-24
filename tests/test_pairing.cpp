#include "../firmware/components/airbridge_network/pairing_gate.h"
#include <cassert>
using esphome::airbridge_network::PairingGate;
int main() {
  PairingGate gate;
  assert(!gate.consume(0));
  gate.sample(true,0);gate.sample(true,4000);gate.sample(false,4001);
  assert(!gate.consume(4002)); // held at boot is not authorization
  gate.sample(true,5000);gate.sample(false,6999);
  assert(!gate.consume(7000)); // short press rejected
  gate.sample(true,8000);gate.sample(false,10000);
  assert(gate.consume(10001));assert(!gate.consume(10002)); // one-shot
  gate.sample(true,12000);gate.sample(false,14000);
  assert(!gate.consume(44000)); // expiry
  gate.sample(true,0xfffffff0U);gate.sample(false,2100);
  assert(gate.consume(2101)); // millis wrap
  PairingGate reboot;
  assert(!reboot.consume(1));
}
