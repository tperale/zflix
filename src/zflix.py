#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import bs4
import sys
import os
import argparse
import subprocess
from func import *


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    RED = '\033[31m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1;1m'
    UNDERLINE = '\033[4m'

    def disable(self):
        self.HEADER = ''
        self.BLUE = ''
        self.GREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        self.BOLD = ''


locations = {"h33t": {"url": "http://www.h33t.to",
                      "dl": "h33t.to/get/"},
             "demonoid": {"url": "www.demonoid.pw",
                          "dl": "www.demonoid.pw/files/download/"},
             "seedpeer.eu": {"url": "www.seedpeer.eu/",
                             "dl": "www.seedpeer.eu/download/"},
             "rarbg": {"url": "rarbg.com/torrent/",
                       "dl": "https://rarbg.com/download.php?id="},
             "tpb": {"url": "http://thepiratebay.org",
                     "dl": "http://torrents.thepiratebay.org"},
             "yourbittorrent": {"url": "yourbittorent.com/torrent/",
                                "dl": "yourbittorrent.com/down/*.torrent"},
             "isohunt": {"url": "http://isohunt.to",
                         "dl": "torrent.isohunt.to/download.php?id="},
             "torrentfunk.com": {"url": "http://www.torrentfunk.com",
                                 "dl": "www.torrentfunk.com/tor/*.torrent"},
             "limetorrents.cc": {"url": "http://www.limetorrents.cc",
                                 "dl": "itorrents.org/torrent/"},
#             "torrents.net": {"url": "http://www.torrents.net",
#                              "dl": "torrents.net/down/*.torrent"},
             "vertor": {"url": "http://www.vertor.com",
                        "dl": "?mod=download."},
             "monova": {"url": "www.monova.org/torrent/",
                        "dl": "www.monova.org/download/torrent/*.torrent"},
             "torlock": {"url": "www.torlock.com",
                         "dl": ".torrent"},
             "torrentproject": {"url": "torrentproject.se",
                                "dl": "torrentproject.se/torrent/*.torrent"}

             }

# TODO
# torrentproject, torrentreactor use an other page to the download
# bitsnoop, tpb, kat are blocked


def main(option, domain):
    search = option.search.replace(' ', '+')
    torrentzPage = urllib.urlopen(domain + '?q=' + search).read()
    feed = bs4.BeautifulSoup(torrentzPage)
    feedTitle = feed.find_all('title')
    feedDescription = feed.find_all('description')

    print(bcolors.HEADER + feedTitle[0].get_text() + bcolors.ENDC)
    feedTitle.pop(0)
    feedDescription.pop(0)

    item_num = len(feedTitle)

    if item_num == 0:
        print("Sorry, no torrents found.")
        if not option.no_verified:
            print("Try: python " + ' '.join(sys.argv[:]) + ' -n')
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

        print('%2i) %50s: Size: %5sMB Seeds: %3s Peers: %3s' %
              (i,
               title if len(title) < 50 else title[:50],
               size,
               bcolors.GREEN + seeds + bcolors.ENDC,
               bcolors.WARNING + peers + bcolors.ENDC)
              )

    print("Which torrent to retrieve ? (or q to quit) : ")
    torrentNum = sys.stdin.readline()

    if torrentNum.strip() == "q":
        print("Exiting the client.")
        sys.exit(0)

    trackerindex = feed.find_all('guid')[int(torrentNum)].get_text()

    # trackerindex = trackerindex.replace("node21", "www.torrentz.com")

    # formatting for saved torrent filename
    title = feedTitle[int(torrentNum)].get_text()
    title = title.replace(' ', '_').replace('/', '_')

    print("GET %s" % trackerindex)

    trackers = urllib.urlopen(trackerindex).read()
    # trackers var contain the source of the torrentz selectioned torrent page

    outputPath = option.destdir + '/' + title + '.torrent'

    hit = False
    downloadLocationTest = locationTesting(trackers,
                                           outputPath,
                                           title,
                                           locations)

    while hit is False and hit is not None:
        hit = next(downloadLocationTest, None)


    # Launch peerflix
    if hit is not None:
        subprocess.Popen(('peerflix %s --%s' %
                          (outputPath, option.player)).split())


if __name__ == "__main__":
    defaultDestdir = os.path.expanduser('~/downloads')
    domain = 'https://www.torrentz.com'
    defaultPlayer = 'mpv'
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str)
    parser.add_argument('-d', '--destdir', default=defaultDestdir, type=str,
                        help='Destination of the downloaded torrent')
    parser.add_argument('-n', '--no_verified', default=False,
                        action='store_true',
                        help='Option to do unverified search')
    parser.add_argument('-c', '--check', default=False, action='store_true',
                        help=('Check link before to output them (slower). '
                              + 'Some link are deprecated.'))
    parser.add_argument('-nr', '--not_remove', default=False,
                        action='store_true',
                        help=("Don't erase the torrent you downloaded when "
                              + "the stream is interrupted"))
    parser.add_argument('-p', '--player', default=defaultPlayer, type=str,
                        help=("Choose the player you want to use to watch"
                              + " your streamed torrent"))

    option = parser.parse_args()

    if option.no_verified:
        domain += '/feedP'
    else:
        domain += '/feed_verifiedP'

    option.destdir = os.path.expanduser(option.destdir)

    main(option, domain)
