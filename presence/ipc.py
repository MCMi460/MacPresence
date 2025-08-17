# Made by Deltaion Lee (MCMi460) on GitHub
# Thanks to https://robins.one/notes/discord-rpc-documentation.html
from os import environ
from socket import socket, AF_UNIX, SOCK_STREAM, SHUT_RDWR
from socket import error as socket_error
from json import dumps, loads
from struct import pack, unpack
from typing import Generator, Tuple
from uuid import uuid4


class IPC:
    def __init__(self, pipe: int, *, client_id: int = None):
        self.pipe = pipe
        self.client_id = client_id

        self.socket = socket(AF_UNIX, SOCK_STREAM)

        self.evts: dict = {}

        self.Opcode = {
            "HANDSHAKE": 0,
            "FRAME": 1,
            "CLOSE": 2,
            "PING": 3,
            "PONG": 4,
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
        for path in ("XDG_RUNTIME_DIR", "TMPDIR", "TMP", "TEMP"):
            if environ.get(path):
                return environ[path] + "/discord-ipc-%s" % self.pipe
        return "/tmp/discord-ipc-%s" % self.pipe

    def connect(self, **kwargs: dict):
        if kwargs.get("pipe") is not None:
            self.pipe: int = kwargs["pipe"]
        try:
            self.socket.connect(self.path)
        except socket_error as err:
            raise err
        return self._handshake(
            kwargs["client_id"] if "client_id" in kwargs else self.client_id
        )

    def _handshake(self, client_id: int):
        self._send(
            self.Opcode["HANDSHAKE"],
            {
                "v": 1,
                "client_id": str(client_id),
            },
        )

        return self._read()

    def _send(self, opcode: int, payload: dict):
        payload = dumps(payload).encode("utf-8")
        try:
            self.socket.send(pack("<II", opcode, len(payload)) + payload)
        except socket_error as err:
            raise err

    def _read(self) -> Generator[Tuple[tuple, dict], None, None]:
        response = self.socket.recv(1024)

        # Because of how generators work, events are only called when they are handled
        while len(response) > 0:
            header = unpack("<II", response[:8])
            data = loads(response[8 : 8 + header[1]].decode("utf-8"))
            if data["evt"] in self.evts:
                self.evts[data["evt"]](header, data)
            yield header, data
            response = response[8 + header[1] :]
        return

    def _subscribe(self, evt: str, func: callable):
        self.evts[evt] = func
        return self._request(
            self.Opcode["FRAME"],
            "SUBSCRIBE",
            {
                "evt": evt,
            },
        )

    def _unsubscribe(self, evt: str):
        del self.evts[evt]
        return self._request(
            self.Opcode["FRAME"],
            "UNSUBSCRIBE",
            {
                "evt": evt,
            },
        )

    def close(self):
        close = self._send(self.Opcode["CLOSE"], {})
        self.socket.shutdown(SHUT_RDWR)
        self.socket.close()
        return close

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _request(self, opcode: int, cmd: str, payload: dict):
        payload = dict(
            {
                "nonce": str(uuid4()),
                "cmd": cmd,
            },
            **payload
        )
        return self._send(opcode, payload)
