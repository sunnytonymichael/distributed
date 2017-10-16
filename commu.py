
from socket import *
import threading
import json
import server
import pickle

class Connection:
    # all nodes

    def __init__(self):
        self.PORT = 8963
        self.address = []
        self.close = False
        # self.all_address = []
        # self.all_user_id = []
        # for info in self.user_info:
        #     self.address.append(info[0])
        #     self.all_address.append(info[0])
        #     self.all_user_id.append(info[1])
        #     if info[1] == self.user_id:
        #         self.self_ip = info[0]
        # remove self ip
        # try:
        #     self.address.remove(self.self_ip)
        # except Exception as e:
        #     pass
        # address of other nodes

            # read config.txt

    def readconfig(self):
        file = open("config.txt")
        try:
            file_line = file.readlines()
            # print(file_line)
            # print(type(file_line))
            nodes = [(addr, user_id)
                     for line in file_line
                     for addr, user_id in [line.strip().split(":")]]
        finally:
            file.close()
        '''''
        print(nodes)
        print(type(nodes))
        print(type(nodes[1]))
        print(nodes[2][1])
        print(type(nodes[2][1]))
        '''''
        return nodes

    # method that get local ip address
    def get_host_ip(self):
        ip = ""
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def shutdown(self):
        self.close = True
        print("shutting")
        #self.listen_thread.join()


    # create a socket
    def mysocket(self):
        # create a UDP socket
        sock = socket(AF_INET, SOCK_DGRAM)
        # ??
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        return sock

    # define a listen method
    def listen(self):
        listen_sock = self.mysocket()
        listen_sock.bind(('0.0.0.0', self.PORT))
        print('start to listen')
        while self.close == False:
            data, sender = listen_sock.recvfrom(4096)
            sender_addr = sender[0]
            encode_data = pickle.loads(data)
            send_log = encode_data[0]
            send_ClockMatrix = encode_data[1]
            server.receive_tweet(sender_addr, send_log, send_ClockMatrix)
            # print(sender_addr, ' say: ', data)
            # if data == 'exit':
            #     break
        print("down")
        listen_sock.close()

    # create a new thread to start listen
    def listen_start(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

    def send_msg(self, receiver_ip, NP,ClockMatrix):
        send_sock = self.mysocket()
        # time = [[0 for x in range(4)]for y in range(4)]
        # msg =('hello', 'world', 666, time)
        # print(msg)
        nodes = receiver_ip
        data = [NP,ClockMatrix]
        log_to_send = pickle.dumps(data)
        # ClockMatrix_to_send = pickle.dumps(ClockMatrix)
        send_sock.sendto(log_to_send, (nodes, 8963))
        #send_sock.sendto(ClockMatrix_to_send,(nodes, 8963))
        # for nodes in self.address:
        send_sock.close()

    def tweet_start(self):
        tweet_thread = threading.Thread(target=self.send_msg)
        tweet_thread.start()

if __name__ == "__main__":

    connect = Connection()
    print(connect.address)
    #connect.listen_start()
    #connect.readconfig()
    print(connect.all_user_id)
    print(connect.all_address)
    '''''
    while True:
        print('want commu?', ' 1 = yes', ' 2 = no')
        choice = input('>')
        if choice == '1':
            connect.tweet_start()
        else:
            break
    '''
