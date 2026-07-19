import json
from .verify_hash import verify_hash
from enum import Enum


class HandShake():
      
    def __init__(self,name , password):
        self.name = name
        self.password = password


class Response(Enum):
     
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


## SERVER SIDE HANDSHAKE

async def server_connection_handshake(message,password, local_users):
        
        clean = message[:-1]
        json_str = clean.decode("utf-8")
        dic_data = json.loads(json_str)
        ## Create new exceptions for this case
        if "password" not in dic_data or "name" not in dic_data:
            raise ValueError("Invalid HandShakeFormat")
        if dic_data["name"] in local_users:
            raise ValueError("Invalid Name")
        if password == "":
            return dic_data

        await verify_hash(password , dic_data["password"])
        return dic_data


def server_success_handshake_response(server_name, end = b"\0"):
     
    res = {"type" : Response.SUCCESS.value , "name" : server_name }
    res_bytes = json.dumps(res).encode("utf-8")
    return res_bytes + end
    

def server_failure_handshake_response( end = b"\0"):
     
    res = {"type" : Response.ERROR.value }
    res_bytes = json.dumps(res).encode("utf-8")
    return res_bytes + end


"CLIENT SIDE HANDSHAKE"

def client_connection_handshake(identifyier , password,end = b'\0'):
        
        dic_data = HandShake(identifyier , password).__dict__
        json_bytes = json.dumps(dic_data).encode('utf-8')
        return (json_bytes + end)

def handle_server_response(res):
     
    clean = res[:-1]
    json_str = clean.decode("utf-8")
    dic_data = json.loads(json_str)

    desired_keys = ["name"]
    ## Create new exceptions for this case
    if "type" not in dic_data:
        raise ValueError
    
    if dic_data["type"] == Response.ERROR.value:
            raise ValueError
    elif dic_data["type"] == Response.SUCCESS.value:
        if "name" not in dic_data:
            raise ValueError
        
        exit_dic = {}
        try:
            exit_dic = {k: dic_data[k] for k in desired_keys}
        except Exception:
            raise ValueError
        else:
            return exit_dic
                
    raise ValueError