Python File Server
====================================================

These simple python script make up a simple file server for saving and retrieving your files

Introduction
------------

This project uses a TCP connection to facilitate the delivery of arbitarly large files.
Start server.py on any system with an opened port.
```python
server.py -p <port> -h <OPTIONAL: host>
```

On your client, start your client on any system around the world and connect to the host and port number your server is initialized on.
```python
client.py -p <port> -h <OPTIONAL: host>
```

Pre-requisites
--------------
A server with an open port.



Commands
--------

- ls : print on the client window a listing of the contents of the current directory
on the server machine.
- get <remote-file-name>: retrieve the remote-file on the server and store it on the
client machine. It is given the same name it has on the server machine.
- put <file-name-name>: put and store the file from the client machine to the server
machine. On the server, it is given the same name it has on the client machine.
- cd <directory-name>: change the on the server (“cd ..” must work)
- mkdir <directory-name>: create a new sub-directory named directoryname