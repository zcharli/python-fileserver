import socket,getopt,sys,subprocess, json, os

#   To use
#       
#       python client.py -p 8080
#       python client.py -p 8080 -h 123.123.123.123
#   If no host was given, we default to localhost
 

#define the socket size
BUFSIZE = 1024

#define the Host and PORT number (default)
HOST = 'localhost' 
PORT = 8080

COMMANDCODE = ["ls", "mkdir", "put", "get", "cd","exit","shutdown"]

def main(argv):
  global HOST # Access those variables defined at the top
  global PORT
  print "Client initializing"
  try:
      opts, args = getopt.getopt(argv,"p:h:",["pport=","hhost="])
  except getopt.GetoptError:
      print 'USAGE     client.py -p <port> -h <OPTIONAL: host>'
      sys.exit(2)
  for opt, arg in opts:
      if opt in ("-p", "--pport"):
          PORT = arg
      elif opt in ("-h", "--hhost"):
          HOST = arg
      else:
          print 'USAGE     client.py -p <port> -h <OPTIONAL: host>'
          sys.exit(2)
  StartClient(HOST,PORT)


def StartClient(HOST,PORT):
  isRunning = True
# Create a TCP/IP socket
 
# Connect the socket to the port where the server is listening
  server_address = (HOST,int(PORT))
  print  'connecting to %s port on %s' % server_address

  try:
    while isRunning:


      # Request for connection
     # sock.connect(server_address)
      # Packet dictionary
      packet = {} 
      cmd = raw_input('Client >> ')
      ret = ValidateCommand(cmd) 
      while ret != "OK":
        print ret
        cmd = raw_input('Client >> ')
        ret = ValidateCommand(cmd)

      packet["command"] = cmd
      args = cmd.split()

      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect(server_address)
      # Serialize the data
      data = json.dumps(packet)
      # Send command
      sock.send(data)
      if cmd == "exit" or cmd == "shutdown":
        isRunning = False
        break;
      # Receive response
      data = RecvAllString(sock)
      # Deserialize the data 
      packet = json.loads(data)

      HandleResponse(packet)


      if len(args) == 2:
        if args[0].lower() == "get":

          # Prepare your a*****e for a file stream
          if packet['code'].upper() == 'OK':
            sock.close()
            
            # Close off current connection due to verification success
            filepath = args[1]

            # Connected again, this time try to get the the stream going
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(server_address)
            if os.path.exists(filepath):
              s = filepath.split('.')
              ext = s[len(s)-1]
              s.pop() #r emove ext
              i = 1

              filepath = "%s-%d.%s" %(''.join(s),i,ext)
              while(os.path.exists(filepath)):
                  filepath = "%s-%d.%s" %(''.join(s),i,ext)
                  i += 1
            f = open(filepath, 'wb')
            l = sock.recv(1024)
            b = len(l)
            print "Receiving file..."

            # Updates numbers on the go
            while l:
              status = "\rDownloading %d bytes" % b
              sys.stdout.write(status)
              sys.stdout.flush()
              f.write(l)
              l = sock.recv(1024)
              b += len(l)
            print ""
            f.close()
        elif args[0].lower() == "put":

          # Prepare to pee into the server as a file stream
          if packet['code'].upper() == 'OK':
            sock.close()
            filepath = args[1]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(server_address)
            f = open(filepath, 'rb')
            print "Sending file..."
            b = 0
            data = f.read(1024)
            b += len(data)

            # Update received amounts on the go
            while data:
              status = "\rUploading %d bytes" % b
              sys.stdout.write(status)
              sys.stdout.flush()
              sock.send(data)
              data = f.read(1024)
              b += len(data)
            print "\nDone Sending"
            sock.shutdown(socket.SHUT_WR)
            f.close()
      
      sock.close()

  finally:
    print  'Shutting down client, Bye bye'
    #sock.close()

def RecvAllString(sock):
  data = []
  while True:
    stream = sock.recv(BUFSIZE)
    if not stream: break
    data.append(stream)
  return ''.join(data)

def HandleResponse(res):
  code = res["code"]
  if code.upper() == "OK":
    print "Server >> ", res["content"]
  else :
    print "Server >> ERROR: ", res['error']

def ValidateCommand(command):
  # Client side validation

  if not command or command == "":
    return "Error: No Command"
  msg = command.split()
  cmd = msg[0].lower()
  if msg[0] not in COMMANDCODE:
    return "Error: Invalid Command"
  elif len(msg) > 2:
    return "Error: Too Many Argument"
  elif cmd == "ls":
      # Handle LS command
    if (len(msg) != 1) :
      return "Error: Not enough argument (2 required)"
  elif cmd == "mkdir":
    if (len(msg) != 2) :
      return "Error: Too Many Argument"
    return "OK"
  elif cmd == "cd":
    if len(msg) == 1:
      return "Error: No Argument exist"
  elif cmd == "get":
    filename = msg[1].lower()
    if os.path.exists(filename):
        return "OK"
  elif cmd == "put":
    if len(msg) == 1:
      return "Error: No Argument exist"
    else:
      filename = msg[1].lower()
      if not os.path.exists(filename):
        return "Error: File does not exist"
  elif cmd == "exit":
    return "OK"
  elif cmd == "shutdown":
    return "OK"
  else:
    return "No such command"
  return "OK"

main(sys.argv[1:])


