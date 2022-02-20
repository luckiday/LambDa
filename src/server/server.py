import os
from os import listdir
from os.path import isfile, join

import blender_render_info
import socket
import threading
from threading import Thread
from socketserver import ThreadingMixIn

# Multithreaded Python server : TCP Server Socket Thread Pool


class ClientThread(Thread):

    def __init__(self, conn, ip, port, filepath, file_len, start_frame, end_frame, data):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.filepath = filepath
        self.file_len = file_len
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.data = data
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        conn.send((filepath + "\n" + file_len + "\n" + str(start_frame) + "\n" + str(end_frame)).encode(FORMAT))
        conn.recv(SIZE)  # confirm client received metadata
        conn.send(data)  # send whole file
        conn.recv(SIZE)  # confirm client receiived .blend file
        print("Sent File Data")


IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((IP, PORT))
threads = []

lock = threading.Lock()

while True:
    tcpServer.listen(4)
    print("Multithreaded Python server : Waiting for connections from TCP clients...")
    (conn, (ip, port)) = tcpServer.accept()
    print(f"[NEW CONNECTION] {ip} on port {port} connected.")
    newthread = (conn, ip, port)
    # newthread.start()
    lock.acquire()
    threads.append(newthread)
    lock.release()

    """ Check if a new project has arrived. """
    root = './'
    curr_projs_set = {item for item in os.listdir(root) if item != '__pycache__' and os.path.isdir(os.path.join(root, item))}
    if len(curr_projs_set):
        for new_proj in curr_projs_set:
            # should have just one .blend file in here
            for filename in os.listdir(new_proj):
                if filename.endswith(".blend"):
                    lock.acquire()
                    threads_tmp = threads
                    threads = []
                    lock.release()
                    filepath = new_proj + "/" + filename
                    file_len = str(os.path.getsize(filepath))

                    """ Opening and reading the .blend file data. """
                    file = open(filepath, "rb")
                    data = file.read()

                    """ Naively spread frames amongst available clients. 1 client can't handle more than 1 job. """
                    # [(frame_start, frame_end, _)] = blender_render_info.read_blend_rend_chunk(filepath)
                    (frame_start, frame_end) = (1, 1)
                    num_available_clients = len(threads_tmp)
                    frames_per_client = (frame_end - frame_start + 1) // num_available_clients
                    # last client will get any leftovers
                    # not handling the case where num_available_clients > num_frames_to_render
                    # because don't ever think we'll reach that point with this demo

                    for ind, client in enumerate(threads_tmp):
                        # start_frame = frame_start + ind * frames_per_client
                        # end_frame = start_frame + frames_per_client - 1
                        start_frame = 1
                        end_frame = 1
                        if ind == len(threads_tmp) - 1:  # last client
                            # end_frame = frame_end
                            end_frame = 1

                        print("SENT: " + (filepath + "\n" + file_len + "\n" + str(start_frame) + "\n" + str(end_frame)))
                        ClientThread(client[0], client[1], client[2], filepath, filename,start_frame, end_frame, data).start()

                    file.close()
