import socket

HOST = "127.0.0.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}")

    conn, addr = s.accept()
    with conn:
        print("Connected:", addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("Received:", data)
            conn.sendall(b"OK\n")
