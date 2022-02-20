import os

import blender_render_info
import socket
import threading
from threading import Thread
import time

# Multithreaded Python server : TCP Server Socket Thread Pool
threads = []
lock = threading.Lock()

class ConnectionThread(Thread):
    """ Keep checking for for new client connections. """
    def __init__(self, tcpServer):
        Thread.__init__(self)
        self.tcpServer = tcpServer

        print("Starting server thread.")

    def run(self):
        MonitorThread().start()
        while True:
            self.tcpServer.listen()
            (conn, (ip, port)) = self.tcpServer.accept()
            newthread = ClientThread(conn, ip, port)
            newthread.start()
            print(f"[NEW CONNECTION] {ip} on port {port} connected.")
            print("CONNECT: lock get")
            lock.acquire()
            threads.append(newthread)
            lock.release()
            print("CONNECT: lock release")

class MonitorThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        print("Starting monitoring thread.")

    def run(self):
        """ Check if a new project has arrived. """
        root = './'
        projs_set = {}
        while True:
            curr_projs_set = {item for item in os.listdir(root) if item != '__pycache__' and os.path.isdir(os.path.join(root, item))}
            new_projs_set = curr_projs_set.difference(projs_set)
            global threads
            if len(new_projs_set) and len(threads):
                print("new job detected")
                for new_proj in new_projs_set:
                    # should have just one .blend file in here
                    for filename in os.listdir(new_proj):
                        print(filename)
                        if filename.endswith(".blend"):
                            print("MONITOR: lock get")
                            lock.acquire()
                            threads_tmp = threads
                            threads = []
                            lock.release()
                            print("MONITOR: lock release")
                            filepath = new_proj + "/" + filename
                            file_len = str(os.path.getsize(filepath))

                            """ Opening and reading the .blend file data. """
                            file = open(filepath, "rb")
                            data = file.read()

                            """ Naively spread frames amongst available clients. 1 client can't handle more than 1 job. """
                            res = blender_render_info.read_blend_rend_chunk(filepath)
                            print(res)
                            [(frame_start, frame_end, _)] = res
                            num_available_clients = len(threads_tmp)
                            frames_per_client = (frame_end - frame_start + 1) // num_available_clients
                            # last client will get any leftovers
                            # not handling the case where num_available_clients > num_frames_to_render
                            # because don't ever think we'll reach that point with this demo

                            for ind, client in enumerate(threads_tmp):
                                start_frame = frame_start + ind * frames_per_client
                                end_frame = start_frame + frames_per_client - 1
                                if ind == len(threads_tmp) - 1:  # last client
                                    end_frame = frame_end

                                client.filepath = filepath
                                client.file_len = file_len
                                client.start_frame = start_frame
                                client.end_frame = end_frame
                                client.data = data
                                client.waiting = False
                            file.close()
                projs_set = curr_projs_set

class ClientThread(Thread):
    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.waiting = True
        print("[+] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
        print('Waiting for client status')
        intent = self.conn.recv(SIZE).decode(FORMAT)
        print(intent)
        if intent == "available":
            while self.waiting:
                time.sleep(5)
            print("Starting job")
            print(self.filepath)
            self.conn.send((self.filepath + "\n" + self.file_len + "\n" + str(self.start_frame) + "\n" + str(self.end_frame)).encode(FORMAT))
            self.conn.recv(SIZE)  # confirm client received metadata
            self.conn.send(self.data)  # send whole file
            self.conn.recv(SIZE)  # confirm client received .blend file
            print("Sent File Data")
        else: # done
            print("Client's done")

            while True:
                metadata = self.conn.recv(SIZE).decode(FORMAT).split("\n")
                if len(metadata) == 1:
                    break
                self.conn.send("ack".encode(FORMAT))
                try:
                    file = open(metadata[0], "wb")
                except FileNotFoundError:
                    os.makedirs("./" + metadata[0].split("/")[0] + "/outputs")
                    file = open(metadata[0], "wb")
                output_file_len = int(metadata[1])
                data = bytearray(output_file_len)
                pos = 0
                while pos < output_file_len:
                    cr = self.conn.recv_into(memoryview(data)[pos:])
                    if cr == 0:
                        raise EOFError
                    pos += cr
                file.write(data)
                print("RECEIVED OUTPUT " + metadata[0])
                self.conn.send("file received".encode(FORMAT))

        self.conn.close()

IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((IP, PORT))

lock = threading.Lock()

print("Multithreaded Python server : Waiting for connections from TCP clients...")
ConnectionThread(tcpServer).start()
