import socket
import subprocess
import os

IP = socket.gethostbyname(socket.gethostname()) # to be replaced with seerver IP
PORT = 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
def main():
  while True:
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """ Connecting to the server. """
    print("CONNECTED WITH SERVER")
    client.connect(ADDR)
    client.send("worker".encode(FORMAT))
    client.recv(SIZE) # role ack
    client.send("available".encode(FORMAT))

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
    print("RECEIVED ALL INFO")
    client.send("file received".encode(FORMAT))
    client.close()
    file.write(data)

    """ Closing the file. """
    file.close()

    """ Render assigned frames~ """
    subprocess.run(["blender", "-b", metadata[0], '-o', proj_name + "/outputs/", "-E", "CYCLES", "-s", metadata[2], "-e", metadata[3], "-a"])

    # """ Send outputs to server. """
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """ Connecting to the server. """
    print("CONNECTED WITH SERVER")
    client.connect(ADDR)
    client.send("worker".encode(FORMAT))
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


if __name__ == "__main__":
  main()