#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import feedparser
import BeautifulSoup
import sys
import os
import argparse
import subprocess


# Constant


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()

DEBUG = 0
string_max = 50
# destdir = '~/Downloads'
destdir = os.path.expanduser('~/Downloads')

locations = {"h33t": {"url": "http://www.h33t.to",
                      "dl": "h33t.to/get/"},
             "tpb": {"url": "http://thepiratebay.org",
                     "dl": "http://torrents.thepiratebay.org"},
             "bitsnoop": {"url": "http://bitsnoop.com",
                          "dl": "http://torrage.com/torrent/.*?\.torrent"},
             "torrentfunk.com": {"url": "http://www.torrentfunk.com",
                                 "dl": "www.torrentfunk.com/tor/*.torrent"},
             "limetorrents.cc": {"url": "http://www.limetorrents.cc",
                                 "dl": "itorrents.org/torrent/"},
             "torrents.net": {"url": "http://www.torrents.net",
                              "dl": "www.torrents.net/down/*.torrent"},
             "vertor": {"url": "http://www.vertor.com",
                        "dl": "http://www.vertor.com/.*?mod=download.*?id="},
             "torlock": {"url": "www.torlock.com",
                         "dl": "www.torlock.com/tor/*.torrent"}

             }

# TODO
# torrentproject, torrentreactor use an other page to the download
# bitsnoop, tpb, kat are blocker


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    RED = '\033[31m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1;1m'

    def disable(self):
        self.HEADER = ''
        self.BLUE = ''
        self.GREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        self.BOLD = ''


def save_file(toSave, outputPath):
    """
    Save a webpage in a specified file
    """
    try:
        print('Writting')
        with open(outputPath, "w") as openedFile:
            openedFile.write(toSave)

        print("Torrent Saved: %s" % (outputPath))

        res = True

    except Exception as e:
        res = False
        print(e)

    return res


def gethref(page, toFind):
    """
    Seek the linj 'toFind' in the whole page 'page' et return
    the exact destination you're looking for.

    toFind: Url of the page to find
    page: Source code of the page where you want to find 'toFind'
    """

    if DEBUG:
        print("gethref(%s, %s)" % (toFind, page))

    soup = BeautifulSoup.BeautifulStoneSoup(page)
    urls = soup('a')  # 'urls' contain a list of <a href=''>...</a>

    match = (toFind in urls[0]['href'])
    i = 1
    while not(match) and i < len(urls):
        match = (toFind in urls[i]['href'])

        if DEBUG:
            print("match: %s pour link: %s" % (match, urls[i]['href']))

        i += 1
    else:
        match = False

    # link['href'] is what's it is after href='...'
    return urls[i]['href'] if match else False


def get_page(basePage, researchedUrl):
    """
    trackers: Contain the source code of the page
    destdir: Path of the destination directory
    title: Title of the torrent final file
    trackername: Name of the torrent site to output in the commandline
    baseurl: torrent site url
    linkmatcher: pattern of the link to download the torrent
    """

    pageUrl = gethref(basePage, researchedUrl)
    if pageUrl:
        # If gethref() found the correct url
        print('Entering: %s' % (pageUrl))
        res = urllib.urlopen(pageUrl).read()
        # Contain the source code of the page
    else:
        res = False
        # If the base page didn't contain the url we were looking for

    return res


def locationTesting(trackersPage, outputPath, title):
    """
    For each download locations specified in the dict 'locations', is tested
    and the result is yield (False if it didn't worked, else True)
    """

    for name in locations:
        res = False
        os.write(sys.stdout.fileno(), "trying %s... \n" % name)
        trackerPage = get_page(trackersPage, locations[name]['url'])
        if trackerPage:
            torrentFile = get_page(trackerPage, locations[name]['dl'])
            if torrentFile:
                res = save_file(torrentFile, outputPath)

        yield res

    print("Error: Torrent found in none of the locations")


def main(option, domain):
    search = option.search.replace(' ', '+')
#    torrentzPage = urllib.urlopen(domain + search).read()
    torrentzPage = urllib.urlopen(domain + '?q=' + search).read()
    feed = feedparser.parse(torrentzPage)
    item_num = feed["items"].__len__()
    if item_num == 0:
        print("Sorry, no torrents found.")
        sys.exit(0)

    for i in range(item_num):
        item = feed["items"][i]
        title = item['title'][:string_max]
        # à refaire avec .format() pour afficher les noms des torrents

        if item['title'].__len__() < string_max:
            title += (string_max-item['title'].__len__()) * ' '
        v = item['summary_detail']['value']
        # pattern matching de size, seeds & peers a la va-vite
        size = v['Size: '.__len__(): v.find("Seed")].strip()
        seeds = v[v.find("Seeds")+'Seeds: '.__len__(): v.find("Peer")]
        peers = v[v.find("Peers")+'Peers: '.__len__(): v.find("Hash")]
        if (option.team is None) or (option.team in title.lower()):
            printstr = "%d:\t%s \t\t (%s)" \
                + "S: " + bcolors.BOLD + bcolors.RED + "%s" + bcolors.ENDC \
                + " P: " + bcolors.BOLD + bcolors.GREEN + "%s" + bcolors.ENDC
            print(printstr % (i, title, size, seeds, peers))

    sys.stdout.write("Which torrent to retrieve ? (or q to quit) : ")
    torrent = sys.stdin.readline()

    if torrent.strip() == "q":
        print("Exiting the client.")
        sys.exit(0)

    trackerindex = feed['items'][int(torrent)]['link']
    trackerindex = trackerindex.replace("node21", "www.torrentz.com")
    # new modifiction on RSS urls -- 20100816
    title = feed['items'][int(torrent)]['title']
    title = title.replace(' ', '_').replace('/', '_')
    # formatting for saved torrent filename

    print("GET %s" % trackerindex)

    trackers = urllib.urlopen(trackerindex).read()
    # trackers var contain the source of the torrentz selectioned torrent page

    outputPath = destdir + '/' + title + '.torrent'
    outputPath = '/home/thomacer/Downloads/' + title + '.torrent'

    hit = False
    downloadLocationTest = locationTesting(trackers, outputPath, title)
    while hit is False and hit is not None:
        hit = next(downloadLocationTest, None)

    process = subprocess.Popen(('peerflix %s --mpv' % (outputPath)).split())
    output = process.communicate()[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str)
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Show more information the execution')
    parser.add_argument('-d', '--destdir', default='~/Downloads', type=str,
                        help='Destination of the downloaded torrent')
    parser.add_argument('-t', '--team', default=None, type=str,
                        help='')
    parser.add_argument('-n', '--no_verified', default=False,
                        action='store_true',
                        help='Option to do unverified search')

    option = parser.parse_args()
    DEBUG = option.verbose
    domain = 'https://www.torrentz.com'

    if option.no_verified:
        domain += '/feedP'
    else:
        domain += '/feed_verifiedP'

    main(option, domain)
