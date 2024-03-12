# Made by Deltaion Lee (MCMi460) on GitHub
from . import *

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
