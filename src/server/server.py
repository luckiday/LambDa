import os

import blender_render_info
import socket
import threading
from threading import Thread
import time
import string
import random
import shutil

# Multithreaded Python server : TCP Server Socket Thread Pool
workers = []
jobs_map = {} # map project names to [RequesterThread, num frames to render, rendering engine]
worker_lock = threading.Lock()
jobs_map_lock = threading.Lock()

"""
Flow:
1. requester connects with server
2. requester tells server it's a requester
3. server acks
4. requester sends metadata
5. server acks
6. requester sends .blend
7. server acks and saves to server's dir in some project folder
8. server's MonitorThread senses that something has been added to server's dir and asks client to fulfill job
9. client disconnects from server to do worrk
10. client finishes job, reconnects with server, and sends outputs to server
11. server sees that all frames have been rendered and sends outputs to requester
"""

class ConnectionThread(Thread):
    """ Keep checking for for new client connections. """
    def __init__(self, tcpServer):
        Thread.__init__(self)
        self.tcpServer = tcpServer

        print("[CONN] Starting server thread.")

    def run(self):
        MonitorThread().start()
        print(f"Server running at {IP}:{PORT}")
        while True:
            self.tcpServer.listen()
            (conn, (ip, port)) = self.tcpServer.accept()
            role = conn.recv(SIZE).decode(FORMAT)
            if role == "worker":
                newthread = WorkerThread(conn, ip, port)
                newthread.start()
                print(f"[CONN] New worker {ip} on port {port} connected.")
                print("[CONN] worker_lock get")
                worker_lock.acquire()
                workers.append(newthread)
                worker_lock.release()
                print("[CONN] worker_lock release")
            else:
                newthread = RequesterThread(conn, ip, port)
                newthread.start()
                print(f"[CONN] New requester {ip} on port {port} connected.")

class MonitorThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        print("[MON] Starting monitoring thread.")

    def run(self):
        """ Check if a new project has arrived. """
        projs_set = set()
        while True:
            curr_projs_set = set([item for item in os.listdir(PROJECTS_DIR)
                if (
                    item != '__pycache__'
                    and os.path.isdir(os.path.join(PROJECTS_DIR, item))
                    and not item.startswith("CHECKING_"))])
            new_projs_set = curr_projs_set.difference(projs_set)
            global workers

            if len(new_projs_set) and len(workers):
                for new_proj in new_projs_set:
                    print("[MON] New proj: " + new_proj)
                    # should have just one .blend file in here
                    for filename in os.listdir(PROJECTS_DIR + "/" + new_proj):
                        if filename.endswith(".blend"):
                            filepath = new_proj + "/" + filename
                            file_len = str(os.path.getsize(PROJECTS_DIR + "/" + filepath))
                            if file_len == "0":
                                """
                                haven't finished writing to the file yet
                                try again next iteration
                                """
                                break

                            """ Opening and reading the .blend file data. """
                            file = open(PROJECTS_DIR + "/" + filepath, "rb")
                            data = file.read()

                            """ Naively spread frames amongst available clients. 1 client can't handle more than 1 job. """
                            res = blender_render_info.read_blend_rend_chunk(PROJECTS_DIR + "/" + filepath)
                            print("[MON] blender_render_info result: " + str(res))
                            if (res == []):
                                print(f"[MON] blender_render_info failed for {filepath}, skipping it.")
                                break
                            [(frame_start, frame_end, _)] = res
                            # frame_start, frame_end = 23, 24

                            """ Reserve workers for this job. """
                            print("[MON] worker_lock get")
                            worker_lock.acquire()
                            while (len(workers) == 0):
                                print("No workers available, waiting...")
                                worker_lock.release()
                                time.sleep(5)
                                worker_lock.acquire()
                            workers_tmp = workers
                            workers = []
                            worker_lock.release()
                            print("[MON] worker_lock release")

                            num_available_clients = len(workers_tmp)
                            frames_per_client = (frame_end - frame_start + 1) // num_available_clients
                            # last client will get any leftovers
                            # not handling the case where num_available_clients > num_frames_to_render
                            # because don't ever think we'll reach that point with this demo

                            for ind, client in enumerate(workers_tmp):
                                start_frame = frame_start + ind * frames_per_client
                                end_frame = start_frame + frames_per_client - 1
                                if ind == len(workers_tmp) - 1:  # last client
                                    end_frame = frame_end

                                client.filepath = filepath
                                client.file_len = file_len
                                client.start_frame = start_frame
                                client.end_frame = end_frame
                                client.data = data
                                client.waiting = False
                                client.proj_name = new_proj
                            file.close()
                            projs_set.add(new_proj)
                            break

