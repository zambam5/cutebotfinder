
import cfg
import socket
import time
import logging
import os
import requests
import json
from datetime import datetime, date



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('bot.log', mode='w')
formatter = logging.Formatter('''%(asctime)s -
                              %(name)s - %(levelname)s - %(message)s''')
handler.setFormatter(formatter)
logger.addHandler(handler)

s = None
try:
    s.close()
except:
    pass

s = socket.socket()
try:
    s.connect((cfg.HOST,cfg.PORT))
except ConnectionAbortedError:
    logger.info('Connection Failed')
'''
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
test = s.recv(1024).decode("utf-8")
logger.info(test)

s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
logger.info(s.recv(1024).decode("utf-8"))
logger.info(s.recv(1024).decode("utf-8"))


s.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
logger.info(s.recv(1024).decode("utf-8"))
s.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
logger.info(s.recv(1024).decode("utf-8"))
'''
def login(sock, PASS, NICK, CHAN):
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    test = s.recv(1024).decode("utf-8")
    logger.info(test)

    s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
    logger.info(s.recv(1024).decode("utf-8"))
    logger.info(s.recv(1024).decode("utf-8"))


    s.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
    logger.info(s.recv(1024).decode("utf-8"))
    s.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
    logger.info(s.recv(1024).decode("utf-8"))

def chat(sock, msg):
    #this was not written by me
    """
    Send a chat message to the server.
    Keyword arguments:
    sock -- the socket over which to send the message
    msg  -- the message to be sent
    """
    sock.send("PRIVMSG {} :{}\r\n".format(cfg.CHAN, msg).encode("utf-8"))

def ping(sock, response):
    #check for ping from twitch and respond
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        logger.info('ping')
        return True

def pong(sock):
    s.send("PING :tmi.twitch.tv\r\n".encode("utf-8"))

def splitmessages(response):
    linecount=response.count('\r\n')
    messages = []
    if linecount==1:
        messages.append(response)
        return messages
    elif linecount > 1:
        messages1 = response.split('\r\n')
        for i in messages1:
            if len(i) == 0:
                continue
            else:
                messages.append(i)
        return messages

def viewer_list(chan):
    #should only need the channel name here    
    url = "https://tmi.twitch.tv/group/user/{}/chatters".format(chan)
    r = requests.get(url)
    chatters = json.loads(r.content)['chatters']
    moderators = chatters['moderators']
    viewers = chatters['viewers']
    return moderators, viewers


def followage(username,chan):
    url = "https://api.twitch.tv/kraken/users/"\
          "{}/follows/channels/{}".format(username, chan)
    page = requests.get(url)
    data = json.loads(page.content)
    if "error" in data.keys():
        return -1
    else:
        x = data["created_at"]
        y = datetime.now()
        z = y-x
        return z.days()

def botcheck(name,potentialbots):
    name=name.lower()
    x = len(name)
    name = ''.join([i for i in name if not i.isdigit()])
    if name in potentialbots:
        return True
    else:
        return False

def bot_finder(viewers,whitelist,sock,chan,potentialbots):
    print("finding bots")
    #sock is needed to message me
    #chan is needed to check followage
    #turn viewers, whitelist into sets
    v = set(viewers)
    w = set(whitelist)
    #remove whitelisted viewers from viewer list
    v = v-w
    #need a container for potential bots
    botlist = []
    for i in v:
        if botcheck(i,potentialbots):
            botlist.append(i)
    b = set(botlist)
    v = v-b
    w = w|v
    number = len(botlist)
    test = 0
    if number > 50:
        test = 1
        chat(s, "/followers 2 months")
        time.sleep(1/cfg.RATE)
        chat(s, "/me the bot thinks they're here")
        bot_killer(botlist,sock)
        return botlist
    whitelist.update(w)
    if test:
        chat(s, "/me bot has gone through the list it had,"
             +" turning off followers only mode")
        time.sleep(1/cfg.RATE)
        chat(s, "/followersoff")
    return botlist

def bot_killer(botlist,sock):
    for i in botlist:
        print(i)
        chat(s, "/ban {} cute bot".format(i))
        time.sleep(1/cfg.RATE)

def white_list(mods,whitelist,sock,message):
    messagex = message.split(';')
    if "zambam5" in message and "~!wl" in message and messagex[6] == "mod=1":
        x=message.find("~")
        y = message[x+4:]
        while y[0] == " ":
            y = y[1:]
        if y in whitelist:
            chat(sock, "@zambam5 already whitelisted")
        else:
            whitelist.update([y.rstrip()])
            print(y, " whitelisted")
            chat(sock, "@zambam5 whitelisted, check log")

def black_list(mods,sock,message):
    message = message.split(';')
    if message[6] == "mod=1":
        if "~!flag" in message[-1]:
            user = message[2].split("=")[1]
            x = message[-1].find("~")
            y = message[-1][x:]
            z = y.find(" ")
            logger.info("check chat log " + y[z+1:])
            chat(s, "@{} user has been flagged".format(user))

'''
Sets required in the above functions
sets are used because order does not matter and they are faster
'''
adjectives = set([line.split(',') for line in open("english-adjectives.txt")][0])
nouns = set([line.split(',') for line in open("english-nouns.txt")][0])
whitelist = set([line.split(',') for line in open("white_list.txt")][0])
potentialbots = set([line.split(',') for line in open("potentialbotnames.txt")][0])

login(s, cfg.PASS, cfg.NICK, cfg.CHAN)
chan = cfg.CHAN[1:]
potentialbots =set()
for i in adjectives:
    for j in nouns:
        potentialbots.update([i+j])

with open('potentialbotnames.txt','w') as f:
    f.writelines(",%s" % item for item in potentialbots)

t = time.time()
while True:
    try:
        #phase1 checks for bots
        #phase2 keeps bot connected to twitch
        x = viewer_list(chan)
        viewers = x[1]
        y = bot_finder(viewers,whitelist,s,chan,potentialbots)
        print(" botlist ", y)
        if time.time()-t > 290:
            whitelist = set([line.split(',') for line in open("white_list.txt")][0])
            try:
                response = s.recv(1024).decode("utf-8")
            except UnicodeDecodeError:
                pass
            ping_test = ping(s,response)
            if ping_test:
                t = time.time()
        elif time.time()-t > 320:
            pong(s)
            try:
                response = s.recv(1024).decode("utf-8")
            except UnicodeDecodeError:
                pass
            if "PONG :tmi.twitch.tv\r\n" in response:
                t = time.time()
            else:
                s.close()
                s = socket.socket()
                try:
                    s.connect((cfg.HOST,cfg.PORT))
                    login(s, cfg.PASS, cfg.NICK, cfg.CHAN)
                except ConnectionAbortedError:
                    logger.info('Connection Failed')
                t = time.time()
        time.sleep(1/cfg.RATE)
    except:
        logger.exception("Fatal error in main loop")
        continue
