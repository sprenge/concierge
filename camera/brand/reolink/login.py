'''
Authenticate to Reolink cameras and receive a token for further configuration requests (get and put)
'''
import json
import requests

class FakeCode:
    def __init__(self):
        self.status_code = 999

class httpLogin:
    def __init__(self, camera_ip, user, password):
        self.port = 80
        self.user = user
        self.password = password
        self.camera_ip = camera_ip

    def get_token(self):
        login_payload  = [{
          "cmd":"Login",
          "action":0,
          "param": {
             "User":
               {"userName":self.user,
                "password":self.password
               }
           }
          }]
        url = 'http://'+self.camera_ip+'/cgi-bin/api.cgi?cmd=Login&token=null'
        try:
            r = requests.post(url, json=login_payload)
        except:
            r = FakeCode()
        if r.status_code == 200:
            resp = r.json()
            try:
                return resp[0]['value']['Token']['name']
            except:
                pass
        return None 

if __name__ == '__main__':
    l = httpLogin('192.168.1.46', 'admin', '12345678')
    token = l.get_token()
    print(token) 
