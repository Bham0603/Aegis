import json
import urllib.request

req = urllib.request.Request(
    'http://localhost:8000/api/v1/attack-lab/runs',
    data=b'{"scenario_id": "data_exfiltration_01"}',
    headers={'Authorization': 'Bearer aegis-W-fWzJ9PPdf9gn_4LoRbOH0KG17a5QtBxzhsEP0g3tA', 'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(req)
print(json.dumps(json.loads(response.read()), indent=2))