class WorkerThread(Thread):
    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.waiting = True
        print("[WORK] New worker socket thread started for " + ip + ":" + str(port))

    def run(self):
        self.conn.send("role".encode(FORMAT)) # ack
        print("[WORK] Waiting for client status")
        intent = self.conn.recv(SIZE).decode(FORMAT)
        if intent == "available":
            print("[WORK] Client's available")
            while self.waiting:
                time.sleep(5)
            print("[WORK] Starting job: " + self.filepath)
            self.conn.send((
                self.filepath
                + "\n" + self.file_len
                + "\n" + str(self.start_frame)
                + "\n" + str(self.end_frame)
                + "\n" + str(jobs_map[self.proj_name][2]) # Look up rend engine
                ).encode(FORMAT))
            self.conn.recv(SIZE)  # confirm client received metadata
            self.conn.send(self.data)  # send whole file
            self.conn.recv(SIZE)  # confirm client received .blend file
            print("[WORK] Sent File Data")
        else: # done
            print("[WORK] Client's done")
            proj_name = ""
            while True:
                metadata = self.conn.recv(SIZE).decode(FORMAT).split("\n")
                if len(metadata) == 1:
                    break
                self.conn.send("ack".encode(FORMAT))

                proj_name = metadata[0].split("/")[0]
                try:
                    file = open(PROJECTS_DIR + "/" + metadata[0], "wb")
                except FileNotFoundError:
                    os.makedirs(PROJECTS_DIR + "/" + proj_name + "/outputs")
                    file = open(PROJECTS_DIR + "/" + metadata[0], "wb")
                output_file_len = int(metadata[1])
                data = bytearray(output_file_len)
                pos = 0
                while pos < output_file_len:
                    cr = self.conn.recv_into(memoryview(data)[pos:])
                    if cr == 0:
                        raise EOFError
                    pos += cr
                file.write(data)
                print("[WORK] RECEIVED OUTPUT " + metadata[0])
                self.conn.send("file received".encode(FORMAT))

            """ Check whether this project's done rendering. """
            if (proj_name != "" and
                len(os.listdir(PROJECTS_DIR + "/" + proj_name + "/outputs"))
                    == jobs_map[proj_name][1]):
            # if len(os.listdir(PROJECTS_DIR + "/" + proj_name + "/outputs")) == 2:
                """ Done with this project so notify requester. """
                jobs_map[proj_name][0].waiting = False
        self.conn.close()

class RequesterThread(Thread):
    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.waiting = True
        print("[REQ] New requester socket thread started for " + ip + ":" + str(port))

    def run(self):
        self.conn.send("role".encode(FORMAT)) # ack

        """ Get project metadata. """
        metadata = self.conn.recv(SIZE).decode(FORMAT).split("\n")
        """ Check received metadata """
        if (len(metadata) != 3):
            self.conn.send("CANCEL".encode(FORMAT))
            self.conn.close()
            return
        self.conn.send("ack".encode(FORMAT))

        rend_engine = metadata[2]

        """ Get .blend file and save to project folder. """
        print("[REQ] Receiving .blend file.")
        blend_file_len = int(metadata[1])
        data = bytearray(blend_file_len)
        pos = 0
        while pos < blend_file_len:
            cr = self.conn.recv_into(memoryview(data)[pos:])
            if cr == 0:
                raise EOFError
            pos += cr
        print("[REQ] Received .blend file.")
        self.conn.send("file received".encode(FORMAT))

        """ Save to project folder. """
        char_pool = string.ascii_letters + string.digits
        proj_name = ''.join(random.choice(char_pool) for i in range(10)) # create random 10-char proj name
        while proj_name in os.listdir(PROJECTS_DIR):
            proj_name = ''.join(random.choice(char_pool) for i in range(10)) # create random 10-char proj name

        """ Name project directory starting with CHECKING_ so it's ignored until Blend file check is done. """
        os.makedirs(PROJECTS_DIR + "/CHECKING_" + proj_name)
        file_name = proj_name + "/" + metadata[0]
        with open(PROJECTS_DIR + "/CHECKING_" + file_name, "wb") as file:
            file.write(data)

        """
        Figure out how many frames this project needs to render.
        Keep track of this so know when workers are done rendering.
        """
        res = blender_render_info.read_blend_rend_chunk(PROJECTS_DIR + "/CHECKING_" + file_name)
        """ If .blend file can't be parsed, cancel the job and let the requester know. """
        if (res == []):
            print(f"[REQ] blender_render_info failed for {file_name}. Cancelling request.")
            try:
                shutil.rmtree(PROJECTS_DIR + "/CHECKING_" + proj_name)
            except OSError as e:
                print("Error: %s : %s" % (proj_name, e.strerror))
            self.conn.send("CANCEL".encode(FORMAT))
            self.conn.close()
            return

        """ Rename project directory to remove 'CHECKING_' now that check has passed. """
        os.replace(PROJECTS_DIR + "/CHECKING_" + proj_name, PROJECTS_DIR + "/" + proj_name)

        [(frame_start, frame_end, _)] = res
        jobs_map_lock.acquire()
        jobs_map[proj_name] = [self, frame_end - frame_start + 1, rend_engine]
        jobs_map_lock.release()

        """ Wait for workers to finish renders. """
        while self.waiting:
            time.sleep(5)

        """ Send outputs to requester. """
        for filename in os.listdir(PROJECTS_DIR + "/" + proj_name + "/outputs"):
            filepath = proj_name + "/outputs/" + filename
            file = open(PROJECTS_DIR + "/" + filepath, "rb")
            data = file.read()
            file_len = str(os.path.getsize(PROJECTS_DIR + "/" + filepath))
            self.conn.send((filepath + "\n" + file_len).encode(FORMAT))
            self.conn.recv(SIZE) # ack
            self.conn.send(data)
            self.conn.recv(SIZE) # ack
        self.conn.send("DONE".encode(FORMAT))
        self.conn.close()

        """ Delete project folder. """
        try:
            shutil.rmtree(PROJECTS_DIR + "/" + proj_name)
        except OSError as e:
            print("Error: %s : %s" % (proj_name, e.strerror))

        jobs_map_lock.acquire()
        del jobs_map[proj_name]
        jobs_map_lock.release()

IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((IP, PORT))

""" Initialize empty projects directory. """
PROJECTS_DIR = './.lambda_projects_queue'
if (".lambda_projects_queue" in os.listdir('./') and os.path.isdir(PROJECTS_DIR)):
    shutil.rmtree(PROJECTS_DIR)
os.makedirs(PROJECTS_DIR)

print("Multithreaded Python server : Waiting for connections from TCP clients...")
ConnectionThread(tcpServer).start()
