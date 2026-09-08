import os
from dotenv import load_dotenv
import socket
import hashlib
from Crypto.Cipher import AES

from ..common.ratelimiter import RateLimiter

load_dotenv()

class AniDBClient():
    def __init__(self) -> None:
        self.host = os.getenv("ANIDB_HOST", "api.anidb.net")
        self.port = int(os.getenv("ANIDB_PORT", 9000))
        self.api_key = os.getenv("ANIDB_API_KEY")
        self.local_port = int(os.getenv("ANIDB_LOCAL_PORT", 4421))
        self.client = os.getenv("ANIDB_CLIENT")
        self.client_ver = os.getenv("ANIDB_CLIENT_VER")
        self.username = os.getenv("ANIDB_USERNAME")
        self.password = os.getenv("ANIDB_PASSWORD")

        self.limiter = RateLimiter()
        self._cipher = None
        self.session = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(10)
        self.sock.bind(("0.0.0.0", self.local_port))

    def _pad(self, data: bytes) -> bytes:
        pad_len = 16 - (len(data) % 16)
        return data + bytes(pad_len)

    def _send(self, command: str) -> str:
        self.limiter.wait()
        data = command.encode()
        if self._cipher:
            data = self._cipher.encrypt(self._pad(data))
        self.sock.sendto(data, (self.host, self.port))
        raw, _ = self.sock.recvfrom(1400)
        if self._cipher:
            raw = raw.rstrip(b'\x00')
            if len(raw) % AES.block_size:
                if len(raw) >= 3 and raw[:3].isdigit():
                    return raw.decode()
                raise RuntimeError(
                    f"Encrypted AniDB response is not block-aligned: {len(raw)} bytes"
                )
            raw = self._cipher.decrypt(raw).rstrip(b'\x00')
        return raw.decode()

    def ping(self) -> bool:
        response = self._send("PING")
        return True if response.startswith("300") else False

    def auth(self) -> str:
            
        cmd = (f"AUTH user={self.username}&pass={self.password}&protover=3&client={self.client}&clientver={self.client_ver}&enc=UTF-8")

        response = self._send(cmd)
        code = response[:3]

        if code in ("200", "201"):
            self.session = response.split(" ")[1]
            if code == "201":
                print("Note a new version of this client is available")
            return self.session
        elif code == "500":
            raise Exception("LOGIN FAILED - wrong username or password")
        elif code =="503":
            raise Exception("CLIENT VERSION OUTDATED - update protover value")
        elif code =="504":
            raise Exception(f"CLIENT BANNED: {response}")
        elif code =="505":
            raise Exception("ILLEGAL INPUT OR ACCESS DENIED")
        elif code =="601":
            raise Exception("ANIDB OUT OF SERVICE - TRY AGAIN LATER")

        raise RuntimeError(f"Unexpected AUTH response: {response}")

    def logout(self):
        if self.session:
            response = self._send(f"LOGOUT s={self.session}")
            self.session = None
            return True if response.startswith("203") else False
        return False

    def command(self, cmd: str) -> str:
        if not self.session:
            raise Exception("NOT LOGGED IN")
        sep = "&" if " " in cmd else " "
        return self._send(f"{cmd}{sep}s={self.session}")

    def encrypt(self) -> None:
        if not self.api_key:
            raise Exception("ANIDB_API_KEY is not set in .env file")

        response = self._send(f"ENCRYPT user={self.username}&type=1")
        code = response[:3]

        if code == "209":
            salt = response.split(" ")[1]
            key = hashlib.md5((self.api_key + salt).encode()).digest()
            self._cipher = AES.new(key, AES.MODE_ECB)
        elif code == "309":
            raise Exception("API PASSWORD NOT DEFINED")
        elif code == "509":
            raise Exception("NO SUCH ENCRYPTION TYPE")
        elif code == "394":
            raise Exception("NO SUCH USER")
        else:
            raise RuntimeError(f"Unexpected ENCRYPT response: {response}")

    def close(self):
        if self.sock.fileno() == -1:
            return

        try:
            self.logout()
        finally:
            self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()