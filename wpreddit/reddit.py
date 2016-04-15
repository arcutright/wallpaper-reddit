import json
import os
import random
import re
import sys
from PIL import Image
from urllib import request
from multiprocessing.dummy import Pool as ThreadPool

from wpreddit import config, connection, download

# in - string[] - list of subreddits to get links from
# out - string[], string[] - a list of links from the subreddits and their respective titles
# takes in subreddits, converts them to a reddit json url, and then picks out urls and their titles
def get_links():
    print("searching for valid images...")
    if config.randomsub:
        parsedsubs = pick_random(config.subs)
    else:
        parsedsubs = config.subs[0]
        for sub in config.subs[1:]:
            parsedsubs = parsedsubs + '+' + sub
    url = "http://www.reddit.com/r/" + parsedsubs + ".json?limit=" + str(config.maxlinks)
    config.log("Grabbing json file " + url)
    uaurl = request.Request(url, headers={'User-Agent': 'wallpaper-reddit python script'})
    response = request.urlopen(uaurl)
    content = response.read().decode('utf-8')
    try:
        data = json.loads(content)
    except (AttributeError, ValueError):
        print('Was redirected from valid Reddit formatting. Likely a router redirect, such as a hotel or airport.'
            'Exiting...')
        sys.exit(0)
    response.close()
    links = []
    titles = []
    for i in data["data"]["children"]:
        links.append(i["data"]["url"])
        titles.append(i["data"]["title"])
    return links, titles

def mass_download():
    numthreads = len(config.subs) if len(config.subs) < config.threads else config.threads
    try:
        if numthreads > 1:
            print('mass download using '+str(numthreads)+' threads')
            pool = ThreadPool(numthreads)
            pool.map(download_from_sub, config.subs)
            pool.close()
            pool.join()
        else:
            for sub in config.subs:
                download_from_sub(sub)
    except KeyboardInterrupt:
        sys.exit(1)
 
def download_from_sub(sub):
    # grabbing lots of extra links because many do not resolve
    url = "http://www.reddit.com/r/" + sub + ".json?limit=" + str(2*config.massdownload)
    print("Grabbing json file " + url)
    uaurl = request.Request(url, headers={'User-Agent': 'wallpaper-reddit python script'})
    response = request.urlopen(uaurl, timeout=3)
    content = response.read().decode('utf-8')
    try:
        data = json.loads(content)
    except (AttributeError, ValueError):
        print('Was redirected from valid Reddit formatting. Likely a router redirect, such as a hotel or airport.'
            'Exiting...')
        return False
    response.close()
    try:
        numValid = 0
        numInvalid = 0
        for i in data["data"]["children"]:
            if(numValid >= config.massdownload):
                break
            link = i["data"]["url"]
            title = i["data"]["title"]
            try:
                if is_valid_link(link) and download.download_image_and_save(link, title):
                    numValid += 1
                else:
                    numInvalid += 1
            except: 
                pass
    except KeyboardInterrupt:
        sys.exit(1)
    print('\tr/'+sub+' finished, downloaded '+str(numValid)+' failed '+str(numInvalid))
    return True

def choose_valid(links, numLinks = -1):
    if len(links) == 0:
        print("No links were returned from any of those subreddits. Are they valid?")
        sys.exit(1)
    if numLinks == -1:
        numLinks = len(links)
    valid_links = []
    for i, link in enumerate(links):
        if len(valid_links) > numLinks:
            break
        if(is_valid_link(link)):
            valid_links.append([link, i])
    return valid_links
    
def is_valid_link(link):
    if not (link[-4:] == '.png' or link[-4:] == '.jpg' or link[-5:] == '.jpeg'):
        if re.search('(imgur\.com)(?!/a/)', link):
            link = link.replace("/gallery", "")
            link += ".jpg"
    if connection.connected(link) and check_dimensions(link) and check_blacklist(link):
        return True
    else:
        return False

# in - string[] - list of links to check
# out - string, int - first link to match all criteria and its index (for matching it with a title)
# takes in a list of links and attempts to find the first one that is a direct image link,
# is within the proper dimensions, and is not blacklisted
def choose_first_valid(links):
    if len(links) == 0:
        print("No links were returned from any of those subreddits. Are they valid?")
        sys.exit(1)
    
    for i, origlink in enumerate(links):
        if config.randomlink:
            link = pick_random(links)
        else:
            link = origlink
        config.log("checking link # {0}: {1}".format(i, origlink))
        if not (link[-4:] == '.png' or link[-4:] == '.jpg' or link[-5:] == '.jpeg'):
            if re.search('(imgur\.com)(?!/a/)', link):
                link = link.replace("/gallery", "")
                link += ".jpg"
            else:
                continue
        if not (connection.connected(link) and check_dimensions(link) and check_blacklist(link)):
            continue

        def not_same_url(link):
            with open(config.walldir + '/url.txt', 'r') as f:
                currlink = f.read()
                if currlink == link:
                    if i < len(links) - 1:
                        return False
                    else:
                        print("current wallpaper is the most recent, will not re-download the same wallpaper.")
                        sys.exit(0)
                else:
                    return True

        if config.force_dl or not (os.path.isfile(config.walldir + '/url.txt')) or not_same_url(link):
            return link, i
    print("No valid links were found from any of those subreddits.  Try increasing the maxlink parameter.")
    sys.exit(0)

# in - string - link to check dimensions of
# out - boolean - if the link fits the proper dimensions
# takes a link and checks to see if the link will match the minimum dimensions
def check_dimensions(url):
    resp = request.urlopen(request.Request(url, headers={'User-Agent': 'wallpaper-reddit python script',
       'Range': 'bytes=0-16384'}), timeout=3)
    try:
        with Image.open(resp) as img:
            dimensions = img.size
            if dimensions[0] >= config.minwidth and dimensions[1] >= config.minheight:
                config.log("Size checks out for: " + url)
                return True
    except IOError:
        config.log("Image dimensions could not be read: " + url)
    return False

# in: a list of subreddits
# out: the name of a random subreddit
# will pick a random sub from a list of subreddits
def pick_random(subreddits):
    rand = random.randint(0, len(subreddits) - 1)
    return subreddits[rand]

# in - string - a url to match against the blacklist
# out - boolean - whether the url is blacklisted
# checks to see if the url is on the blacklist or not (True means the link is good)
def check_blacklist(url):
    with open(config.walldir + '/blacklist.txt', 'r') as blacklist:
        bl_links = blacklist.read().split('\n')
    for link in bl_links:
        if link == url:
            return False
    return True

# blacklists the current wallpaper, as listed in the ~/.wallpaper/url.txt file
def blacklist_current():
    if not os.path.isfile(config.walldir + '/url.txt'):
        print('ERROR: ~/.wallpaper/url.txt does not exist.'
            'wallpaper-reddit must run once before you can blacklist a wallpaper.')
        sys.exit(1)
    with open(config.walldir + '/url.txt', 'r') as urlfile:
        url = urlfile.read()
    with open(config.walldir + '/blacklist.txt', 'a') as blacklist:
        blacklist.write(url + '\n')
