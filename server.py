from datetime import datetime
from copy import copy
import commu
import pickle
from socket import *
import os



Log = None
ClockMatrix = None
Users = []
Address = []
Block = None

Own_user = None

def readconfig():
    file = open("config.txt")
    try:
        file_line = file.readlines()
        nodes = [(addr, user_id)
                for line in file_line
                for addr, user_id in [line.strip().split(":")]]
    finally:
        file.close()
    return nodes


def load_txt():
    global Own_user
    global Users
    global Address
    user_info = readconfig()
    print('Please enter your user id')
    user_id = input('')
    Own_user = int(user_id)
    address = []
    all_address = []
    all_user_id = []
    for info in user_info:
        address.append(info[0])
        all_address.append(info[0])
        all_user_id.append(int(info[1]))
        if info[1] == user_id:
            self_ip = info[0]


def get_users_and_addr():
    user_info = readconfig()
    all_address = []
    all_user_id = []
    for info in user_info:
        all_address.append(info[0])
        all_user_id.append(int(info[1]))
    return all_address, all_user_id

Address, Users = get_users_and_addr()

class BlockEvent:
    def __init__(self, user, target, time):
        self.user = user
        self.target = target
        self.time = time

class UnblockEvent:
    def __init__(self, user, target, time):
        self.user = user
        self.target = target
        self.time = time

class Tweet:
    def __init__(self, user, text, time):
        self.user = user
        self.text = text
        self.time = time


#dictionary to list
def hash_dict(dictionary):
    list = []
    for user, temp in dictionary.items():
        for other_users, temp2 in temp.items():
            list.append((user,other_users,temp2))
    return list

#list to dictionary
def unhash_dict(list):
    matrix = {}
    for user in Users:
        matrix[user] = {}
        for other_users in Users:
            matrix[user][other_users] = 0

    for element in list:
        user = element[0]
        other_users = element[1]
        temp = element[2]
        matrix[user][other_users] = temp
    return matrix

def save_ClockMatrix():
    global ClockMatrix
    list = hash_dict(ClockMatrix)
    pickle.dump(list, open('ClockMatrix.pickle', 'wb'))

def load_ClockMatrix():
    global Users
    time = datetime.utcnow()
    if os.path.isfile('ClockMatrix.pickle'):
        list = pickle.load(open("ClockMatrix.pickle", 'rb'))
        return unhash_dict(list)
    else:
        matrix = {}

        for user in Users:
            matrix[user] = {}
            for other_users in Users:
                matrix[user][other_users] = time

        return matrix

#set to list
def save_Log():
    global Log
    Log = list(Log)
    with open('Log.pickle','wb') as file:
        pickle.dump(Log, file)

#list to set
def load_Log():

    if not os.path.isfile('Log.pickle'):
        return set()
    else:
        list = pickle.load(open("Log.pickle", 'rb'))
        return set(list)

def hasRecv(event,receiver):
    global ClockMatrix
    if ClockMatrix[event.user][receiver] >= event.time:
        return True
    else:
        return False


def partial_log(receiver):
    global Log
    NP = copy(Log)#Shallow copy
    NP = set(NP)
    for event in Log:
        flag = hasRecv(event,receiver)
        if flag == False:
            NP.add(event)
    return NP



def get_blocked():
    global Log
    global Users
    #set initial block matrix to all unblock status
    blocked = {}
    if Users != None:
        for user in Users:
            blocked[user] = {}
            for other_users in Users:
                if other_users != user:
                    time = datetime.utcnow()
                    blocked[user][other_users] = UnblockEvent(user, other_users, time)


    events = set(filter(lambda event: type(event) is BlockEvent or type(event) is UnblockEvent, Log))

    for event in events:
        if event.time > blocked[event.user][event.target].time:
            blocked[event.user][event.target] = event
    return blocked

Log = load_Log()
ClockMatrix = load_ClockMatrix()
Block = get_blocked()

def block(blockee):
    global Log
    global ClockMatrix
    global Block
    global Own_user
    #create a BlockEvent
    time = datetime.utcnow()
    blockevent = BlockEvent(Own_user,blockee, time)
    #remove the previous block or unblock log
    Log =  {event for event in Log if not (((type(event) is BlockEvent) or (type(event) is UnblockEvent))
                        and event.user == Own_user and event.target == blockee)
            }
    #update log and matrix
    Log.add(blockevent)
    ClockMatrix[Own_user][Own_user] = time
    #update blockmatrix
    Block[Own_user][blockee] = blockevent
    #sync
    save_Log()
    save_ClockMatrix()

