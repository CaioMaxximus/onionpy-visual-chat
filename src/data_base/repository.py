from data_base import db_service_manager as db
from models import DiscoveredServer, OnionServer



async def save_new_server(server_name, local_port , 
                            onion_hostname, onion_port):
    await db.save_new_server(server_name, local_port , 
                            onion_hostname, onion_port)

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
async def get_server_by_name(name):
    res =  await db.get_server_by_name(name)
    return OnionServer(res["server_name"] ,res["onion_hostname"],
                       res["local_server_port"] ,res["onion_port"] )

async def remove_server(server_name):
    try:
        await db.remove_server(server_name)
    except:
        raise ValueError(f"Error trying to remove server {server_name}")
    
async def remove_discovered_server(hostname):
    try:
        await db.remove_discovered_server(hostname)
    except:
        raise ValueError(f"Error trying to remove discovered server {hostname}")
    
async def create_tables():
    try:
        await db.create_tables()
    except:
        raise ValueError(f"Error trying to remove discovered server")
    
async def list_all_ports():
    return await db.list_all_ports()