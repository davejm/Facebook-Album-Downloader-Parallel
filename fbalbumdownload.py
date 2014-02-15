# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 19:56:02 2013

@author: David Moodie

Required modules: facebook-sdk, progressbar2
Optional: easygui (for GUI - quite unnecessary)

Written for Python 3
"""

import facebook
#from pprint import pprint
#import easygui as eg
import urllib, multiprocessing
import os, errno
from progressbar import ProgressBar
import re
from time import time
import argparse

def ensure_dir(path):
    """Create the necessary directory if not already created."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def download(source_url):
    """Asynchronously download pictures from source url."""

    d_url = source_url[0]
    d_albumname = source_url[1]
    d_uname = source_url[2]
    d_friend_id = source_url[3]
    dumplocation = source_url[4]
    
    d_filename = (d_url.split('/')[-1]).split("?")[0]
    d_filelocation  = (dumplocation + "/" + d_uname + "--" + d_friend_id + "/albums/" \
        + d_albumname + "/")
    ensure_dir(d_filelocation)
    urllib.request.urlretrieve(d_url, d_filelocation + d_filename)
        
class fbUser(object):
    """Class to handle target fb user's properties and albums."""    
    def __init__(self, uid):
        global GRAPH        
        self.uid = uid
        self.albums = GRAPH.get_connections(self.uid, "albums", \
            fields="name, id, count")['data']
        for album in self.albums[:]:
            if not "count" in album:
                self.albums.remove(album)
        self.name = GRAPH.get_object(self.uid, fields="name")['name']

def getOAUTH(file="oauthkey.txt"):
    with open(file, 'r') as key:
        return key.read()

def parseUser(useridorusername):
    if not useridorusername.isdigit():
        userselect = GRAPH.get_object(useridorusername, fields="id")['id']
    return userselect

def inputUserID(GRAPH, GUI):
    if GUI == False:
        userselect = input("Enter user's id / username to download albums: ")
    else:
        userselect = eg.enterbox("Enter user's id / username to download albums.", \
        "User Selection")
    userselect = parseUser(userselect)
    return userselect


if __name__ == '__main__':   
    
    GUI = False
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--oauthkey", help="Specify an oauthkey to use for authentication.")
    parser.add_argument("-u", "--user", help="Specify a user id or username to download albums from.")
    parser.add_argument("-d", "--directory", help="Output directory for album dumps. E.g. C:\dump (default: <curdir>/dump)")
    args = parser.parse_args()
    
    if args.oauthkey:
        OAUTHKEY = args.oauthkey
    else:
        OAUTHKEY = getOAUTH()
    #OAUTHKEY = ''
        
    if args.directory:
        DUMPLOCATION = args.directory
    else:
        DUMPLOCATION = "dump"
    
    GRAPH = facebook.GraphAPI(OAUTHKEY)
    
    if args.user:
        userselect = [parseUser(args.user)]
    else:
        userselect = [inputUserID(GRAPH, GUI)] #TODO: Implement multiple user album download
    
    for specifiedUser in userselect:
    
        USER = fbUser(specifiedUser) #Specify target fb user id
        print("Downloading " + USER.name + "'s albums.\n")
    
        choices = []
        for i in range(len(USER.albums) - 1):
            choices.append("Index :" + str(i) + ": " + USER.albums[i]['name'])
        
        ALBUMSTODOWNLOAD = []
        if GUI:
            try:
                ALBUMSTODOWNLOAD = eg.multchoicebox("", "", choices)
            except TypeError:
                print("No albums selected.")
                exit()
        else:
            for choice in choices:
                print(choice)
            albumindicies = input("\nType the indicies of the albums you would" \
                + " like to download separated by commas e.g. 1,2,4\n")
            albumindicies = albumindicies.split(",")
            ALBUMSTODOWNLOAD = [choices[int(i)] for i in albumindicies]
            
        
        
        ALBUMINDICIES = [int(x.split(":")[1]) for x in ALBUMSTODOWNLOAD]
        
        
        for index in ALBUMINDICIES:
            starttime = time()
            albumid = USER.albums[index]['id']
            albumname = USER.albums[index]['name'] + "--" + albumid
            albumname = re.sub('[:*?"<>| ]', '_', albumname)
            #albumpiccount = ALBUMS[index]['count']
            print("Saving album - " + albumname)
            
            pool = multiprocessing.Pool()
            source_urls = []
            albumpics = GRAPH.get_connections(albumid, "photos", \
                    fields="source", limit=5000)['data']
            
            
            for pic in albumpics:
                source_urls.append((pic['source'], albumname, USER.name, USER.uid, DUMPLOCATION))
            #pprint(source_urls) # DEBUG

            results = []
            piccounter = 1
            def picdownloaded(arg):
                """Increment the piccounter variable for use in progressbar."""
                global piccounter            
                piccounter += 1
            
            for x in source_urls:
                r = pool.apply_async(download, (x,), callback=picdownloaded)
                results.append(r)
            #Wait for now but will implement concurrent album downloads later
            albumpiccount = USER.albums[index]['count']
            with ProgressBar(maxval=albumpiccount) as progress:
                while piccounter < albumpiccount:
                    progress.update(piccounter)
            
            
    #        #Wait block only needed if no blocking code preventing end of prog
    #        #before the processes have finished downloading. (Blocking code in this
    #        case is the while loop within the with block of the progressbar.)
    #        for r in results:
    #            r.wait()
            
            #output.wait()
            duration = time() - starttime
            print("Download took: " + str(duration) + " seconds.\n")
        
        print("Finished all downloads.\n")
        tmp = input("Hit Enter to exit")
