import asyncio

class MenuService:

    def __init__(self, notification_bus, tor_service, repository):
        """Initialize MenuService with required dependencies."""

        self.notification_bus = notification_bus
        self.tor_service = tor_service
        self.repository = repository

    def __repr__(self):
        return (
            f"MenuService(notification_bus={self.notification_bus!r}, "
            f"tor_service={self.tor_service!r}, repository={self.repository!r})"
        )
        
    
    async def start_tor_service(self,tor_start_timeout):
        await asyncio.to_thread(self.tor_service.start_tor,tor_start_timeout)

    async def start_tables(self):
        await self.repository.create_tables()

    async def get_servers(self):
        return await self.repository.get_all_servers()
    
    async def remove_server(self, server_name):
       
       await asyncio.to_thread(self.tor_service.remove_onion_service,server_name)
       await self.repository.remove_server(server_name)
    
    async def remove_discovered_server(self,hostname):
        await self.repository.remove_discovered_server(hostname)
        
    async def create_new_onion_server(self,server_name):
        await asyncio.to_thread(self.tor_service.create_new_onion_server,server_name)
    
    async def start_proxy(self):
        await asyncio.to_thread(self.tor_service.start_tor,10)

    async def end_tor(self):
        await asyncio.to_thread(self.tor_service.end_tor)