import socket
import subprocess
import gzip
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
def main():
  """ Staring a TCP socket. """
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  """ Connecting to the server. """
  client.connect(ADDR)

  """ Receive filepath, .blend file length, and frame number to render. """
  metadata = client.recv(SIZE).decode(FORMAT)
  client.send("metadata received".encode(FORMAT))
  metadata = metadata.split("\n")
  print(metadata)

  print(f"[RECV] Receiving .blend file.")
  proj_name = metadata[0].split("/")[0]
  if proj_name not in os.listdir("./"):
    os.makedirs("./" + proj_name)

  file = open(metadata[0], "wb")
  blend_file_len = int(metadata[1])
  data = bytearray(blend_file_len)
  pos = 0
  while pos < blend_file_len:
      cr = client.recv_into(memoryview(data)[pos:])
      if cr == 0:
          raise EOFError
      pos += cr

  client.send("file received".encode(FORMAT))
  file.write(data)

  """ Closing the file. """
  file.close()

  """ Render assigned frames~ """
  subprocess.run(["blender", "-b", metadata[0], '-o', proj_name + "/outputs/", "-E", "CYCLES", "-s", metadata[2], "-e", metadata[3], "-a"])

  """ TODO: Send outputs to server. """

if __name__ == "__main__":
  main()