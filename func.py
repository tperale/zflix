#!/usr/bin/python
# -*- coding: utf-8 -*-

# Find a better filename

import urllib
import bs4
import os
import sys


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

    if href is not None:
        while match:
            match = (toFind in urls[0].get('href'))

    else:
        match = False
    i = 0

    while not(match) and i < (len(urls) - 1):
        i += 1

        href = urls[i].get('href')

        if href is not None:
            j = 0
            while match:
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
