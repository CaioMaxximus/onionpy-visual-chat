import json
from .verify_hash import verify_hash


class HandShake():
      
    def __init__(self,id , password):
        self.id = id
        self.password = password
    
    


async def server_connection_handshake(message,password):
        
        clean = message[:-1]
        json_str = clean.decode("utf-8")
        dic_data = json.loads(json_str)
        ## Create new exceptions for this case
        if "password" not in dic_data or "id" not in dic_data:
            raise ValueError
        if password == "":
            return dic_data

        await verify_hash(password , dic_data["password"])
        return dic_data



def client_connection_handshake(identifyier , password,end = b'\0'):
        
        dic_data = HandShake(identifyier , password).__dict__
        json_bytes = json.dumps(dic_data).encode('utf-8')
        return (json_bytes + end)
