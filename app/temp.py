import time
from enum import Enum, auto

# my_time = time.time()
# print(my_time)


# class Role(Enum):

#     MASTER = "master"
#     SLAVE = "slave"

# class InfoHandler:
#     role: Role
#     host: str
#     port: int
#     def __init__(self, role: Role):
#         self.role = role
#     def respond(self):
#         response = f"role:{self.role.value}"
#         response_len = len(response)
#         return f"${response_len}\r\n{response}\r\n"
    
# info = InfoHandler(Role.MASTER)
# print(info.role.value)


            #    if command == "ping":
            #         response = getresponce("PONG")
            #     elif command == "echo":
            #         response = getresponce(vector2[1] if len(vector2)>1 else "")
            #     elif command == "set": 
            #         myDict = {vector2[1]: vector2[2]}
            #         if len(vector2) > 4:
            #             myDict["expiry"] = vector2[-1]
            #             myDict["start"] = time.time_ns()
            #             flag = True
            #         response = getresponce("OK")
            #     elif command == "get":
            #         response = getresponce(myDict[vector2[1]])
            #         if(flag):
            #             if (time.time_ns() - myDict["start"])* 10**-6 >= int(myDict["expiry"]):
            #                 response = getresponce("")
            #     elif command == "info":
            #          print("It's triggred")
            #          if info.role == Role.MASTER:
            #              response = f"$11\r\nrole:{info.role.value}\r\n"
            #          else:
            #              response = f"$10\r\nrole:{info.role.value}\r\n"
            #          print("sending re")
vector = "*1\r\n$4\r\nping\r\n".split("\r\n")
print(vector)


    
    # if command == "ping":
    #     f_trigger()
    # elif command == "echo":
    #     response = getresponce(vector2[1] if len(vector2)>1 else "")
    # elif command == "set": 
    #     myDict = {vector2[1]: vector2[2]}
    #     if len(vector2) > 4:
    #         myDict["expiry"] = vector2[-1]
    #         myDict["start"] = time.time_ns()
    #         flag = True
    #     response = getresponce("OK")
    # elif command == "get":
    #     response = getresponce(myDict[vector2[1]])
    #     if(flag):
    #         if (time.time_ns() - myDict["start"])* 10**-6 >= int(myDict["expiry"]):
    #             response = getresponce("")
    # elif command == "info":
    #     print("this is the info section ")
    #     response = f"role:{info.role.value}\r\n"
    #     response += f"master_replid:{info.master_replid}\r\n"
    #     response += f"master_repl_offset:{info.master_repl_offset}\r\n"
    #     response = getresponce(response)
    # elif command == "replconf" or vector2[1] == "listening-port":
    #     response = getresponce("OK")
    # elif command == "replconf" or vector2[1] == "capa":
    #     response = getresponce("OK")
    # elif command == "psync":
    #     response = f"+FULLRESYNC {info.master_replid} {0}\r\n"
    #     # response = getresponce(response)
    # return response.encode()
