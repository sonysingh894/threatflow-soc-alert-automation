#!/var/ossec/framework/python/bin/python3
import sys
import json
import requests

alert_file = sys.argv[1]
webhook_url = sys.argv[3]

with open(alert_file) as f:
    alert_json = json.load(f)

requests.post(webhook_url, json=alert_json, timeout=10)
