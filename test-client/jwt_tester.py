import json
import requests

files = {'carpic': open('430.jpg', 'rb')}
login_url = "http://127.0.0.1:8000/users/login/"
classify_url = "http://127.0.0.1:8000/core/classify/"
body = {
	"email": "szabag@idata.hu",
	"password": "asd123"
}

login_result = requests.post(login_url, body)
token = 'andy ' + json.loads(login_result.text)['token']
print(token)

files = {'carpic': open('430.jpg', 'rb')}
headers={'Authorization': token}

class_result = requests.post(classify_url, headers=headers, files=files)
print(class_result.text)
