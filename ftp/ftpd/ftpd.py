import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import requests

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("sending ip address : ", cia)

class myFTPHandler(FTPHandler):
    def on_file_received(self, file):
        data = {"file": file}
        try:
            r = requests.post("http://"+cia+":5100/ftp/api/v1.0/files", json=data, timeout=10)
        except:
            pass

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/root", perm="elradfmwMT")
#authorizer.add_anonymous("/home/nobody")

# handler = FTPHandler
handler = myFTPHandler
handler.authorizer = authorizer
handler.passive_ports = range(30000, 30009)

server = FTPServer(("0.0.0.0", 21), handler)
server.serve_forever()