def unblock(unblockee):
    global Log
    global ClockMatrix
    global Block
    global Own_user
    #create a UnblockEvent
    time = datetime.utcnow()
    unblockevent = UnblockEvent(Own_user,unblockee, time)
    #remove the previous block or unblock log
    Log =  {event for event in LOG if not (((type(event) is BlockEvent) or (type(event) is UnblockEvent))
                        and event.user == Own_user and event.target == blockee)
            }
    #update log and matrix
    Log.add(unblockevent)
    ClockMatrix[Own_user][Own_user] = time
    #update blockmatrix
    Block[Own_user][blockee] = unblockevent
    #sync
    save_Log()
    save_ClockMatrix()

def send_tweet(text):#,log,follower):

    global ClockMatrix
    global Own_user


    global Address
    global Users

    global Log
    #create a tweet event
    time = datetime.utcnow()
    tweet = Tweet(Own_user, text, time)
    #update the ClockMatrix

    ClockMatrix[Own_user][Own_user] = time
    hashed_cm = hash_dict(ClockMatrix)

    for receiver in Users:
        if receiver == Own_user:
            continue
        if not type(Block[Own_user][receiver]) is BlockEvent:
            NP = partial_log(receiver)
            NP.add(tweet)
            temp = Users.index(receiver)
            receiver_ip = Address[temp]
            connect = commu.Connection()
            connect.send_msg(receiver_ip,NP,hashed_cm)

    #update local log
    Log = set(Log)
    Log.add(tweet)
    save_Log()
    save_ClockMatrix()


#update local ClockMatrix
def update_ClockMatrix(sender, send_ClockMatrix):
    global ClockMatrix
    for user in Users:
        ClockMatrix[Own_user][user] = max(ClockMatrix[Own_user][user],send_ClockMatrix[sender][user])
    for user in Users:
        for other_users in Users:
            ClockMatrix[user][other_users] = max(ClockMatrix[user][other_users],send_ClockMatrix[user][other_users])

def receive_tweet(sender, send_log, send_ClockMatrix):
    global Users
    global Block
    global Log
    global Own_user
    global ClockMatrix
    global Address
    temp = Address.index(sender)
    sender_id = Users[temp]

    def update_ClockMatrix(sender, send_ClockMatrix):
        global ClockMatrix
        global Users
        global Own_user
        for user in Users:
            ClockMatrix[Own_user][user] = max(
                    ClockMatrix[Own_user][user],
                    send_ClockMatrix[sender][user]
                )

            ClockMatrix[user][sender] = max(
                    ClockMatrix[user][sender],
                    send_ClockMatrix[user][sender]
                )

    #Update local time matrix
    update_ClockMatrix(sender_id, ClockMatrix)


    #update block things
    events = list(filter(lambda event: type(event) is BlockEvent or type(event) is UnblockEvent,send_log))

    for event in events:
        if event.time > Block[event.user][event.target].time:
            Log =  {temp for temp in Log if not (((type(event) is BlockEvent) or (type(event) is UnblockEvent))
                                and event.user == temp.user and event.target == temp.user)
                    }

            Block[event.user][event.target] = event
            Log.add(event)
    #Merge the send log with local log after removing block and unblock events
    send_log = set(filter(lambda event: not(type(event) is BlockEvent or type(event) is UnblockEvent),send_log))
    Log = set(Log)
    Log = Log.union(send_log)
    #save
    save_Log()
    save_ClockMatrix()

def view():

    global Log
    global Block

    temp = set(filter(lambda event: type(event) is Tweet, Log))

    tweets = [(tweet.user, tweet.text, tweet.time) for tweet in temp]

    #sorted by time
    tweets = sorted(tweets, key=lambda tweet: tweet[2], reverse=True)

    #filter block
    for blocker in Users:
        if blocker == Own_user:
            continue
        temp = Block[blocker][Own_user]
        if type(temp) is BlockEvent:
            tweets = list(filter(lambda tweet: not tweet[0] == blocker, tweets))

    print(tweets)
