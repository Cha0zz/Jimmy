#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20-sep.-2015

@author: jasperdelaey

This program is an IRC Chatbot created with the help of a tutorial found on: http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
'''


import socket
import pickle
import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import wikipedia
import random
import json
import thread
import lxml
from lxml import etree
import pywapi
import mechanize
from urlparse import urlparse
import hashlib
import string
# from apiclient.discovery import build
# import urbandict
# import time
# import ast

server = "burstfire.uk.eu.gamesurge.net"  # settingss
channel = "#limittheory"
botnick = "Jimmy42"

# defines the socket
irc = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
# connects to the server
irc.connect((server, 6667))
irc.send("USER " + botnick + " " + botnick + " " + botnick +
         " :Jimmy\n")  # user authentication
irc.send("NICK " + botnick + "\n")  # sets nick
irc.send("PRIVMSG nickserv :iNOOPE\r\n")  # auth

connected = False
sleep = False
corn_mode = True
override = False
cheercount = 0
hailcount = 0
wavecount = 0
readbuffer = ""


error = "Something went wrong."


f = open('/users/jasperdelaey/documents/workspace/bot/savefile', 'rb')
array = pickle.load(f)
f.close()

f2 = open(
    '/users/jasperdelaey/documents/workspace/bot/personalsavefile', 'rb')
pmusic = pickle.load(f2)
f2.close()

pmusic_arr = {"Cha0zz": [
    "https://www.youtube.com/watch?v=6l6vqPUM_FE"]}

nopelist = ["KungCheops"]

commands = ["!nick", "!quit", "!help", "!join", "!leave", "!sleep", "!wake", "!work", "!bed", "!choose", "!no",
            "!update", "!corn_on", "!corn_off", "!countdown", "!sing", "!music", "!add", "!remove", "!songcount", "!psongcount", "!youtube", "!wiki", "!google", "!padd", "!premove", "!pmusic", "!image", "!roll", "!plist", "!moon", "!weather",
            "!urban", "!dict", "!identify"]  # list of available commands

greetings = ["Hi", "Hello", "Hey", "Greetings",
             "Heyaa", "Howdy", "Aloha", "Hola", "Bonjour", "Ciao"]  # list of greetings

sentences = ["You talkin' to me?", "You talkin' 'bout me?",
             "\001ACTION rustles his jimmies. \001"]  # list of random sentences

refuse = ["NO", "Never", "Do it yourself.",
          "Lol, no"]  # list of refusals

# list of people not to greet when they log in
blacklist = ["corn", "flakes", "fett"]

# list used to identify compliments
compliment = ["good", "smart", "clever"]

suggestions = ["I really like this song", "How about this song",
               "Someone told me that this is a good piece of music"]

music = ["https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=BEwNrjvNiYs", "https://www.youtube.com/watch?v=eONClyzrhzI&feature=youtu.be", "https://www.youtube.com/watch?v=LMPWfHqVj40&feature=youtu.be", "https://www.youtube.com/watch?v=uFQrgNyiYwQ", "https://www.youtube.com/watch?v=qd4KMK8c3x0", "https://www.youtube.com/watch?v=MxHGyqobsbI&feature=youtu.be", "https://www.youtube.com/watch?v=RcZn2-bGXqQ", "https://youtu.be/jdYJf_ybyVo", "https://youtu.be/Wqn-7ZkYUYM",
         "https://www.youtube.com/watch?v=Z_DhNLCyVss", "https://www.youtube.com/watch?v=1GKXaC4SrF8", "https://www.youtube.com/watch?v=ihTABU6t8IU", "https://www.youtube.com/watch?v=VnT7pT6zCcA&feature=youtu.be", "https://www.youtube.com/watch?v=zNcsBf2GCFc", "https://youtu.be/EAtBki0PsC0", "https://www.youtube.com/watch?v=pYb8ux67W2E", "https://www.youtube.com/watch?v=7ztvgT4aV-8", "https://www.youtube.com/watch?v=iC65ufGUvKM", "https://www.youtube.com/watch?v=XAg5KjnAhuU", "https://www.youtube.com/watch?v=3vC5TsSyNjU"]


def sendmsg(msg, channel=""):
    """
    This function is responsible for sending messages to the IRC stream
    """

    if channel == "":  # select the correct channel to answer to.
        channel = text.split()[2]
    if channel == botnick:  # correctly answer to pm's
        channel = text.split("!")[0].strip(":")

    try:
        irc.send("PRIVMSG " + channel + " :" +
                 msg + "\n")
        # msg.encode('utf-8', 'ignore')
        print(botnick + ": " + channel + " " + msg)
    except:
        pass


def action(msg, channel=""):
    """
    This function sends an action
    """
    if channel == "":
        channel = text.split()[2]
    sendmsg("\001ACTION " + msg + "\001", channel)


def sendpm(name, msg):
    """
    This function sends a pm
    """
    irc.send("PRIVMSG " + name + " :" + msg + "\n")
    print(botnick + ": " + name + " " + msg)


def sleepwatch():
    """
    This function puts the bot to sleep, it won't respond to other commands anymore
    """
    if "!sleep" in text:
        global sleep
        sleep = True
        sendmsg("Zzzzzzz")
    if "!corn_on" in text:
        global corn_mode
        corn_mode = True
        sendmsg("I will stop doing things without it being asked")


def wakewatch():
    """
    This function wakes the bot up
    """
    if "!wake" in text:
        global sleep
        sleep = False
        sendmsg("I'm awake now.")
    if "!corn_off" in text:
        global corn_mode
        corn_mode = False
        sendmsg("I will resume cheering and waving!")


def changechannel(channel=""):
    """
    This function allows the bot to join and leave new channels
    """
    if channel != "":
        irc.send("JOIN " + channel + "\r\n")
    else:
        if ":!join" in text:  # join a new channel
            chan = text.split()[4]
            irc.send("JOIN " + chan + "\r\n")
            sendmsg('I joined the channel ' + chan)
        if ":!leave" in text:  # leave a channel
            chan = text.split()[4]
            irc.send("PART " + chan + "\r\n")


def changenick(nick="False"):
    """
    This function changes the nick of the bot
    """
    global botnick
    if ":!nick" in text:
        try:
            botnick = text.split()[4]
            irc.send("NICK " + botnick + "\n")
        except:
            sendmsg(
                "The correct use for this command is: !nick <new nick>")
    elif nick != "False":
        botnick = nick
        irc.send("NICK " + botnick + "\n")


def greetingwatch():
    """
    This function is responsible for greeting people
    """
    greetings2 = greetings
    name = text.split("!")[0].strip(":")
    for i in greetings:
        if text.lower().find(i.lower() + " " + botnick.lower()) != -1 or text.lower().find(i.lower() + ", " + botnick.lower()) != -1:
            sendmsg(random.choice(
                greetings2) + " " + name)
    # if text.find("JOIN") !=-1 and text.lower().find(botnick.lower()) == -1 and text.find(":!") == -1:
        # for nick in blacklist:
        #  if text.lower().find(nick) == -1:
            #    name = text.split("!")[0].strip(":")
            #     if text.lower().find("slymodi") != -1:
            #       irc.send("PRIVMSG "+ channel +" :"+ "All hail Sly Mo Di!" +"\n")
            #    else:
            #     irc.send("PRIVMSG "+ channel +" :"+ random.choice(greetings2) + " " + name +"\n")


def textwatch():
    """
    This function looks for general chat triggers and reacts to them
    """
    name = text.split("!")[0].strip(":")
    global cheercount
    global hailcount
    global wavecount
    if corn_mode is False:
        # responding to waving
        if text.find("o/") != -1 and text.find("\o/") == -1 and text.find("/o/") == -1:
            if wavecount < 1:
                sendmsg("o/")
            wavecount += 1
            if wavecount == 4:  # reset counter
                wavecount = 0

        if text.lower().find("ciao") != -1:  # respond to ciao
            sendmsg("Ciao " + name)

        if text.find("\o/") != -1:  # respond to cheering
            if cheercount < 1:
                sendmsg("\o/")
            cheercount += 1
            if cheercount == 4:
                cheercount = 0

        if text.lower().find("all hail") != -1:  # respond to hailing
            if hailcount < 1:
                sendmsg("All hail! /o/")
            hailcount += 1
            if hailcount == 4:
                hailcount = 0

    if text.lower().find(botnick.lower()) != -1 and text.find("sing") != -1 and text.find("song") != -1 or text.find("!sing") != -1:  # lets the bot sing a song
        sendmsg("It's called Daisy.")
        sendmsg("Daisy ... Daisy ...")
        sendmsg("Give me your answer, do.")
        sendmsg("I'm half crazy ...")
        sendmsg("all for the love of you.")

    # makes the bot respond to his name
    if text.lower().find(botnick.lower() + "?") != -1:
        sendmsg(random.choice(sentences))

    if text.lower().find(botnick.lower()) != -1 and text.find("tell") != -1 and text.find("telling") == -1:  # make the bot tell things
        if text.find("tell") > text.lower().find(botnick.lower()):
            name1 = text.split()[5]
            message_list = text.split()[6:]
            message = " ".join(message_list)
            sendmsg(name1 + ", " + name +
                    " wanted me to tell you " + "'" + message + "'")
        else:
            pass

    if text.lower().find(botnick.lower()) != -1 and text.find("give") != -1 and text.find("gives") == -1:  # make the bot give things
        name1 = text.split()[5]
        message_list = text.split()[6:]
        message = " ".join(message_list)
        final_message = message.replace(
            "me ", name)
        sendmsg("\001ACTION" + " gives " + name1.replace("me",
                                                         name) + " " + final_message + "\001")

    if text.lower().find(botnick.lower()) != -1 and text.find("fetch") != -1 and text.find("fetches") == -1:  # make the bot fetch things
        name1 = text.split()[5]
        message_list = text.split()[6:]
        message = " ".join(message_list)
        final_message = message.replace(
            "me ", name)
        sendmsg("\001ACTION" + " fetches " +
                name1.replace("me", name) + " " + final_message + "\001")

    if text.lower().find(botnick.lower()) != -1 and text.find("bring") != -1 and text.find("brings") == -1:  # make the bot bring things
        name1 = text.split()[5]
        message_list = text.split()[6:]
        message = " ".join(message_list)
        final_message = message.replace(
            "me ", name)

        sendmsg("\001ACTION" + " brings " +
                name1.replace("me", name) + " " + final_message + "\001")

    if text.lower().find(botnick.lower()) != -1:
        for i in compliment:
            if text.lower().find(i) != -1 and name.lower().find(i) == -1:  # response to compliments
                sendmsg(":D Thanks " + name)

    if text.lower().find(botnick.lower()) != -1 and text.find("countdown") != -1 or text.find("!countdown") != -1:  # final countdown
        sendmsg(
            "3 ... 2 ... 1 | https://www.youtube.com/watch?v=9jK-NcRmVcw&gl=BE")

    if text.lower().find(botnick.lower()) != -1 and text.find("update") != -1 and text.find("where") != -1 or text.find("!update") != -1:  # update song
        sendmsg(
            "Wup-date, wup-date ヾ(⌐■_■)ノ♪ | https://www.youtube.com/watch?v=I8jkz0pdHk8")

    if text.lower().find("!work") != -1:  # BACK TO WORK
        original_nick = botnick
        changenick("RedHotBalrog")
        sendmsg(
            "BACK TO WORK! | http://wowimg.zamimg.com/hearthhead/sounds/VO_EX1_603_Play_01.mp3")
        sendmsg("\001ACTION cracks whip \001")
        changenick(original_nick)

    if text.lower().find("thank") != -1 and text.lower().find(botnick.lower()) != -1 and text.find("tell") == -1 and text.find("say") == -1:  # responding to people thanking the bot
        sendmsg("You're welcome " + name)

    if text.lower().find(botnick.lower()) != -1 and text.lower().find("make") != -1 and text.find("tell") == -1 and text.find("say") == -1:  # sudo make me a sandwich
        if text.lower().find("sudo") != -1:
            message_list = text.split()[6:]
            message = " ".join(message_list)
            sendmsg("\001ACTION makes " +
                    message.replace("me", name) + "\001")
        else:
            sendmsg(random.choice(refuse))

    if text.lower().find(botnick.lower()) != -1:  # respond with bot info
        if text.lower().find("who is") != -1 or text.lower().find("who are you") != -1:
            sendmsg("I'm " + botnick +
                    " and I'm a bot made by Cha0zz. | https://github.com/Cha0zz/Jimmy")
            sendmsg("Use !help for a list of available commands.")

    if text.find("!identify") != -1:
        sendmsg("I'm " + botnick +
                " and I'm a bot made by Cha0zz. | https://github.com/Cha0zz/Jimmy")
        sendmsg("Use !help for a list of available commands.")

    if text.lower().find(botnick.lower()) != -1 and text.find("why") != -1:  # shrug
        sendmsg("¯\_(ツ)_/¯")

    if text.lower().find(botnick.lower() + " say") != -1 or text.lower().find(botnick.lower() + ", say") != -1:  # let the bot say things
        message_list = text.split()[5:]
        message = " ".join(message_list)
        sendmsg(message)

    if text.lower().find(botnick.lower()) != -1 and text.lower().find("poke") != -1:  # poke back
        sendmsg("\001ACTION pokes " +
                name + " back \001")

    # Choose something out of a given list
    if text.lower().find(botnick.lower() + " choose") != -1 or text.find(":!choose") != -1:
        if text.find("Cha0zz") != -1 and text.find("Cha0zz!") == -1:
            message_list = ["Cha0zz for he is my master.",
                            "Cha0zz", "My master, Cha0zz"]
        elif text.find(" or") == -1:
            message_list = text.split(",")[1:]
            if text.find(":!choose") == -1:
                message_list.append(
                    text.split()[5].strip(","))
            else:
                message_list.append(
                    text.split()[4].strip(","))
        else:
            message_list = text.split(" or")[1:]
            if text.find(":!choose") == -1:
                message_list.append(
                    text.split()[5])
            else:
                message_list.append(
                    text.split()[4])
        try:
            print(message_list)
            sendmsg(random.choice(message_list).lstrip(" "))
        except:
            sendmsg(
                'Use "," or "or" to separate the possible choices.')

    if text.find("!no") != -1 and text.find("node") == -1:  # NOOOOOOOO
        sendmsg(
            "Noooooo | http://www.nooooooooooooooo.com")

    if text.lower().find(botnick.lower()) != -1 and text.find("stay") != -1 and text.find("alive") != -1:  # stayin' alive
        sendmsg(
            "Ha-Ha-Ha-Ha, stayin' alive | https://www.youtube.com/watch?v=I_izvAbhExY")

    if text.lower().find("taiya") != -1 and text.find("dance") != -1 and text.lower().find(":taiya!") == -1:  # dancing queen
        sendmsg(
            "Taiya, you are my dancing queen. | https://www.youtube.com/watch?v=xFrGuyw1V8s")

    if text.lower().find("who let the dogs out") != -1:  # who let the dogs out
        sendmsg(
            "Woof, woof, woof, woof | https://www.youtube.com/watch?v=Qkuu0Lwb5EM")

    if text.lower().find(botnick.lower()) != -1 and text.find("eggs") != -1 and text.find("dozen") != -1:  # how many eggs go in a dozen
        sendmsg(
            "12 (－‸ლ) | https://www.youtube.com/watch?v=fwSYoj5E5JQ")

    if text.find("!bed") != -1:  # BACK TO BED
        original_nick = botnick
        changenick("SleepyBalrog")
        sendmsg("BACK TO BED!")
        sendmsg("\001ACTION cracks pillow \001")
        changenick(original_nick)

    if text.lower().find("jimmy") != -1 and text.find("what is your nick") != -1:  # relay botnick
        sendmsg(botnick)

    if text.lower().find(botnick.lower()) != -1 and text.lower().find("answer") != -1 and text.lower().find("what") != -1:
        sendmsg("That's easy, obviously the answer is 42.")

    if "!pudding" in text:
        pudding_list = ["PUDDING", "pudding", "PuDdInG"]
        sendmsg(random.choice(pudding_list))

    if text.lower().find("idiot") != -1:
        sendmsg("Idiots, idiots everywhere.")

    if text.lower().find("what is the meaning of life") != -1 or text.lower().find("what's the meaning of life") != -1:
        sendmsg("42")


def helpwatch():
    """
    This function looks for the help command
    """
    commands_str = ", ".join(
        str(i) for i in commands)

    helplist = ["add", "remove", "music", "join", "leave", "nick"]
    if "!help" in text:

        # for item in helplist:
            # if not item in text:
                # sendmsg("Help document not implemented.")

        if "pmusic" in text:
            sendmsg(
                "Play music from your personal or someone else's library. | !pmusic <opt: person>")
        elif "padd" in text:
            sendmsg("Add music to your personal library | !padd <link>")
        elif "premove" in text:
            sendmsg(
                "Remove music from your personal library | !premove <link>")
        elif "psongcount" in text:
            sendmsg(
                "This function shows the amount of songs in your personal library.")
        elif "songcount" in text:
            sendmsg(
                "This function shows the amount of songs in the general library.")
        elif "add" in text:
            sendmsg("This function adds music to " +
                    botnick + "'s music library. | !add <link>")
        elif "remove" in text:
            sendmsg("This function adds music to " +
                    botnick + "'s music library. | !remove <link>")
        elif "music" in text:
            sendmsg("This function plays music from " +
                    botnick + "'s music library. | !music")
        elif "join" in text:
            sendmsg("This function makes " + botnick +
                    " join a channel | !join <#channel>")
        elif "leave" in text:
            sendmsg("This function makes " + botnick +
                    " leave a channel | !leave <#channel>")
        elif "nick" in text:
            sendmsg("This function changes " + botnick +
                    "'s username | !nick <newnick>")
        elif "sleep" in text:
            sendmsg(
                "This function puts " + botnick + " to sleep, he won't respond to you anymore until he is awakened with '!wake' | !sleep")
        elif "wake" in text:
            sendmsg("This function awakens " + botnick +
                    " so that he starts responding again. | !wake")
        elif "choose" in text:
            sendmsg("Makes " + botnick +
                    " choose an item from a given list, separate items with ',' or 'or' | !choose <options>")
        elif "corn_on" in text:
            sendmsg("Prevents " + botnick +
                    " from doing things without it being asked such as greeting and waving.")
        elif "corn_off" in text:
            sendmsg("Disables corn_on mode.")
        elif "youtube" in text:
            sendmsg(
                "Search youtube for the given query | !youtube <search>")
        elif "wiki" in text:
            sendmsg(
                "Search wikipedia for the given query | !wiki <search>")
        elif "google" in text:
            sendmsg(
                "Search google for the given query | !google <search>")
        elif "image" in text:
            sendmsg(
                "Search google images for a given query | !image <search>")
        elif "roll" in text:
            sendmsg("Rolls a dice | !roll <AdX>")
        elif "plist" in text:
            sendmsg(
                "Shows all the songs in your personal library | !plist <opt: name>")
        elif "sing" in text:
            sendmsg(botnick + " sings a song.")
        elif "moon" in text:
            sendmsg("Gives the current moon-phase")
        elif "weather" in text:
            sendmsg(
                "Gives the weather for a location | !weather <location>")
        elif "urban" in text:
            sendmsg("Searches the urban dictionairy | !urban <query>")
        elif "dict" in text:
            sendmsg(
                "Searches a dictionairy for a definition | !dict <query>")
        elif "identify" in text:
            sendmsg("Gives information about the bot.")
        else:
            sendmsg(
                "The available commands are " + commands_str)
            sendmsg(
                "For info about a specific command use '!help <command>' (without the '!' infront of the command)")

    elif text.lower().find(botnick.lower()) != -1 and text.lower().find("help") != -1:
        sendmsg(
            "The available commands are " + commands_str)
        sendmsg("for info about a specific command use '!help <command>'")


def quitwatch():
    """
    This function lets the bot leave the IRC stream
    """
    name = text.split("!")[0].strip(":")
    if ":!quit" in text and text.find("Cha0zz@Cha0zz.user.gamesurge") != -1:
        sendmsg("I'm going, ciao.")
        irc.send("QUIT" + "\n")
    elif ":!quit" in text and text.find("Cha0zz@Cha0zz.user.gamesurge") == -1:
        if name == "Cha0zz":
            sendmsg("You're not the real Cha0zz.")
        else:
            sendmsg(
                "Only Cha0zz can tell me to quit.")


def musicwatch():
    """
    This function adds, removes and returns music from the music list.
    It also allows the bot to do simple youtube searches
    """
    name = text.split("!")[0].strip(":")
    songcount = len(array)

    # add music to your personal library
    if text.find("!add") != -1 or text.find("!padd") != -1:
        song = text.split()[4]
        if text.find("!padd") != -1:
            if name not in pmusic:
                pmusic[name] = []
            if song in pmusic[name]:
                sendmsg(
                    "You already have that song in your personal library " + name)
            else:
                pmusic[name].append(song)
                f2 = open(
                    '/users/jasperdelaey/documents/workspace/bot/personalsavefile', 'wb')
                pickle.dump(pmusic, f2)
                f2.close()
                sendmsg(
                    "I added the song to your personal library " + name)

        try:
            a = urllib.urlopen(song)
            code = a.getcode
            if song in array:
                sendmsg(
                    "I already have that song in my list.")
            elif name in nopelist:
                sendmsg(
                    "I don't take links from you " + name)
            elif code == 404:
                sendmsg(
                    "Please provide a valid link.")
            elif 'youtu' in song and "http" in song:
                array.append(song)
                f = open(
                    '/users/jasperdelaey/documents/workspace/bot/savefile', 'wb')
                pickle.dump(array, f)
                f.close()
                sendmsg("I added the song to my music list.")
            else:
                sendmsg(
                    "Please provide your music as a youtube link.")
        except:
            sendmsg(
                "Please provide a valid link.")

    if text.find("!pmusic") != -1:  # get music from someon else's personal library
        try:
            name1 = text.split()[4]
            if name1 not in pmusic:
                sendmsg(
                    "This person doesn't has any music in their personal library.")

            link = random.choice(pmusic[name1])
            youtube = etree.HTML(urllib.urlopen(link).read())
            video_title = " ".join(youtube.xpath(
                "//span[@id='eow-title']/@title"))
            sendmsg(video_title + " | " +
                    link)

        except:
            link = random.choice(pmusic[name])
            youtube = etree.HTML(urllib.urlopen(link).read())
            video_title = " ".join(youtube.xpath(
                "//span[@id='eow-title']/@title"))
            sendmsg(video_title + " | " +
                    link)

    if text.find("!remove") != -1:  # remove a song from the songlist
        if text.find("https://www.youtube.com/watch?v=dQw4w9WgXcQ") != -1:
            sendmsg("I'm sorry " + name +
                    " I'm afraid I can't do that.")
        else:
            try:
                song = text.split()[4]
                array.remove(song)
                f = open(
                    '/users/jasperdelaey/documents/workspace/bot/savefile', 'wb')
                pickle.dump(array, f)
                f.close()
                sendmsg("I removed the song from my music list.")
            except:
                sendmsg(
                    "I couldn't remove that song, make sure that you provide the correct link.")

    if text.find("!premove") != -1:  # remove music from your personal library
        try:
            song = text.split()[4]
            pmusic[name].remove(song)
            f2 = open(
                '/users/jasperdelaey/documents/workspace/bot/personalsavefile', 'wb')
            pickle.dump(pmusic, f2)
            f2.close()
            sendmsg(
                "I removed the song from your personal library " + name)
        except:
            sendmsg(
                "I couldn't remove that song, make sure that you provide the correct link.")

    if text.find("!songcount") != -1:  # amount of songs in the global library
        sendmsg("I currently have " + str(songcount) +
                " songs in my music library.")

    if text.find("!psongcount") != -1:
        try:
            psongcount = len(pmusic[name])
            sendmsg("I currently have " + str(psongcount) +
                    " songs in your personal library " + name)
        except:
            sendmsg("I couldn't find any music in your personal library.")

    if text.lower().find(botnick.lower()) != -1 and text.lower().find("music") != -1 or text.find("!music") != -1:  # give music out of the music list
        if "add" in text:
            sendmsg(
                "The correct command to add music to the music list is '!add <music-url>'")
        link = random.choice(array)
        youtube = etree.HTML(urllib.urlopen(link).read())
        video_title = " ".join(youtube.xpath(
            "//span[@id='eow-title']/@title"))
        sendmsg(video_title + " | " + link)

    if text.find("!youtube") != -1 or text.find("!yt") != -1 or text.find("!video") != -1 or text.find("!y ") != -1:  # searches youtube
        try:
            string = text[text.find("!y"):]
            search = string[string.find(" ") + 1:].rstrip("\n")
            result_list = []
            # search_list = text.split()[4:]
            # search = " ".join(search_list)
            search_query = urllib.urlencode({"search_query": search})
            url = "http://www.youtube.com/results?" + search_query
            response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html)
            for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
                result_list.append(
                    "http://www.youtube.com" + vid['href'])
            # prevents from returning a user instead of a video
            if "/user/" in result_list[0]:
                link = result_list[1]
            else:
                link = result_list[0]
            youtube = etree.HTML(urllib.urlopen(link).read())
            video_title = " ".join(youtube.xpath(
                "//span[@id='eow-title']/@title"))
            sendmsg(video_title.encode('utf-8', 'ignore') +
                    " | " + link.encode('utf-8', 'ignore'))
        except:
            sendmsg(error)

"""
    if "!plist" in text:  # send a list of all the music in the personal library
        try:
            name1 = text.split()[4]
            if name1 not in pmusic:
                sendmsg(
                    "This person doesn't has any music in their personal library.")
            music_list = ", ".join(pmusic[name1])
            sendpm(name, music_list)
        except:
            music_list = ", ".join(pmusic[name])
            sendpm(name, music_list)
"""


def wikiwatch():
    """
    Search wikipedia
    """
    try:
        if text.find("!wiki") != -1 or text.find("!wikipedia") != -1 or text.find("!w ") != -1:
            string = text[text.find("!w"):]
            search = string[string.find(" ") + 1:].rstrip("\n")
            search_list = text.split()[4:]
            # search = " ".join(search_list)
            summary = wikipedia.summary(search, sentences=2)
            if len(summary) > 430:
                summary = summary[0:430] + "..."
            # print(summary)
            page = wikipedia.page(search)
            title = page.title
            url = page.url
            sendmsg(title + " | " + url)
            try:
                sendmsg(summary.encode('utf-8', 'ignore'))
            except:
                sendmsg(
                    "fix this when you have the time, probably to do with non-unicode characters.")
    except:
        try:
            search_list = text.split()[4:]
            search = " ".join(search_list)
            lookup = wikipedia.search(search, results=5)
            # page = wikipedia.page(lookup[0])
            # title = page.title
            url = "https://en.wikipedia.org/wiki/" + \
                lookup[0].replace(" ", "+")
            sendmsg(
                "I'm not sure what you mean, this is what I could find. | " + url)
        except:
            sendmsg(error)


def googlewatch():
    """
    This function searches google or google images for a given query.
    """
    try:
        if text.find("!google") != -1 or text.find("!g ") != -1:  # search google
            string = text[text.find("!g"):]
            search = string[string.find(" ") + 1:].rstrip("\n")
            search_list = text.split()[4:]
            # search = " ".join(search_list)
            search_query = urllib.urlencode({'q': search})
            response = urllib2.urlopen(
                "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&" + search_query).read()
            data = json.loads(response)
            results = data['responseData']['results']
            result = results[0]
            title = result['title'].replace(
                "<b>", "").replace("</b>", "")
            url = result['url']
            if url.find("watch%") != -1:  # circumvent google bot detection
                url = url.replace("watch%3Fv%3D", "watch?v=")
            sendmsg(title.encode('utf-8', 'ignore') + " | " + url)
    except:
        sendmsg(error)

    if "!image" in text or "!img" in text or "!i " in text:
        # With help of:
        # https://github.com/creeveshft/Web_Scraping/blob/master/Google%20Image%20Searcher/getimage.py
        url_list = []
        answer_list = []
        max_amount = "3"
        k = 0

        sentence = text.split()

        string = text[text.find("!i"):]

        for word in sentence:
            if word[1].isdigit and word[0] == "x":
                if len(word) > int(max_amount) + 1 or int(word[1]) > int(max_amount):
                    amount = 3
                    sendmsg(
                        "The maximum amount of allowed images is 3.")
                else:
                    amount = int(word[1])

                string = string.replace(word, "")
            else:
                amount = 1

        search = string[string.find(" ") + 1:].rstrip("\n")
        search_query = urllib.urlencode({'q': search})

        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'Mozilla')]

        html = browser.open(
            "https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1414&bih=709&" + search_query + "&o" + search_query)
        # html = urllib.urlopen("https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1414&bih=709&q="+search+"&oq="+search).read()

        soup = BeautifulSoup(html)
        # print(soup)
        results = soup.findAll("a")
        # print(results)
        for i in results:
            # print(i)
            i = str(i)
            # if "imgres?imgurl" in i:
            #start = i.find("imgres?imgurl") + len("imgres?imgurl")
            #end = i.find("jsaction",start)
            # url_list.append(i[start:end])
            if "src=" in i:
                start = i.find("src=") + 5
                end = i.find("width=") - 2
                url_list.append(i[start:end])

        # print(url_list)

        while k < amount:
            answer_list.append(url_list[k])
            k += 1

        answer = " | ".join(answer_list)

        sendmsg("This is what I could find | " + answer)

    """
    if "!image" in text or "!img" in text or "!i " in text:
        keyBing = ""
        credentialBing = 'Basic ' + \
            (':%s' % keyBing).encode('base64')[:-1]
        search_list = text.split()[4:]
        search = " ".join(search_list)
        searchString = urllib.urlencode({'Query': search})
        # searchString = urllib.urlencode({"Query", search})
        url = "https://api.datamarket.azure.com/Bing/Search/v1/Image?" + \
            searchString + "%27&$top=5&$format=json"
        request = urllib2.Request(url)
        request.add_header('Authorization', credentialBing)
        print(request)
        request_opener = urllib2.build_opener()
        response = request_opener.open(request)
        response_data = response.read()
        result = json.loads(response_data)
        print(result)
    """

    """
    try:
        if text.find("!image") != -1 or text.find("!img") != -1:  # search google images
            search_list = text.split()[4:]
            if "x2" in search_list:
                search_list.remove("x2")
            if "x3" in search_list:
                search_list.remove("x3")
            search = " ".join(search_list)
            search_query = urllib.urlencode({'q': search})
            response = urllib2.urlopen(
                "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&" + search_query).read()
            data = json.loads(response)
            results = data['responseData']['results']
            result1 = results[0]
            result2 = results[1]
            result3 = results[2]
            title1 = result1['title'].replace(
                "<b>", "").replace("</b>", "")
            title2 = result2['title'].replace(
                "<b>", "").replace("</b>", "")
            title3 = result3['title'].replace(
                "<b>", "").replace("</b>", "")
            url1 = result1['url']
            url2 = result2['url']
            url3 = result3['url']
            # title_filtered = ''.join(
            # filter(lambda x: x in string.printable, title))
            if "x3" in text:
                sendmsg(url1.encode('utf-8', 'ignore') +
                        " | " + url2.encode('utf-8', 'ignore') + " | " + url3.encode('utf-8', 'ignore'))

            elif "x2" in text:
                sendmsg(url1.encode('utf-8', 'ignore') +
                        " | " + url2.encode('utf-8', 'ignore'))

            else:
                sendmsg(title1.encode('utf-8', 'ignore') +
                        " | " + url1.encode('utf-8', 'ignore'))
    except:
        sendmsg("Google discontinued its ajax api :(")
    """


def dicewatch():  # !roll 5d10
    """
    this function rolls dice
    """
    name = text.split("!")[0].strip(":")
    if "!roll" in text:
        try:
            roll_list = []
            roll_list_int = []
            i = 0
            max_dice = 20
            max_side = 1000
            dice = text.split()[4]
            dice_split = dice.split("d")
            dice_count = int(dice_split[0])
            side_count = int(dice_split[1])
            if dice_count > max_dice:
                sendmsg("You can only roll " +
                        str(max_dice) + " die at a time.")
            elif side_count > max_side:
                sendmsg("You can only roll die with max " +
                        str(max_side) + " sides.")
            else:
                while i < dice_count:
                    roll = random.randrange(1, side_count + 1)
                    roll_list.append(str(roll))
                    roll_list_int.append(roll)
                    i += 1
                sum_of_list = sum(roll_list_int)
                roll_str = ", ".join(roll_list)
                sendmsg(name + " rolled " + roll_str +
                        " | total: " + str(sum_of_list))
        except:
            sendmsg("This isn't in yet, blame my master Cha0zz.")


def overridewatch():
    """
    Makes the bot only listen to Cha0zz
    """
    name = text.split("!")[0].strip(":")
    if ":!override" in text and text.find("Cha0zz@Cha0zz.user.gamesurge") != -1:
        global override
        if override is True:
            override = False
            sendmsg("Override disabled.")
        else:
            override = True


def REKT():
    """
    Rekt stuff
    """
    map_list = ["http://i.imgur.com/eupMU6w.png",
                "http://i.imgur.com/UXsCSEh.jpg"]
    if "!map" in text:
        map_info = text.split()[4:]
        map_nr = int(map_info[1])
        try:
            if "mission" in text:
                sendmsg("This is the map of mission " +
                        str(map_nr) + " | " + map_list[map_nr - 1])
            else:
                sendmsg("I currently only have mission maps.")
        except:
            sendmsg(error)


def pm():
    if "!pm" in text and "!pmusic" not in text:
        name = text.split()[4]
        msg = " ".join(text.split()[5:])
        sendpm(name, msg)


def weather():
    """
    get weather and stuff
    """
    if text.find("!weather") != -1:  # gets the weather for a given location
        try:
            string = text[text.find("!w"):]
            location = string[string.find(" ") + 1:].rstrip("\n")
            # location = " ".join(text.split()[4:])
            lookup = pywapi.get_location_ids(location)
            for i in lookup:
                location_id = i
            weather_com_result = pywapi.get_weather_from_weather_com(
                location_id)
            temperature = weather_com_result[
                "current_conditions"]["temperature"]
            weather_text = weather_com_result[
                "current_conditions"]["text"]
            wind_direction = weather_com_result[
                "current_conditions"]["wind"]["text"]
            wind_speed = weather_com_result[
                "current_conditions"]["wind"]["speed"]
            place = weather_com_result["location"]["name"]
            sendmsg(place + " | " + weather_text + " | " + temperature +
                    " C | " + wind_speed + " km/h " + wind_direction + " wind")
        except:
            sendmsg(error)

    if text.find("!moon") != -1:  # gets the current moonphase
        try:
            location = "new york"
            lookup = pywapi.get_location_ids(location)
            for i in lookup:
                location_id = i
            weather_com_result = pywapi.get_weather_from_weather_com(
                location_id)
            moon = weather_com_result[
                "current_conditions"]["moon_phase"]["text"]
            if moon.lower() == "new moon":
                moon += " | " + u"\U0001F311"
            elif moon.lower() == "waxing crescent":
                moon += " | " + u"\U0001F312"
            elif moon.lower() == "first quarter":
                moon += " | " + u"\U0001F313"
            elif moon.lower() == "waxing gibbous":
                moon += " | " + u"\U0001F314"
            elif moon.lower() == "full moon":
                moon += " | " + u"\U0001F315"
            elif moon.lower() == "waning gibbous":
                moon += " | " + u"\U0001F316"
            elif moon.lower() == "last quarter":
                moon += " | " + u"\U0001F317"
            elif moon.lower() == "waning crescent":
                moon += " | " + u"\U0001F318"
            sendmsg(unicode(moon).encode('utf-8', 'ignore'))
        except:
            sendmsg(error)

"""
def urban():
    if text.find("!urban") != -1:
        try:
            search = " ".join(text.split()[4:])
            result = urbandict.define(search)
            definition = str(result[0]['def']).replace(
                "\n", " ").lstrip(" ")
            if len(definition) > 430:
                definition = definition[0:430] + "..."
            sendmsg(definition)
        except:
            sendmsg(error)
"""


def urban2():
    """
    lookup stuff in the urban dictionary, now without library.
    """
    if "!urban" in text or "!u " in text:
        try:
            string = text[text.find("!u"):]
            search = string[string.find(" ") + 1:].rstrip("\n")
            name = text.split("!")[0].strip(":")
            # search = " ".join(text.split()[4:])
            search_query = urllib.urlencode({'term': search})
            url = "http://www.urbandictionary.com/define.php?" + search_query
            response = urllib.urlopen(url).read().replace(
                "<br/>", " ").replace("\n", "").replace("&gt;", ">")
            start = int(response.find("<div class='meaning'>")
                        ) + len("<div class='meaning'>")
            end = int(response.find("</div>", start))
            definition = " ".join(response[start:end].split())
            definition = re.sub(
                '\<.*?\>', '', definition).replace("&quot;", "'").replace("&#39;", "'")
            if len(definition) > 430:
                definition = definition[0:430] + "..."
            # sendmsg("This is what I could find | " + url)
            # sendmsg(definition)
            sendpm(name, "This is what I could find | " + url)
            sendpm(name, definition)
        except:
            sendmsg(error)


def lookup():
    """
    Look stuff up in a dictionary
    """
    if text.find("!dict") != -1 or text.find("!define") != -1 or text.find("!d ") != -1:
        try:
            string = text[text.find("!d"):]
            search = string[string.find(" ") + 1:].rstrip("\n")
            # search = " ".join(text.split()[4:])
            search_query = urllib.urlencode({'term': search})
            url = "http://www.dictionary.com/cgi-bin/dict.pl?" + search_query
            response = urllib2.urlopen(url).read()
            start = int(response.find(
                '<div class="def-content">')) + 25
            end = int(response.find("</div>", start))
            definition = response[start:end].replace("\n", "")
            definition = re.sub('\<.*?\>', '', definition)
            if len(definition) > 430:
                definition = definition[0:430] + "..."
            if "www.facebook.com" in definition:
                sendsmg("I'm not sure what you mean | " + url)
            else:
                if response.find("there's not a match on Dictionary.com.") != -1:
                    sendmsg("I couldn't find the requested word(s).")
                else:
                    sendmsg("This is what I could find | " + url)
                    sendmsg(definition)
        except:
            sendmsg(error)


def translate(language1="", language2="", sentence=""):
# https://glosbe.com/a-api
    if language1 == "" or language2 == "" or sentence == "":
        line = text[text.find("!t"):]
        line_list = line.split(" ")
        language1 = line_list[0]
        language2 = line_list[1]
        sentence = " ".join(line_list[2:])

    query = urllib.urlencode({"from" : language1, "dest": language2, "phrase": sentence, "format" : "json" })

    url = "https://glosbe.com/gapi/translate?" + query

    response = urllib2.urlopen(url).read()
    data = json.loads(response)

    translation = data["tuc"][0]["phrase"]["text"]
    meaning = data ["tuc"][0]["meanings"]["text"]

    sendmsg(translation)
    sendmsg(meaning)


def bot():
    """
    stuff handled by the bot
    """
    while 1:  # puts it in a loop
        global text
        global readbuffer
        received = irc.recv(4096)  # receive the text
        readbuffer = readbuffer + received
        temp = string.split(readbuffer, "\n")
        readbuffer = temp.pop()

        for text in temp:
            text = string.rstrip(text)
            text = string.split(text)
            text = " ".join(text)

            print(text)  # print text to console

            if text.find('PING') != -1:  # check if 'PING' is found
                # returnes 'PONG' back to the server
                # (prevents pinging out!)
                irc.send('PONG ' + text.split()
                         [1] + '\r\n')

            # if text.lower().find("to connect, type") != -1:
                # irc.send('PONG ' + text.split()
                #[1] + '\r\n')

            if connected is False:
                irc.send("JOIN " + channel + "\r\n")

            if sleep is False and override is False:
                changenick()
                textwatch()
                helpwatch()
                greetingwatch()
                changechannel()
                sleepwatch()
                musicwatch()
                wikiwatch()
                googlewatch()
                dicewatch()
                pm()
                # REKT()
                weather()
                # urban()
                urban2()
                lookup()
            wakewatch()
            quitwatch()
            overridewatch()

# put the listener/ bot in his own thread
thread.start_new_thread(bot, ())

while 1:
    """
    Stuff to send messages/ do stuff from the command line.
    """
    user_text = str(raw_input(""))
    try:
        if user_text.find("/channel") != -1:
            channel = user_text.split()[1]
        elif user_text.find("/join") != -1:
            chan = user_text.split()[1]
            changechannel(chan)
        elif user_text.find("/quit") != -1:
            irc.send("QUIT" + "\n")
        elif user_text.find("/me") != -1:
            msg = " ".join(user_text.split()[1:])
            action(msg, channel)
        elif user_text.find("/nick") != -1:
            nick = user_text.split()[1]
            changenick(nick)
        elif "/pm" in user_text:
            nick = user_text.split()[1]
            msg = user_text.split()[2:]
            sendpm(nick, msg)
        else:
            sendmsg(user_text, channel)
    except:
        pass
