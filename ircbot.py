#!/usr/bin/python

import socket
import sys
import time

# IRC servers:
freenode = "irc.freenode.net"
ircnet = "irc.utu.fi"
efnet = "efnet.portlane.se"
slavelist  = [ircnet, efnet, freenode]

#########################
#C2 settings:
if len(sys.argv) < 2:
    master = freenode
    channel = "#nicenicebot"
    botnick = "nicebot"
    password = "nicepass"
else:
    master = str(sys.argv[1])
    channel = str(sys.argv[2])
    botnick = str(sys.argv[3])
    password = str(sys.argv[4])
#########################

def openConn(server):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #open a socket
    soc.connect((server, 6667)) #connect to server
    soc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :Nice bot here!\n") #user authentication
    soc.send("NICK "+ botnick +"\n")
    soc.send("PRIVMSG nickserv :identify %s %s\n" % (botnick, password))
    return soc

def closeConn(soc):
#    soc.shutdown(socket.SHUT_RDWR)
    soc.close()
    return

        
def ping(recieved, server, soc):
    if recieved.find("PING") != -1:     
        if server in [efnet]:
            soc.send("\QUOTE PONG " + recieved.split() [1] + "\n")
        else:
            soc.send("PONG " + recieved.split() [1] + "\n")
    return

def getWhois(kuka, C2):
    print "Asking from slaves :: \whois "+kuka+"\n"

    for srv in slavelist:
        if srv == master:
            C2.send("WHOIS "+ kuka +"\n")
        else:
            irc = openConn(srv)      
            irc.send("WHOIS "+ kuka +"\n")
            
        while 1:              # Loop to whois replies
            if srv == master:
                text = C2.recv(1024)
            else:
                text = irc.recv(1024)  #Listen to receive the whois reply

            ping(text, srv, irc)
            
            if text.find('311') != -1:
                t1 = text.split('\n') 
                for i in xrange(16):
                    if t1[i].find('311') != -1:
                        ti1 = t1[i].split(botnick) 
                        to1 = ti1[1].strip()
                        print "Answer from "+srv+" :: "+str(to1)+"\n"
                        break #from for
                break #from whois while loop
        
            if text.find('401') != -1:
                t2 = text.split('\n') 
                for i in xrange(16):
                    if t2[i].find('401') != -1:
                        ti2 = t2[i].split(botnick) 
                        to2 = ti2[1].strip()
                        print "Answer from "+srv+" :: "+str(to2)+"\n"
                        break #from for
                break #from whois while loop

        closeConn(irc) 
    return


def main():
#    global C2
    C2 = openConn(master)
    print "Connecting to C2: "+ master
    C2.send("JOIN "+ channel +"\n")   #join the C2 channel
    print "Wait for one minute for the connection to establish before making any whois querys.\n"
    
    
    while 1:                          # C2-loop
        connexion = C2.recv(4096)     # Listen for commands from C2
#        print connexion
        time.sleep( 1 )
        ping(connexion, master, C2)

        if connexion.find(':!whois') != -1:
            who = connexion.split('!whois') 
            kuka = who[1].strip()     # remove whitespaces
            getWhois(kuka, C2)
            
        if connexion.find(':!halt') != -1:
            closeConn(C2)
            return 0
                    
main()
