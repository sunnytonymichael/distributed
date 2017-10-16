from commu import Connection
import server

# def write_tweet():
#     tweet = input("Enter your tweet: ")
#     return tweet

# def readconfig():
#     file = open("config.txt")
#     try:
#         file_line = file.readlines()
#         # print(file_line)
#         # print(type(file_line))
#         nodes = [(addr, user_id)
#                 for line in file_line
#                 for addr, user_id in [line.strip().split(":")]]
#     finally:
#         file.close()
#     return nodes



    # all_nodes = readconfig()
    # print('enter ur user id')
    # self_id = input('')
    # address = []c
    # self.all_address = []
    # self.all_user_id = []
    # for info in self.user_info:
    #     self.address.append(info[0])
    #     self.all_address.append(info[0])
    #     self.all_user_id.append(info[1])
    #     if info[1] == self.user_id:
    #         self.self_ip = info[0]



if __name__ == "__main__":
    server.load_txt()
    connect = Connection()
    connect.listen_start()
    user_command = ""
    while (1):
        user_command = input("Please enter your command\n")
        if user_command == "tweet":
            print("please enter what you want to tweet")
            text = input('')
            server.send_tweet(text)

        elif user_command == "view":
            server.view()
        elif user_command == "block":
            print("please enter who you want to block")
            blockee = int(input(''))
            server.block(blockee)
        elif user_command == "unblock":
            print("please enter who you want to unblock")
            unblockee = int(input(''))
            server.block(unblockee)
        elif user_command == "end":
            shutdown = Connection()
            shutdown.shutdown()
            print("COMPLETE")
            bre
