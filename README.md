# OnionPy Visual Chat

<p align="center">
  <img src="src/assets/logo_onio_py.png" alt="Project Logo" width="200">
</p>

A graphical application for hosting and connecting to onion-based chat stateless servers P2P, 
enabling the creation of multiple independent Tor hidden services with minimal setup.
Built with CustomTkinter, asyncio, and the Tor control library Stem.

## Status

  - Working on the build phase; only working on Debian for now.
  - Working in the server response for flood data
  - Cleaning architecture

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| **CustomTkinter GUI** | ✅ Done | Intuitive desktop interface |
| **Zero-Config Onion Setup** | ✅ Done | Create Tor hidden services without config files |
| **P2P Client/Server** | ✅ Done | Connect to any onion address, host multiple servers |
| **Password Protected Servers** | ✅ Done | Optional  access control |
| **Real-time Notifications** | ✅ Done | Connection status, errors, and alerts |
| **Message Broadcasting** | ✅ Done | Async message delivery to all connected clients |
| **Secure Credentials** | ✅ Done | Passwords hashed  |
| **Persistent Storage** | ✅ Done | SQLite database for servers and connections |
| **Async Non-Blocking UI** | ✅ Done | Smooth, responsive interface via asyncio |
| **Connection Management** | ✅ Done | View, manage, and delete saved servers |

---

## 🔒 Security Considerations

### Implemented
- ✅ **Password Hashing**: bcrypt with random salt (never plaintext in DB)
- ✅ **Handshake Protocol**: JSON-based with mandatory authentication fields
- ✅ **Tor Routing**: All traffic routed through Tor hidden services
- ✅ **Connection Validation**: Decorator-based state checks before operations
- ✅ **Input Validation**: Regex patterns for names and passwords

### Known Limitations
- ⚠️ **No Message Persistence**: Chat history not saved (by design for privacy)
- ⚠️ **No Reconnection Logic**: Dropped connections not retried (TODO)

---

## Requirements
- Python 3.8+
- Dependencies listed in `requirements.txt`

## Install
```bash
git clone https://github.com/CaioMaxximus/onion_py_chat.git
make install
```
## Execute

APP
```bash
make run
```
TESTS
```bash
./run_tests.sh
```
## Control flow architecture

![control flow](visual_schemes/control_flow.png)

## Tests

- TorServiceManager ![Status](https://img.shields.io/badge/status-done-brightgreen)
- client_connection ![Status](https://img.shields.io/badge/status-working-yellow)
- server_connection ![Status](https://img.shields.io/badge/status-done-brightgreen)
- client_controller ![Status](https://img.shields.io/badge/status-lacking-red)
- basic_async_controller ![Status](https://img.shields.io/badge/status-done-brightgreen)
- menu_controller ![Status](https://img.shields.io/badge/status-done-brightgreen)
- server_controller ![Status](https://img.shields.io/badge/status-lacking-red)

## Project Structure

## Contact
- Author: Caio Maxximus
- Email: puntmaxximus@gmail.com


