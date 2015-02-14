#!/usr/bin/python
# -*- coding: utf-8 -*-

# Find a better filename

import urllib
import bs4
import os
import sys


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()


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


class TrackersPage:
    def __init__(self, url):
        self.page = urllib.urlopen(url).read()
        soup = bs4.BeautifulSoup(self.page, 'html.parser')
        self.trackersUrls = soup.find_all('a')
        # 'trackerUrls' contain a list of <a href=''>...</a>

        self.torrentFile = None


        self.locations = {"h33t": {"url": "http://www.h33t.to",
                                   "dl": "h33t.to/get/"},
                          "demonoid": {"url": "www.demonoid.pw",
                                       "dl": "www.demonoid.pw/files/download/"},
                          "seedpeer.eu": {"url": "www.seedpeer.eu/",
                                          "dl": "/download/"},
                          "rarbg": {"url": "rarbg.com/torrent/",
                                    "dl": "rarbg.com/download.php?id="},
                          #"tpb": {"url": "http://thepiratebay.org",
                          #        "dl": "http://torrents.thepiratebay.org"},
                          "yourbittorrent": {"url": "yourbittorent.com/torrent/",
                                             "dl": "/down/*.torrent"},
                          "isohunt": {"url": "http://isohunt.to",
                                      "dl": "torrent.isohunt.to/download.php?id="},
                          "torrentfunk.com": {"url": "/tor/*.torrent",
                                              "dl": "www.torrentfunk.com/tor/*.torrent"},
                          "limetorrents.cc": {"url": "http://www.limetorrents.cc",
                                              "dl": "itorrents.org/torrent/"},
                           "torrents.net": {"url": "http://www.torrents.net",
                                            "dl": "torrents.net/down/*.torrent"},
                          "vertor": {"url": "http://www.vertor.com",
                                     "dl": "?mod=download."},
                          "monova": {"url": "www.monova.org/torrent/",
                                     "dl": "www.monova.org/download/torrent/"},
                          "torrentdl": {"url": "torrentdownloads.me/torrent/",
                                        "dl": "itorrents.org/torrent/"}
                          #"torlock": {"url": "www.torlock.com",
                          #            "dl": ".torrent"},
                          #"torrentproject": {"url": "torrentproject.se",
                          #                   "dl": "torrentproject.se/torrent/*.torrent"}
                          }

        self.send_locations()

    def gethref(self, urlsList, toFind):
        """
        Seek the link 'toFind' in the whole page 'page' et return
        the exact destination you're looking for.

        toFind: Url of the page to find splitted in a list
        page: Source code of the page where you want to find 'toFind'
        """

        match = False
        i = 0

        while not(match) and i < len(urlsList):
            href = urlsList[i].get('href')

            if href is not None:
                j = 0
                match = True  # If it don't match it'll turn False
                while match and j < len(toFind):
                    # Verify that each part of 'toFind' is in 'href'
                    match = (toFind[j] in href)
                    j += 1
            i += 1

        # link['href'] is what's it is after href='...'
        return urlsList[i-1].get('href') if match else False

    def get_page(self, urlsList, researchedUrl):
        """
        """

        pageUrl = self.gethref(urlsList, researchedUrl.split('*'))
        if pageUrl:
            # If gethref() found the correct url
            print('Entering: %s' % (pageUrl))
            res = urllib.urlopen(pageUrl).read()
            # Contain the source code of the page
        else:
            res = False
            # If the base page didn't contain the url we were looking for

        return res

    def location_testing(self):  # ,  outputPath, title):
        """
        Each download locations specified in the dict 'locations' is tested
        and the result is yielded (False if it didn't worked, else True)
        """

        for name in self.locations:
            res = False
            os.write(sys.stdout.fileno(), "trying %s... \n" % name)

            res = self.get_page(self.trackersUrls, self.locations[name]['url'])
            # If find Tracker specific page
            if res is not False:
                soup = bs4.BeautifulSoup(res)
                urls = soup.find_all('a')
                # Looking for the download link
                res = self.get_page(urls, self.locations[name]['dl'])

            yield res

        print("Error: Torrent found in none of the locations")

    def send_locations(self):
        downloadLocationTest = self.location_testing()
        hit = False
        while hit is False and hit is not None:
                hit = next(downloadLocationTest, None)

        self.torrentFile = hit
