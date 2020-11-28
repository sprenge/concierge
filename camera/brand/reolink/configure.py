import json
import os
import requests
from login import httpLogin


class Osd:
    def __init__(self, token, host):
        self.token = token
        self.host = host

    def get_data(self):
        url = "http://"+self.host+"/api.cgi?cmd=GetOsd&token="+self.token
        payload = [{"cmd":"GetOsd","action":1,"param":{"channel":0}}]
        try:
            r = requests.post(url, json=payload)
            if r.status_code != 200:
                return None
            out = r.json()
        except Exception as e:
            print(e)
            return None
        ret_data = {}
        ret_data["name"] = out[0]['value']['Osd']['osdChannel']['name']
        return ret_data

    def put_data(self, new_data):
        url = "http://"+self.host+"/api.cgi?cmd=SetOsd&token="+self.token
        new_payload = [
            {"cmd":"SetOsd","action":0,"param":
                {"Osd":
                    {"bgcolor":0,"watermark":0,"channel":0,"osdChannel":
                        {"enable":1,"name":new_data["name"],"pos":"Lower Right"},
                    "osdTime":{"enable":1,"pos":"Top Center"}
                    }
                }
            }]
        try:
            r = requests.post(url, json=new_payload)
            if r.status_code == 200:
                return True
        except Exception as e:
            print(e)
        return False

class SystemGeneral:
    def __init__(self, token, host):
        self.token = token
        self.host = host

    def put_data(self, new_data):
        url = "http://"+self.host+"/api.cgi?token="+self.token
        new_payload = [
            {"cmd":"SetTime","action":0,"param":
                {"Time":
                    {"timeZone":new_data["timezone"],"timeFmt":"YYYY/MM/DD","hourFmt":0}   
                }
            }]
        try:
            r = requests.post(url, json=new_payload)
            if r.status_code == 200:
                return True
        except Exception as e:
            print(e)
        return False

class Ftp:
    def __init__(self, token, camera_ip_address, server_ip_address):
        self.token = token
        self.camera_ip_address = camera_ip_address
        self.server_ip_address = server_ip_address

    def put_data(self, new_data):
        url = "http://"+self.camera_ip_address+"/api.cgi?SetFtptoken="+self.token
        new_payload = [
            {"cmd":"SetFtp","action":0,"param":
                {"Ftp":
                    {"server":self.server_ip_address,"port":21,"maxSize":1000,"anonymous":0,"userName":new_data['user'],"password":new_data['password'],"remoteDir":"","streamType":0,"interval":15,"mode":1,
                    "schedule":{"enable":1,"table":"111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"}
                    }
                }
            }]
        try:
            r = requests.post(url, json=new_payload)
            if r.status_code == 200:
                return True
        except Exception as e:
            print(e)
        return False
    
    def get_data(self):
        url = "http://"+self.camera_ip_address+"/api.cgi?cmd=GetFtpd&token="+self.token
        payload = [{"cmd":"GetFtp","action":1,"param":{}}]
        try:
            r = requests.post(url, json=payload)
            if r.status_code != 200:
                return None
            out = r.json()
        except Exception as e:
            print(e)
            return None
        # ret_data = {}
        # ret_data["name"] = out[0]['value']['Osd']['osdChannel']['name']
        return out


if __name__ == '__main__':
    ip_address = '192.168.1.14'
    l = httpLogin(ip_address, 'admin', '12345678')
    token = l.get_token()
    # ftp = Ftp(token, ip_address, '192.168.1.6')
    # print (ftp.get_data())
    # new_p = {'user': 'user', 'password': '12345'}
    # ftp.put_data(new_p)
    # payload = {}
    # osd = Osd(token, ip_address)
    # print(osd.get_data())
    # new_p = {"name": "camerLisa"}
    # print(osd.put_data(new_p))
    sg = SystemGeneral(token, ip_address)
    new_p = {"timezone": -3600}
    # sg.put_data(new_p)

