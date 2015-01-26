#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import os
import argparse
import subprocess
from func import *


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()



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
    trackerIndex = search_torrent(option.search.replace(' ', '+'), domain)

    print("GET %s" % trackerIndex)

    trackers = urllib.urlopen(trackerIndex).read()
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
