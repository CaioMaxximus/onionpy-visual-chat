import asyncio
import ssl
from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType


async def connect_via_proxy(
    proxy_host,
    proxy_port,
    proxy_type,
    dest_host,
    dest_port
):
    print(f"[+] Conectando ao proxy {proxy_host}:{proxy_port} ({proxy_type.name})")

    proxy = Proxy(
        proxy_type=proxy_type,
        host=proxy_host,
        port=proxy_port,
        rdns= True
    )

    try:
        # 1. Conectar ao proxy e receber socket
        sock = await proxy.connect(
            dest_host=dest_host,
            dest_port=dest_port,
        )
        print("[✔] Socket proxy estabelecido")

        # 2. Conectar via asyncio.open_connection usando o socket
        reader, writer = await asyncio.open_connection(
            host=None,
            port=None,
            sock=sock,
            ssl=None,   # deixe sem SSL para testar
        )
        # reader, writer = await asyncio.open_connection(host= proxy_host ,
        #                                                port = proxy_port)
        print("[✔] open_connection funcionando")

        # 3. Fazer a requisição HTTP para teste
        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {dest_host}\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()

        writer.write(request)
        await writer.drain()

        print("[+] Lendo resposta...")
        data = await reader.read(-1)

        print("\n=== RESPOSTA ===\n")
        print(data.decode(errors="ignore"))

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print("[ERRO]", e)


async def main():
    await connect_via_proxy(
        proxy_host="127.0.0.1",
        proxy_port=9050,
        proxy_type=ProxyType.SOCKS5,   # pode trocar para SOCKS5 se for o caso
        dest_host="e3qptke7t4rqsqfp7vxlstw6dj7gx3npqvql5ygjnq5rhvb5iokdopyd.onion",
        dest_port=80,
    )

asyncio.run(main())
