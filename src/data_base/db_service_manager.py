import  aiosqlite

DYNAMIC_PORT_MIN = 49152
DYNAMIC_PORT_MAX = 65535

# servers = {
#     "server_name",
#     "onion_hostname",
#     "local_server_port",
#     "onion_port"
# }

async def create_tables(db_path: str = "my.db"):
    """Create the servers table if it doesn't exist."""
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            server_name TEXT PRIMARY KEY,
            onion_hostname TEXT PRIMARY KEY,
            local_server_port INTEGER NOT NULL,
            onion_port INTEGER NOT NULL
        )
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS discovered_servers (
            server_name TEXT NOT NULL,
            onion_hostname TEXT PRIMARY KEY,
            port INTEGER NOT NULL
        )
        """)

        await conn.commit()


async def save_new_server(server_name: str, local_port , onion_hostname, onion_port: int, db_path: str = "my.db") -> None:
    """
    Insert or replace a server record.
    server_name is the primary key; this will upsert the entry.
    """
    # print("chamei para ")
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO servers (server_name, onion_hostname, local_server_port ,onion_port ) VALUES (?, ?, ?,?)",
            (server_name, onion_hostname, local_port ,onion_port)
        )
        await conn.commit()


async def remove_server(server_name: str, db_path : str= "my.db"):
    """
    Remove a server record from the database
    """

    async with  aiosqlite.connect(db_path) as conn:
        await conn.execute(
            "DELETE FROM servers WHERE server_name = ?",
            (server_name,)
        )
        await conn.commit()


async def save_discovered_server_securely(server_name : str, onion_hostname : str ,port : int, db_path : str = "my.db"):
    """
    Stores a new discovered server
    """

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(
            "INSERT INTO discovered_servers (server_name, onion_hostname, port) VALUES (?,?,?) ON CONFLICT DO NOTHING",
            (server_name, onion_hostname ,port)
        )
        await conn.commit()


async def list_all_discovered_servers(db_path : str = "my.db"):

    async with aiosqlite.connect(db_path) as conn:
        async with await conn.execute(
            "SELECT * FROM discovered_servers"
        ) as cursor:
            res = await cursor.fetchall()
            return res


async def get_server_by_name(server_name: str, db_path: str = "my.db"):
    """
    Retrieve a server by server_name.
    Returns a dict with keys: server_name, onion_hostname, server_port or None if not found.
    """
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT server_name, onion_hostname, local_server_port ,  onion_port FROM servers WHERE server_name = ?",
            (server_name,),
        ) as cursor:
            res = await cursor.fetchone()
            if res is None:
                raise FileNotFoundError
            return {"server_name": res["server_name"], "onion_hostname": res["onion_hostname"],
                     "local_server_port": res["local_server_port"], "onion_port" : res["onion_port"]}


async def list_all_ports(db_path: str = "my.db") -> list:
    """Return a list of all server_port values stored in the database."""

    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute(
            """SELECT local_server_port FROM servers
            union  all
        select onion_port FROM servers """) as cursor:
            rows = await cursor.fetchall()

            return [int(r[0]) for r in rows if r[0] is not None]
        

### Keeping for testing
if __name__ == "__main__":
    async def op():
        await create_tables()
        await save_discovered_server_securely("descdsadoberto" ,"dasdsadasadsad.onion" , 123)
        res = await list_all_discovered_servers()
        print(res)
        # await save_new_server("teste1" ,122 ,  "doasdosadik.onion", 2121)
        # print(await get_server_by_name("teste1"))
        # print(await list_all_ports())
        
    import asyncio
    asyncio.run(op())