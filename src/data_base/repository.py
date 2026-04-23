from data_base import db_service_manager as db
from models import DiscoveredServer, OnionServer

async def get_all_discovered_servers():
    servers = await db.list_all_discovered_servers()
    #  verficar se pode retornar none
    exit_ =  []
    for s in servers:
        exit_.append(DiscoveredServer(name =s[0] , hostname=s[1],port= s[2], password= ""))
    return exit_

async def get_all_servers():
    servers = await db.list_all_servers()
    exit_ =  []

    for s in servers:
        exit_.append(OnionServer(name=s[0], hostname=s[1],local_server_port=s[2],
                                 onion_port=s[3],password= ""))
    return exit_