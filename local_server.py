import asyncio

HOST = "127.0.0.1"
PORT = 8080

async def client():
    print(f"[CLIENT] Conectando a {HOST}:{PORT}...")

    reader, writer = await asyncio.open_connection(HOST, PORT)
    print("[CLIENT] Conectado!")

    while True:
        msg = input("Mensagem para enviar: ")

        writer.write((msg + "\n").encode())
        await writer.drain()

        # resposta = await reader.readline()
        # print("[CLIENT] Resposta:", resposta.decode().strip())


asyncio.run(client())
