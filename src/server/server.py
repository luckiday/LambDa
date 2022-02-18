import socket
import os
import blender_render_info

IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def main():
  print("[STARTING] Server is starting.")

  """ Starting a TCP socket """
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  """ Bind the IP and PORT to the server """
  server.bind(ADDR)

  """ Server is listening, i.e., server is now waiting for the client to connect """
  server.listen()

  print("[LISTENING] Server is listening.")

  available_clients = []

  while True:
    """ Server has accepted the connection from the client """
    conn, addr = server.accept()
    available_clients.append(conn)

    print(f"[NEW CONNECTION] {addr} connected.")

    """ Check if a new project has arrived. """
    root='./'
    curr_projs_set = { item for item in os.listdir(root) if item != '__pycache__' and os.path.isdir(os.path.join(root, item)) }
    if len(curr_projs_set):
      for new_proj in curr_projs_set:
        for filename in os.listdir(new_proj): # should have just one .blend file in here
          if filename.endswith(".blend"):
              filepath = new_proj + "/" + filename
              file_len = str(os.path.getsize(filepath))

              """ Opening and reading the .blend file data. """
              file = open(filepath, "rb")
              data = file.read()

              """ Naively spread frames amongst available clients. 1 client can't handle more than 1 job. """
              # [(frame_start, frame_end, _)] = blender_render_info.read_blend_rend_chunk(filepath)
              (frame_start, frame_end) = (1, 1)
              num_available_clients = len(available_clients)
              frames_per_client = (frame_end - frame_start + 1) // num_available_clients
              # last client will get any leftovers
              # not handling the case where num_available_clients > num_frames_to_render
              # because don't ever think we'll reach that point with this demo

              for ind, client in enumerate(available_clients):
                start_frame = frame_start + ind * frames_per_client
                end_frame = start_frame + frames_per_client - 1
                if ind == len(available_clients) - 1: # last client
                  end_frame = frame_end

                print("SENT: " + (filepath + "\n" + file_len + "\n" + str(start_frame) + "\n" + str(end_frame)))
                client.send((filepath + "\n" + file_len + "\n" + str(start_frame) + "\n" + str(end_frame)).encode(FORMAT))
                client.recv(SIZE) # confirm client received metadata
                client.send(data) # send whole file
                client.recv(SIZE) # confirm client receiived .blend file
                print("sent file data")

              """ Closing the file. """
              file.close()

if __name__ == "__main__":
  main()
