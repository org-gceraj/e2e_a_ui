import requests

ip = requests.get("https://api.ipify.org").text

# API_URL = "http://gceraj-api-svc:8000/predict"
API_URL = "http://"+ip+":30080/predict"
print ( API_URL)

