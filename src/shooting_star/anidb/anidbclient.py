import os
from dotenv import load_dotenv
import socket

from .ratelimiter import RateLimiter

load_dotenv()

class AniDBClient():
    def __init__(self) -> None:
        self.host = os.getenv("ANIDB_HOST", "api.anidb.net")
        self.port = int(os.getenv("ANIDB_PORT", 9000))
        self.local_port = int(os.getenv("ANIDB_LOCAL_PORT", 4421))
        self.client = os.getenv("ANIDB_CLIENT")
        self.client_ver = os.getenv("ANIDB_CLIENT_VER")
        self.username = os.getenv("ANIDB_USERNAME")
        self.password = os.getenv("ANIDB_PASSWORD")

        self.limiter = RateLimiter()

        self.session = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(10)
        self.sock.bind(("0.0.0.0", self.local_port))

    def _send(self, command: str) -> str:
        self.limiter.wait()
        self.sock.sendto(command.encode(), (self.host, self.port))
        data, _ = self.sock.recvfrom(1400)
        return data.decode()

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

    def close(self):
        self.logout()
        self.sock.close()