#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import bs4
import sys
import os
import argparse
import subprocess


# Constant

class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()

destdir = os.path.expanduser('~/Downloads')

locations = {"h33t": {"url": "http://www.h33t.to",
                      "dl": "h33t.to/get/"},
             "tpb": {"url": "http://thepiratebay.org",
                     "dl": "http://torrents.thepiratebay.org"},
             "isohunt": {"url": "http://isohunt.to",
                         "dl": "torrent.isohunt.to/download.php?id="},
             "torrentfunk.com": {"url": "http://www.torrentfunk.com",
                                 "dl": ".torrent"},
             "limetorrents.cc": {"url": "http://www.limetorrents.cc",
                                 "dl": "itorrents.org/torrent/"},
#             "torrents.net": {"url": "http://www.torrents.net",
#                              "dl": ".torrent"},
             "vertor": {"url": "http://www.vertor.com",
                        "dl": "?mod=download."},
             "torlock": {"url": "www.torlock.com",
                         "dl": ".torrent"}

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

    soup = bs4.BeautifulSoup(page)
    urls = soup.find_all('a')  # 'urls' contain a list of <a href=''>...</a>

    href = urls[0].get('href')
    if href is not None:
        match = (toFind in urls[0].get('href'))
    else:
        match = False
    i = 0

    while not(match) and i < (len(urls) - 1):
        i += 1

        if DEBUG:
            print(urls[i])

        href = urls[i].get('href')
        if href is not None:
            match = (toFind in href)

        if DEBUG:
            print("match: %s pour link: %s" % (toFind, urls[i].get('href')))

    # link['href'] is what's it is after href='...'
    return urls[i].get('href') if match else False


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
    torrentzPage = urllib.urlopen(domain + '?q=' + search).read()
    feed = bs4.BeautifulSoup(torrentzPage)
    feedTitle = feed.find_all('title')
    feedDescription = feed.find_all('description')

    print(bcolors.HEADER + feedTitle[0].get_text() + bcolors.ENDC)
    feedTitle.pop(0)
    print(bcolors.HEADER + feedDescription[0].get_text() + bcolors.ENDC)
    feedDescription.pop(0)

    item_num = len(feedTitle)

    if item_num == 0:
        print("Sorry, no torrents found.")
        sys.exit(0)

    for i in range(item_num):
        title = feedTitle[i].get_text()
        description = feedDescription[i].get_text().split()
        # We parse something like
        # <description>Size: 4780 MB Seeds: 27 Peers: 17 Hash:
        # a000000a00a0aaaa00aa0000a0aaa0a0000aa0aa </description>

        size = description[1]
        seeds = description[4]
        peers = description[6]

        print("{:3d}) {:50s}: Size: {:4s} MB Seeds: {:3s}  Peers: {:3s}".format(
            i,
            title if title < 50 else title[:50],
            size,
            bcolors.GREEN + seeds + bcolors.ENDC,
            bcolors.RED + peers + bcolors.ENDC))

    sys.stdout.write("Which torrent to retrieve ? (or q to quit) : ")
    torrent = sys.stdin.readline()

    if torrent.strip() == "q":
        print("Exiting the client.")
        sys.exit(0)

    trackerindex = feed.find_all('guid')[int(torrent)].get_text()
    # trackerindex = trackerindex.replace("node21", "www.torrentz.com")

    title = feedTitle[int(torrent)].get_text()
    title = title.replace(' ', '_').replace('/', '_')
    # formatting for saved torrent filename

    print("GET %s" % trackerindex)

    trackers = urllib.urlopen(trackerindex).read()
    # trackers var contain the source of the torrentz selectioned torrent page

    outputPath = destdir + '/' + title + '.torrent'
    # outputPath = '/home/thomacer/Downloads/' + title + '.torrent'

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
