import socket, sys, getopt, subprocess, json, os

HOST = 'localhost'
PORT = 8098
 
#   To use
#       python server.py -p 8080
#       python server.py -p 8080 -h 123.123.123.123
 
#define process type
iotype = subprocess.PIPE

COMMANDCODE = ["ls", "mkdir", "put", "get", "cd","exit","shutdown"]
SYSFOLDER = "FileSystemFolder/"


def main(argv):
    global HOST # Access those variables defined at the top
    global PORT
    
    # Extract the arguments from the program
    try:
        opts, args = getopt.getopt(argv,"p:h:",["pport=","hhost="])
    except getopt.GetoptError:
        print 'USAGE     server.py -p <port> -h <OPTIONAL: host>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--pport"):
            PORT = arg
        elif opt in ("-h", "--hhost"):
            HOST = arg
        else:
            print 'USAGE     server.py -p <port> -h <OPTIONAL: host>'
            sys.exit(2)
    print "Server Initializing on port %s (%s)..." % (PORT,HOST)
    StartServer(PORT, HOST)
 
#   res :: Dict
#   command - command to implement
#   error   - error reason
#   content - the stuff
#   code    - 'OK' or 'Error:'
 
def StartServer(PORT,HOST):
    global COMMANDCODE
    global SYSFOLDER
    print "Opening connections..."
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not os.path.exists(SYSFOLDER):
        os.makedirs(SYSFOLDER)
    # Bind the socket to the port
    server_address = (HOST,int(PORT))
    #print  'starting up on %s port %s' % server_address
    sock.bind(server_address)
    isRunning = True
    # Listen for incoming connections
    sock.listen(5) # Accept 5 connections
    currentPath = []
    while isRunning:
        # This while block signifies a connection to a client
        print 'waiting for a connection'
        connection, client_address = sock.accept()
        isServingClient = True
        print "waiting for recv"

        try:
            print 'connection from', client_address
            while isServingClient:
                sendAck = True
                # This while signifies a transaction with a client (command)
                data = connection.recv(1024)

                # Here we deserialize the data from the packet 
                packet = json.loads(data)

                # We can use out deserialized dict to get items 
                command = packet["command"]
                print '\nClient>> %s' % command
                if command != '':
                    msg = command.split()
                    cmd = msg[0].lower()
                    packet = {}
                    if msg[0] not in COMMANDCODE:
                        packet["error"] = "Error:: Invalid Argument"
                        packet["code"] = "ERROR"

                    elif len(msg) > 2:
                        packet["error"] = "Error:: Two Many Argument"
                        packet["code"] = "ERROR"
                    elif cmd == "ls":       # Handle LS command
                        if (len(msg) == 1) :

                            # Return files in the directory's folder
                            files = os.listdir(SYSFOLDER+GetCurrentWorkingFolder(currentPath))
                            ls = "";
                            path = SYSFOLDER+GetCurrentWorkingFolder(currentPath) + "/"
                            if len(files) == 0:
                                print "There isn't anything on the server, upload something now!"
                            for x in files:
                                if os.path.isfile(path+x):
                                    ls += "\n File: " + x
                                if os.path.isdir(path+x):
                                    ls += "\n Folder: " + x
                            packet["code"] = "OK"
                            packet["content"] = ls
                        else:
                            packet["error"] = "Error: Too Many Argument"
                            packet["code"] = "ERROR"
                    elif cmd == "mkdir":    # Handle MKDIR command
                        if len(msg) == 1:
                            packet["error"] = "Error: No Argument"
                            packet["code"] = "ERROR"
                        else:
                            directory = msg[1]
                            path = SYSFOLDER + GetCurrentWorkingFolder(currentPath)+ '/' + directory
                            if not os.path.exists(path):
                                os.makedirs(path)
                                packet["code"] = "OK"
                                packet["content"] = "Directory " + directory +" Created Succefully"
                            else:
                                packet["error"] = "Error: Directory exists"
                    elif cmd == "cd":       #Handle cd and back command
                        if len(msg) == 1:
                            packet["error"] = "Error: No Argument exists"
                            packet["code"] = "ERROR"
                        else:
                            directory = msg[1]
                            filePath = SYSFOLDER+GetCurrentWorkingFolder(currentPath)

                            # We use an array keep track of the current directory we are in
                            if directory == "..": 
                                print "Command: " + cmd + "\nArgument: Back Directory" 
                                packet["code"] = "OK"
                                if len(currentPath) != 0:
                                    currentPath.pop()
                                packet["content"] = SYSFOLDER+GetCurrentWorkingFolder(currentPath)
                            else:
                                if(os.path.exists(SYSFOLDER+GetCurrentWorkingFolder(currentPath)+"/"+directory)):
                                    currentPath.append(directory)
                                    print "Command: " + cmd + "\nArgument: " + directory
                                    packet["code"] = "OK"
                                    packet["content"] = SYSFOLDER+GetCurrentWorkingFolder(currentPath)
                                else:
                                    packet["code"] = "ERROR"
                                    packet["error"] = "No folder exists of that name"
                    elif cmd == "get":      #Handle get command
                        if len(msg) == 1:
                            packet["error"] = "Error: No Argument exists"
                            packet["code"] = "ERROR"
                        else:

                            # Check if the file exists 
                            filename = msg[1]
                            filePath = SYSFOLDER+GetCurrentWorkingFolder(currentPath)+"/"+filename
                            if (os.path.isfile(filePath)):
                                packet["content"] = "Server ready to send file"
                                packet["code"] = "OK" 
                                data = json.dumps(packet)
                                connection.send(data)
                                connection.close()

                                # Break up this transaction into peices
                                connection, client_address = sock.accept()
                                f = open(filePath, 'rb')
                                print "Sending file..."

                                # Send the file when there is no error
                                data = f.read(1024)
                                while data:
                                  connection.send(data)
                                  data = f.read(1024)
                                print "\nDone Sending"

                                # Send shutdown as stream has finished
                                connection.shutdown(socket.SHUT_WR)
                                connection.close()
                                sendAck = False
                                isServingClient = False
                            else:
                                packet["error"] = "Error: File Not exists"
                                packet["code"] = "ERROR"

                    elif cmd == "put":      #Handle put command
                        if len(msg) == 1:
                            packet["error"] = "Error: No Argument exists"
                            packet["code"] = "ERROR"

                        else:
                            filename = msg[1]

                            # renaming the file
                            filePath = SYSFOLDER+GetCurrentWorkingFolder(currentPath)+"/"+filename
                            if os.path.exists(filePath):
                                s = filename.split('.')
                                ext = s[len(s)-1]
                                s.pop() # remove ext
                                i = 1

                                # Trying for ever till we can make a valid name
                                filePath = "%s%s/%s-%d.%s" %(SYSFOLDER,GetCurrentWorkingFolder(currentPath),''.join(s),i,ext)
                                while(os.path.exists(filePath)):
                                    filePath = "%s%s/%s-%d.%s" %(SYSFOLDER,GetCurrentWorkingFolder(currentPath),''.join(s),i,ext)
                                    i += 1
                            packet["content"] = "Server is ready to receive file"
                            packet["code"] = "OK"
                            data = json.dumps(packet)
                            connection.send(data)
                            connection.close()

                            # Second part of this iprocess is to receive the file
                            connection, client_address = sock.accept()
                            print "accepted the file transfer"
                            
                            f = open(filePath,"wb")
                            l = connection.recv(1024)
                            print "transfer started"
                            while l:
                                f.write(l)
                                l = connection.recv(1024)
                            f.close()
                            print "transfer complete"
                            connection.close()
                            sendAck = False
                            isServingClient = False

                    elif cmd == "exit":     #Hanlde exit command
                        packet["content"] = "Bye bye"
                        packet["code"] = "OK"
                        data = json.dumps(packet)
                        connection.send(data)
                        isServingClient = False
                        
                    elif cmd == "shutdown": #Handle shutdown command
                        isServingClient = False
                        isRunning = False
                       
                    if sendAck:
                        # Only skip the ACK on file transfers
                        data = json.dumps(packet)
                        connection.send(data)
                        connection.close()
                        isServingClient = False 
        except:
            print "Client disconnected"   
            connection.close()
        finally:
            # Clean up the connection
            connection.close()
 
def GetCurrentWorkingFolder(path):
    return '/'.join(path)

def GetFilesInDirectory(path):
    # Concats files in the path
    files = os.listdir(PATH)
    for fl in files:
        i = int(files.index(fl))+1
        print str(i) +" "+ fl
    return files
 
 
main(sys.argv[1:])
