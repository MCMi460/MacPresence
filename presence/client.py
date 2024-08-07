# Made by Deltaion Lee (MCMi460) on GitHub
from . import *

class Client:
    def __init__(self, client_id:int, *, pipe:int = 0):
        self.IPC = IPC(pipe, client_id = client_id)
        self.IPC.connect()

        self.pid = os.getpid()

    def update(self, presence:typing.Optional[Presence] = None, *, handle_generator:bool = True):
        self.IPC._request(
            self.IPC.Opcode['FRAME'],
            'SET_ACTIVITY',
            {
                'args': {
                    'activity': presence.to_dict() if presence else None,
                    'pid': self.pid,
                }
            }
        )

        return list(self.read()) if handle_generator else self.read()
    
    def read(self):
        return self.IPC._read()
