import time
from enum import Enum, auto

my_time = time.time()
print(my_time)


class Role(Enum):

    MASTER = "master"
    SLAVE = "slave"

class InfoHandler:
    role: Role
    host: str
    port: int
    def __init__(self, role: Role):
        self.role = role
    def respond(self):
        response = f"role:{self.role.value}"
        response_len = len(response)
        return f"${response_len}\r\n{response}\r\n"
    
info = InfoHandler(Role.MASTER)
print(info.role.value)