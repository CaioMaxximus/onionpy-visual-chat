import json
class ServerMessage():

    def __init__(self, author, message , from_server):

        self.author = author
        self.message = message
        self.from_server = from_server
    
    def convert_to_stream(self, end = b"\0"):

        dic_data = self.__dict__
        json_data = json.dumps(dic_data).encode("utf-8")
        return json_data + end
    
    @classmethod
    def from_stream(cls, data):

        clean_data = data[:-1]
        json_data = clean_data.decode("utf-8")
        dic_data = json.loads(json_data)

        return cls(**dic_data)
        

