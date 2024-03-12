# Made by Deltaion Lee (MCMi460) on GitHub
# Thanks to https://robins.one/notes/discord-rpc-documentation.html
from . import *

class Presence:
    def __init__(self, **fields) -> None:
        self._types:typing.List[typing.Tuple[str, type]] = [
            ('state', str),
            ('details', str),
            ('start', int),
            ('end', int),
            ('large_image', str),
            ('large_text', str),
            ('small_image', str),
            ('small_text', str),
            ('id', str),
            ('size', int),
            ('match', str),
            ('join', str),
            ('spectate', str),
            ('buttons', list),
            ('instance', bool),
        ]
        
        self._activity = self._fix_activity({
            'state': fields.get('state'),
            'details': fields.get('details'),
            'timestamps': {
                'start': fields.get('start'),
                'end': fields.get('end'),
            },
            'assets': {
                'large_image': fields.get('large_image'),
                'large_text': fields.get('large_text'),
                'small_image': fields.get('small_image'),
                'small_text': fields.get('small_text'),
            },
            'party': {
                'id': fields.get('party_id'),
                'size': fields.get('party_size'),
            },
            'secrets': {
                'match': fields.get('match'),
                'join': fields.get('join'),
                'spectate': fields.get('spectate'),
            },
            'buttons': fields.get('buttons'),
            'instance': fields.get('instance'),
        })
    
    def _fix_activity(self, dictionary:dict) -> typing.Optional[dict]:
        if all(x == None for x in dictionary.values()):
            return None
        for key in dictionary.copy():
            if isinstance(dictionary[key], dict):
                dictionary[key] = self._fix_activity(dictionary[key])
            if dictionary[key] is None:
                del dictionary[key]
            elif not isinstance(dictionary[key], dict(self._types)[key]):
                raise TypeError('Presence field \'%s\' does not match type \'%s\'' % (key, dict(self._types)[key]))
        return dictionary

    def to_JSON(self) -> str:
        return json.dumps(self._activity)
    
    def to_dict(self) -> dict:
        return self._activity
    
    def __str__(self) -> str:
        ret = []
        for key in self._activity:
            ret.append('%s: %s' % (key, self._activity[key]))
        return '\n'.join(ret)

class Client:
    def __init__(self, client_id:int, *, pipe:int = 0):
        self.IPC = IPC(pipe, client_id = client_id)
        self.IPC.connect()

        self.pid = os.getpid()

    def update(self, presence:Presence):
        self.IPC._request(
            self.IPC.Opcode['FRAME'],
            'SET_ACTIVITY',
            {
                'args': {
                    'activity': presence.to_dict(),
                    'pid': self.pid,
                }
            }
        )

        return self.read()
    
    def read(self):
        return self.IPC._read()
    
    def subscribe(self, **kwargs:dict):
        evt:str = kwargs['evt']
        return self.IPC._request(
            self.IPC.Opcode['FRAME'],
            'SUBSCRIBE',
            {
                'evt': evt,
            },
        )

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
