#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import bs4
import os
import sys


class torrentz:
    def __init__(self):
        self.domain = 'https://www.torrentz.com'
        self.domain += '/feedP'

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

    def get_href(self, urlsList, toFind):
        """
        Seek the link 'toFind' in the whole page 'page' and return
        the exact destination you're looking for.

        ARGUMENTS:
            toFind: Url of the page to find splitted in a list
            page: Source code of the page where you want to find 'toFind'

        RETURN VALUE:
            The destination you're looking for.
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
        Get the page of the researchedUrl.

        ARGUMENTS:
            urlsList: List of link in the page.
            researchedUrl: Researched url trough the urlsList

        RETURN VALUE:
            The page of the searched url or a False if the url is not found.
        """
        pageUrl = self.get_href(urlsList, researchedUrl.split('*'))
        if pageUrl:
            # If gethref() found the correct url
            print('Entering: %s' % (pageUrl))
            res = requests.get(pageUrl)
            res = res.text
            # Contain the source code of the page
        else:
            res = False
            # If the base page didn't contain the url we were looking for

        return res

    def get_torrent_from_tracker(self, trackerPage, trackerName):
        """
        Get a magnet link on a webpage

        ARGUMENTS:
            trackerPage: A link to a tracker.
            trackerName: The name of that tracker, used to find the format
                of a download link for a torrent.

        RETURN VALUE:
            A .torrent file.
        """
        # If find Tracker specific page
        soup = bs4.BeautifulSoup(trackerPage)
        urls = soup.find_all('a')
        # Looking for the download link
        return self.get_page(urls, self.locations[trackerName]['dl'])

    def get_magnet_from_tracker(self, trackerPage):
        """
        Get a magnet link on a webpage

        ARGUMENT:
            trackerPage: A link to a tracker.

        RETURN VALUE:
            A magnet link.

        NB:
            It work like self.get_href but more simple.
        """
        soup = bs4.BeautifulSoup(trackerPage)
        urls = soup.find_all('a')

        i = 0
        res = False
        while res is False and i < len(urls):
            if 'magnet:' in urls[i].get('href'):
                print('Getting ' + urls[i].get('href'))
                res = urls[i].get('href')
            i += 1

        return res

    def get_specific_tracker(self, pageLink):
        """
        Get the a supported tracker from a torrentz page.

        ARGUMENT:
            pageLink: A torrentz download page.

        RETURN VALUE:
            The page of a supported tracker, and the name of the tracker.
        """
        page = requests.get(pageLink)
        page = page.text
        soup = bs4.BeautifulSoup(page, 'html.parser')
        trackersUrls = soup.find_all('a')  # Every trackers listed in the page

        for name in self.locations:
            os.write(sys.stdout.fileno(), "trying %s... \n" % name)

            trackersPage = self.get_page(trackersUrls,
                                         self.locations[name]['url']
                                         )
            if trackersPage:
                yield trackersPage, name

        print("Error: Torrent found in none of the locations")

    def get_torrent(self, pageLink):
        """
        Function returning the .torrent file to save into a user specified
        directory.

        ARGUMENT:
            pageLink: The link of the page you want to get the torrent.

        RETURN VALUE:
            The .torrent file.
        """
        trackerFind = self.get_specific_tracker(pageLink)
        torrent = False
        while torrent is False:
            # Use a loop if torrent is not found in the page.
            trackerPage, trackerName = next(trackerFind, (None, None))
            torrent = self.get_torrent_from_tracker(trackerPage, trackerName)

        return torrent

    def get_magnet(self, pageLink):
        """
        Function returning the magnet link for the torrent.

        ARGUMENT:
            pageLink: The link of the page you want to get the torrent.

        RETURN VALUE:
            A magnet link.
        """
        downloadLocationTest = self.get_specific_tracker(pageLink)
        magnet = False

        while magnet is False:
            trackerPage, trackerName = next(downloadLocationTest, None)
            magnet = self.get_magnet_from_tracker(trackerPage)

        return magnet

    def search_torrent(self, search):
        """
        Add to the dic "queryResult" with a refernce used for the key
        a list of returned torrent link with a specific search term.

        ARGUMENTS:
            search: The user searcher torrents.
            queryResult: A dict proxy where the result will be stocked.
        """
        torrentzPage = requests.get(self.domain + '?q=' + search)
        torrentzPage = torrentzPage.text
        feed = bs4.BeautifulSoup(torrentzPage)
        feedLink = feed.find_all('guid')
        feedTitle = feed.find_all('title')
        feedDescription = feed.find_all('description')

        feedTitle.pop(0) # useless info
        feedDescription.pop(0) # useless info

        if len(feedTitle) == 0:
            return []

        result = []
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
            newEntry['seeds'] = description[4].replace(',', '')
            newEntry['peers'] = description[6].replace(',', '')
            newEntry['ref'] = self

            result.append(newEntry)

        return result
