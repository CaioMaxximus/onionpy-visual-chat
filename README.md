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

## Features
- CustomTkinter interface providing easy and intuitive access to the application features.
 ![Status](https://img.shields.io/badge/status-done-brightgreen)
- No need to setup onion configuration files - just enter a valid server name and you're done.
 ![Status](https://img.shields.io/badge/status-done-brightgreen)
- Easy creation of onion clients using Tor as a proxy by simply typing the desired onion adress.
 ![Status](https://img.shields.io/badge/status-done-brightgreen)
- Informative view with popup notifications about connection status and erros.
 ![Status](https://img.shields.io/badge/status-done-brightgreen)
- Multithreaded asynchronous application providing a smooth and non-blocking interface.
-![Status](https://img.shields.io/badge/status-done-brightgreen)
- Option to manage the local servers and recent connections.
 ![Status](https://img.shields.io/badge/status-done-brightgreen)
- Create servers with special requirements such as passwords.
 ![Status](https://img.shields.io/badge/status-done-green)
 - Keep the local credentials proper encripited and safe. 
 ![Status](https://img.shields.io/badge/status--done-green)


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
- client_connection ![Status](https://img.shields.io/badge/status-lacking-red)
- server_connection ![Status](https://img.shields.io/badge/status-done-brightgreen)
- client_controller ![Status](https://img.shields.io/badge/status-lacking-red)
- basic_async_controller ![Status](https://img.shields.io/badge/status-done-brightgreen)
- menu_controller ![Status](https://img.shields.io/badge/status-done-brightgreen)
- server_controller ![Status](https://img.shields.io/badge/status-lacking-red)

## Project Structure

## Contact
- Author: Caio Maxximus
- Email: puntmaxximus@gmail.com


