# Made by Deltaion Lee (MCMi460) on GitHub
# Thanks to https://robins.one/notes/discord-rpc-documentation.html
from . import *

class IPC:
    def __init__(self, pipe:int, *, client_id:int = None):
        self.pipe = pipe
        self.client_id = client_id

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        self.Opcode = {
            'HANDSHAKE': 0,
            'FRAME': 1,
            'CLOSE': 2,
            'PING': 3,
            'PONG': 4,
        }
        self.RPC_Errors = [
            1000,
            4000,
            4002,
            4003,
            4004,
            4005,
            4006,
            4007,
            4008,
            4009,
            4010,
            5000,
            5001,
            5002,
            5003,
            5004,
        ]

    @property
    def path(self):
        for path in ('XDG_RUNTIME_DIR', 'TMPDIR', 'TMP', 'TEMP'):
            if os.environ.get(path):
                return os.environ[path] + '/discord-ipc-%s' % self.pipe
        return '/tmp/discord-ipc-%s' % self.pipe

    def connect(self, **kwargs:dict):
        if kwargs.get('pipe') is not None:
            self.pipe:int = kwargs['pipe']
        try:
            self.socket.connect(self.path)
        except socket.error as err:
            raise err
        return self._handshake(kwargs['client_id'] if 'client_id' in kwargs else self.client_id)

    def _handshake(self, client_id:int):
        self._send(self.Opcode['HANDSHAKE'], {
            'v': 1,
            'client_id': str(client_id),
        })

        return self._read()

    def _send(self, opcode:int, payload:dict):
        payload = json.dumps(payload).encode('utf-8')
        try:
            self.socket.send(struct.pack('<II', opcode, len(payload)) + payload)
        except socket.error as err:
            raise err

    def _read(self):
        response = self.socket.recv(1024)
        header = struct.unpack('<II', response[:8])
        data = json.loads(response[8:].decode('utf-8'))
        if data.get('code') in self.RPC_Errors:
            raise Exception('%s: %s' % (header, data))

        return header, data

    def close(self):
        close = self._send(self.Opcode['CLOSE'], {})
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        return close

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _request(self, opcode:int, cmd:str, payload:dict):
        payload = dict({
            'nonce': str(uuid.uuid4()),
            'cmd': cmd,
        }, **payload)
        return self._send(opcode, payload)
