import requests

url = "http://127.0.0.1:8000/accounts/login/"
url2 = "http://127.0.0.1:8000/core/classify/"
uname = 'andy'
pw = 'Fosill13'

client = requests.session()

r0 = client.get(url)  # sets cookie
csrftoken = ""
if 'csrftoken' in client.cookies:
    csrftoken = client.cookies['csrftoken']
else:
    print("gond van!")

login_data = dict(login=uname, password=pw, csrfmiddlewaretoken=csrftoken, next='/') # FIXME sending password's non encrypted way??!

r_login = client.post(url, data=login_data, headers=dict(Referer=url))

data = dict(csrfmiddlewaretoken=csrftoken)
files = {'carpic': open('430.jpg', 'rb')}

r = client.post(url2, data=data, files=files)
print(r.text)