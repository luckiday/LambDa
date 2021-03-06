import argparse
import socket
import subprocess
import os
import shutil

parser = argparse.ArgumentParser(description="Join this device into the LambDa render farm running on a specified server.")
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
  while True:
    """ Starting a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """ Connecting to the server. """
    try:
      client.connect(ADDR)
    except:
      print("Connection failed. Check that the server IP address was correct.")
      quit()
    print("CONNECTED WITH SERVER")
    client.send("worker".encode(FORMAT))
    client.recv(SIZE) # role ack
    client.send("available".encode(FORMAT))

    """ Receive filepath, .blend file length, frame numbers to render, and render engine to use. """
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
    print("RECEIVED ALL INFO")
    client.send("file received".encode(FORMAT))
    client.close()
    file.write(data)

    """ Closing the file. """
    file.close()

    """ Check render engine choice. """
    if (metadata[4] not in ["CYCLES", "BLENDER_EEVEE", "BLENDER_WORKBENCH"]):
      print(f"Invalid render engine: {metadata[4]}, using CYCLES instead.")
      rend_engine = "CYCLES"
    else:
      rend_engine = metadata[4]

    """ Render assigned frames~ """
    print(' '.join(["blender", "-b", metadata[0], '-o', "//outputs/", "-E", rend_engine, "-s", metadata[2], "-e", metadata[3], "-a"]))
    subprocess.run(["blender", "-b", metadata[0], '-o', "//outputs/", "-E", rend_engine, "-s", metadata[2], "-e", metadata[3], "-a"])

    # """ Send outputs to server. """
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """ Connecting to the server. """
    client.connect(ADDR)
    print("CONNECTED WITH SERVER")
    client.send("worker-return".encode(FORMAT))
    client.recv(SIZE) # role ack
    client.send("done".encode(FORMAT))
    for filename in os.listdir(proj_name + "/outputs"):
      filepath = proj_name + "/outputs/" + filename
      file = open(filepath, "rb")
      data = file.read()
      file_len = str(os.path.getsize(filepath))
      client.send((filepath + "\n" + file_len).encode(FORMAT))
      client.recv(SIZE) # ack
      client.send(data)
      client.recv(SIZE) #ack
    client.send("DONE".encode(FORMAT))
    client.close()

    """ Delete project folder. """
    try:
      shutil.rmtree(proj_name)
    except OSError as e:
      print("Error: %s : %s" % (proj_name, e.strerror))

if __name__ == "__main__":
  main()