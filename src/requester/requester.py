import socket
import os
import argparse

parser = argparse.ArgumentParser(description="Submit job request to server via TCP. Run until job finished. Outputs saved to your current directory.")
parser.add_argument("path", help="path to .blend file")
parser.add_argument("--serv-addr", help="IP address of server to connect to")
args = parser.parse_args()

IP = socket.gethostbyname(socket.gethostname()) # to be replaced with server IP
if (args.serv_addr):
  try:
    socket.inet_aton(args.serv_addr)
    IP = args.serv_addr
  except:
    print("The argument could not be parsed as an IP address.")
    quit()
PORT = 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
def main():
  """ Starting a TCP socket. """
  requester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  """ Connecting to the server. """
  try:
    requester.connect(ADDR)
  except:
    print("Connection failed. Check that the server IP address was correct.")
    quit()
  print("REQUESTER CONNECTED WITH SERVER")
  requester.send("requester".encode(FORMAT))
  requester.recv(SIZE) # role ack

  print("Sending project metadata, i.e. filename + .blend file length.")
  file_len = str(os.path.getsize(args.path))
  metadata = args.path.split("/")[-1] + "\n" + str(file_len)
  print("-------\n" + metadata + "\n-------")
  requester.send(metadata.encode(FORMAT))
  requester.recv(SIZE) # ack

  print("Sending .blend file.")
  file = open(args.path, "rb")
  data = file.read()
  requester.send(data)
  requester.recv(SIZE) # ack

  print("Waiting for outputs")
  while True:
    metadata = requester.recv(SIZE).decode(FORMAT).split("\n")
    if (metadata[0] == "CANCEL"):
      requester.close()
      print("Request canceled by server.")
      quit()
    if len(metadata) == 1:
        break
    requester.send("ack".encode(FORMAT))

    try:
        file = open(metadata[0], "wb")
    except FileNotFoundError:
        os.makedirs(metadata[0].split("/")[0] + "/outputs")
        file = open(metadata[0], "wb")
    output_file_len = int(metadata[1])
    data = bytearray(output_file_len)
    pos = 0
    while pos < output_file_len:
        cr = requester.recv_into(memoryview(data)[pos:])
        if cr == 0:
            raise EOFError
        pos += cr
    file.write(data)
    print("RECEIVED OUTPUT " + metadata[0])
    requester.send("file received".encode(FORMAT))

  requester.close()

if __name__ == "__main__":
  main()