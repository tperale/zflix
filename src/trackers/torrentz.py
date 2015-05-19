#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import bs4
import os
import sys


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()


class Torrentz:
    def __init__(self):
        self.domain = 'https://www.torrentz.com'
        #if not_verified:
        self.domain += '/feedP'
        #else:
        #    self.domain += '/feed_verifiedP'

        self.trackerIndex = None
        self.torrentTitle = None

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

    def location_testing(self, pageLink):
        """
        Each download locations specified in the dict 'locations' is tested
        and the result is yielded (False if it didn't worked, else True)
        """
        page = urllib.urlopen(pageLink).read()
        soup = bs4.BeautifulSoup(page, 'html.parser')
        trackersUrls = soup.find_all('a')  # Every trackers listed in the page

        for name in self.locations:
            res = False
            os.write(sys.stdout.fileno(), "trying %s... \n" % name)

            res = self.get_page(trackersUrls, self.locations[name]['url'])
            # If find Tracker specific page
            if res is not False:
                soup = bs4.BeautifulSoup(res)
                urls = soup.find_all('a')
                # Looking for the download link
                res = self.get_page(urls, self.locations[name]['dl'])

            yield res

        print("Error: Torrent found in none of the locations")

    def download(self, pageLink):
        downloadLocationTest = self.location_testing(pageLink)
        hit = False
        while hit is False and hit is not None:
            hit = next(downloadLocationTest, None)

        return hit

    def search_torrent(self, search, queryResult):
        """
        Add to the dic "queryResult" with a refernce used for the key
        a list of returned torrent link with a specific search term.
        ARGUMENTS:
            search: The user searcher torrents.
            queryResult: A dict proxy where the result will be stocked.
        """
        torrentzPage = urllib.urlopen(self.domain + '?q=' + search).read()
        feed = bs4.BeautifulSoup(torrentzPage)
        feedLink = feed.find_all('guid')
        feedTitle = feed.find_all('title')
        feedDescription = feed.find_all('description')

        feedTitle.pop(0) # useless info
        feedDescription.pop(0) # useless info

        if len(feedTitle) == 0:
            queryResult[self] = None
            return

        queryResult[self] = []
        for i in range(len(feedTitle)):
            newEntry = {}
            newEntry['title'] = feedTitle[i].get_text()
            newEntry['link'] = feedLink[i].get_text()

            description = feedDescription[i].get_text().split()
            # We parse something like
            # <description>Size: 4780 MB Seeds: 27 Peers: 17 Hash:
            # a000000a00a0aaaa00aa0000a0aaa0a0000aa0aa </description>
            newEntry['size'] = description[1]
            # Don't need to be converted in an int.
            newEntry['seeds'] = int(description[4])
            newEntry['peers'] = int(description[6])
            newEntry['ref'] = self

            queryResult[self].append(newEntry)