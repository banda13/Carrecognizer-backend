import requests

url = "http://127.0.0.1:8000/accounts/login/"
url2 = "http://127.0.0.1:8000/core/classify/"
uname = 'szabag'
pw = 'Fosill13'

client = requests.session()

r0 = client.get(url)  # sets cookie
csrftoken = client.cookies['csrftoken']

login_data = {'login':uname, 'password':pw, 'csrfmiddlewaretoken':csrftoken} # FIXME sending password's non encrypted way??!

r_login = client.post(url, data=login_data)

csrftoken = client.cookies['csrftoken']
data = dict(csrfmiddlewaretoken=csrftoken)
files = {'carpic': open('430.jpg', 'rb')}

r = client.post(url2, data=data, files=files)
print(r.text)