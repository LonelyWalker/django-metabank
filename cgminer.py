# -*- coding:utf-8 -*-
import socket

try:
    import json
except ImportError:
    import simplejson as json


class Client:
    def __init__(self, host='localhost', port=4028):
        self.host = host
        self.port = port

    def command(self, command, *params):
        # sockets are one time use. open one for each command
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        parameter = ','.join(str(v) for v in params)

        try:
            sock.connect((self.host, self.port))
            if parameter:
                self._send(sock, json.dumps({"command": command, "parameter": parameter}))
            else:
                self._send(sock, json.dumps({"command": command}))
            received = self._receive(sock)

        finally:
            # shutdown and close the socket properly
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        # the null byte makes json decoding unhappy
        decoded = json.loads(received.replace('\x00', ''))

        return decoded

    def _send(self, sock, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def _receive(self, sock, size=65500):
        msg = ''
        while True:
            chunk = sock.recv(size)
            if chunk == '':
                # end of message
                break
            msg = msg + chunk
        return msg
