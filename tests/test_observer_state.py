from pathlib import Path
import yaml
from jinja2 import Environment

package = yaml.safe_load((Path(__file__).parents[1] / 'examples/home-assistant/bzp_airbridge.yaml').read_text())
automation = next(a for a in package['automation'] if a['id'] == 'bzp_airbridge_observe_remote')
template = automation['actions'][-1]['data']['option']
env = Environment()
env.globals['states'] = lambda _: 'Medium'
render = lambda previous, slot: env.from_string(template).render(previous=previous, slot=slot).strip()
assert render('Off', 0) == 'Medium'
for state in ['Low', 'Medium', 'High']:
    assert render(state, 0) == 'Off'
assert render('Low', 1) == 'Medium'
assert render('Medium', 1) == 'High'
assert render('High', 1) == 'High'
assert render('High', 2) == 'Medium'
assert render('Medium', 2) == 'Low'
assert render('Low', 2) == 'Low'
assert render('Off', 1) == 'Off'
assert render('Off', 2) == 'Off'
print('Home Assistant observer state transitions passed')

# Exercise the actual observer templates with reconnect and explicit-sync events.
valid = env.from_string(automation['actions'][1]['value_template'])
gap = env.from_string(automation['actions'][2]['if'][0]['value_template'])
sync = automation['actions'][3]
sync_value = env.from_string(sync['then'][1]['data']['option'])
for level, state in enumerate(['Off', 'Low', 'Medium', 'High']):
    assert valid.render(origin='sync', slot=level) == 'True'
    assert sync_value.render(slot=level) == state
assert valid.render(origin='sync', slot=4) == 'False'
assert valid.render(origin='ready', slot=-1) == 'False'
assert gap.render(before=['12', 'tx', '1'], parts=['0', 'ready', '-1']) == 'True'
assert gap.render(before=[], parts=['13', 'tx', '1']) == 'True'
assert gap.render(before=['0', 'ready', '-1'], parts=['1', 'sync', '3']) == 'False'
assert gap.render(before=['13', 'tx', '1'], parts=['14', 'tx', '2']) == 'False'
assert list(automation['actions'][2]['then'][0]) == ['stop']
assert not any(a['id'] == 'bzp_airbridge_observer_disconnect' for a in package['automation'])
assert 'initial' not in package['input_select']['bzp_airbridge_estimated_state']
assert not any('button.press' == a.get('action') for a in sync['then'])
print('Reconnect preserves estimates; explicit sync handles Off/Low/Medium/High without RF')
