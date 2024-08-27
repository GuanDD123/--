import requests
import json

parameter = "device_platform=webapp&aid=6383&channel=channel_pc_web&..."
url = "http://127.0.0.1:12080/go"
data = {
    "group": "zzz",
    "action": "getData",
    "param": json.dumps(
        {"parameter": parameter}
    )
}

res = requests.post(url, data=data)
print(res.text)
