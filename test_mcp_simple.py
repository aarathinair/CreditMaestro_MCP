# test_mcp_simple.py
import json
import requests

# Hard-code the Flask URL to IPv4
base_url = "http://127.0.0.1:5000"
path = "/getTransactions"

url = f"{base_url}{path}"
payload = {"startDate":"2025-04-01","endDate":"2025-04-30"}

print("→ URL:", url)
print("→ Payload:", payload)

resp = requests.post(url, json=payload)

print("← Status code:", resp.status_code)
print("← Response headers:", resp.headers)
print("← Response body:", resp.text)

try:
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    # swallow; we’ve already printed status/body
    pass
