#!/usr/bin/python
# -*- coding: utf-8 -*-

# Find a better filename

import urllib
import bs4
import os
import sys


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


def search_torrent(search, domain):
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

    trackerIndex = feed.find_all('guid')[int(torrentNum)].get_text()

    # formatting for saved torrent filename
    title = feedTitle[int(torrentNum)].get_text()
    title = title.replace(' ', '_').replace('/', '_')

    return title, trackerIndex



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
    Seek the link 'toFind' in the whole page 'page' et return
    the exact destination you're looking for.

    toFind: Url of the page to find splitted in a list
    page: Source code of the page where you want to find 'toFind'
    """

    soup = bs4.BeautifulSoup(page)
    urls = soup.find_all('a')  # 'urls' contain a list of <a href=''>...</a>

    href = urls[0].get('href')


    match = False
    i = 0

    while not(match) and i < (len(urls) - 1):
        i += 1

        href = urls[i].get('href')

        if href is not None:
            j = 0
            while not(match) and j < len(toFind):
                # Verify that each part of 'toFind' is in 'href'
                match = (toFind[j] in href)
                j += 1

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

    pageUrl = gethref(basePage, researchedUrl.split('*'))
    if pageUrl:
        # If gethref() found the correct url
        print('Entering: %s' % (pageUrl))
        res = urllib.urlopen(pageUrl).read()
        # Contain the source code of the page
    else:
        res = False
        # If the base page didn't contain the url we were looking for

    return res


def locationTesting(trackersPage, outputPath, title, locations):
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
