from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/root", perm="elradfmwMT")
#authorizer.add_anonymous("/home/nobody")

handler = FTPHandler
handler.authorizer = authorizer
handler.passive_ports = range(30000, 30009)

server = FTPServer(("0.0.0.0", 21), handler)
server.serve_forever()
