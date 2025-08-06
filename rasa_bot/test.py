# test.py
import requests

res = requests.get("http://127.0.0.1:8000/api/questions/1/0")
print(res.status_code)
print(res.text)
