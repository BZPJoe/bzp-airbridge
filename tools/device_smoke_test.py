"""Opt-in builder API test on an EMPTY custom store. Never transmits RF.

stage creates synthetic test data; verify-cleanup checks persistence after a
reboot/OTA then removes only that known fixture. Legacy slots are untouched.
"""
import argparse
import copy
import json
import time
import urllib.request
import urllib.parse

p = argparse.ArgumentParser()
p.add_argument('--device', required=True)
p.add_argument('mode', choices=['stage', 'verify-cleanup'])
a = p.parse_args()
url = 'http://' + a.device + '/airbridge/builder'

def get():
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def post(payload, expect_error=False):
    revision = get()['revision']
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={'X-Airbridge-Request': 'builder', 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        assert r.status == 200
    for _ in range(20):
        time.sleep(.5)
        result = get()
        if result['revision'] != revision and not result['pending']:
            assert bool(result['error']) == expect_error, result['error']
            return result
    raise RuntimeError('Unknown request outcome; inspect device before retrying')

def blank(d):
    return {'schema': 2, 'profile': d['profile'], 'remotes': ['', '', '', ''],
            'buttons': [{'slot': i, 'name': '', 'remote': 0, 'icon': 0, 'order': i,
                         'active': False, 'pulses': []} for i in range(8)]}

d = get()
if a.mode == 'stage':
    assert not any(d['remotes']) and not any(b['active'] for b in d['buttons']), 'Custom store is not empty; refusing test'
    fixture = blank(d)
    fixture['remotes'][0] = '_BZP_TEST_'
    fixture['buttons'][0].update(active=True, name='Synthetic test', pulses=[400, -400] * 8)
    result = post({'op': 'replace', 'data': fixture})
    assert result['buttons'][0]['pulses'] == fixture['buttons'][0]['pulses']
    bad = copy.deepcopy(fixture)
    bad['buttons'][0]['pulses'][1] = 400
    result = post({'op': 'replace', 'data': bad}, expect_error=True)
    assert result['buttons'][0]['pulses'] == fixture['buttons'][0]['pulses']
    result = post({'op': 'learn', 'slot': 0})
    assert result['learning'] == 0
    result = post({'op': 'cancel'})
    assert result['learning'] == -1 and result['buttons'][0]['pulses'] == fixture['buttons'][0]['pulses']
    print('PASS: store roundtrip, invalid import rejection, learn/cancel preserves saved data. No RF transmitted.')
else:
    assert d['remotes'] == ['_BZP_TEST_', '', '', ''], 'Fixture changed; refusing cleanup'
    assert d['buttons'][0]['name'] == 'Synthetic test' and d['buttons'][0]['pulses'] == [400, -400] * 8
    assert not any(b['active'] for b in d['buttons'][1:]), 'Other custom buttons found; refusing cleanup'
    result = post({'op': 'replace', 'data': blank(d)})
    assert not any(b['active'] for b in result['buttons'])
    print('PASS: persisted fixture verified and removed. Legacy captures untouched; no RF transmitted.')
