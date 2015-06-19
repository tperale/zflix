#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
try:
    import bs4
except:
    print("BeautifulSoup4 is not installed.")
    exit()

class torrentz:
    def __init__(self):
        self.domain = 'https://www.torrentz.com'

    def get_magnet_from_tracker(self, trackerLink):
        """
        Get a magnet link on a webpage

        ARGUMENT:
            trackerLink: A link to a tracker.

        RETURN VALUE:
            A magnet link.
        """
        page = requests.get(trackerLink)
        page = page.text

        # Getting all the link in the page to try to get the magnet link.
        soup = bs4.BeautifulSoup(page)
        urls = soup.find_all('a')

        magnetLink = None
        for link in urls:
            inPageLink = link.get('href')
            if inPageLink is not None and 'magnet:' in inPageLink:
                print('Getting ' + link.get('href'))
                magnetLink = link.get('href')

        return magnetLink

    def get_specific_tracker(self, pageLink):
        """
        Get the a supported tracker from a torrentz page.

        ARGUMENT:
            pageLink: A torrentz download page link.

        RETURN VALUE:
            The link of a supported tracker.
        """
        # Getting the page.
        page = requests.get(pageLink)
        page = page.text

        soup = bs4.BeautifulSoup(page)

        trackersUrls = soup.find('div', class_="download")
        # Get the div with the links first
        trackersUrls = trackersUrls.find_all('dl')
        trackersUrls.pop(0) # First is a sponsored link
        # Every trackers listed in the page

        for tracker in trackersUrls:
            # YIELD every tracker link to try to get the magnet link there.
            trackerLink = tracker.find('a')
            yield trackerLink.get('href')

        print("Error: Torrent found in none of the locations")

    def get_magnet(self, pageLink):
        """
        Function returning the magnet link for the torrent.

        ARGUMENT:
            pageLink: The link of the page you want to get the torrent.

        RETURN VALUE:
            A magnet link.
        """
        downloadLocationTest = self.get_specific_tracker(self.domain + pageLink)
        magnet = False

        while magnet is False:
            trackerLink = next(downloadLocationTest, None)
            if trackerLink is not None:
                magnet = self.get_magnet_from_tracker(trackerLink)
            else:
                break

        return magnet

    def search_torrent(self, search):
        """
        Add to the dic "queryResult" with a refernce used for the key
        a list of returned torrent link with a specific search term.

        ARGUMENTS:
            search: The user searcher torrents.
            queryResult: A dict proxy where the result will be stocked.
        """
        torrentzPage = requests.get(self.domain + '/any?f=' + search)
        torrentzPage = torrentzPage.text
        soup = bs4.BeautifulSoup(torrentzPage)
        torrentLinks = soup.find('div', class_="results")
        torrentLinks = torrentLinks.find_all('dl')

        result = []
        for link in torrentLinks[:-1]:
            newEntry = {}

            mainCell = link.find("a")
            newEntry['title'] = mainCell.text
            newEntry['link'] = mainCell.get("href")

            try:
                newEntry['size'] = link.find("span", class_="s").text
            except AttributeError:
                newEntry['size'] = "Pending"

            # Don't need to be converted in an int.
            newEntry['seeds'] = link.find("span", class_="u"
                                          ).text.replace(',', '')
            newEntry['peers'] = link.find("span", class_="d"
                                          ).text.replace(',', '')

            newEntry['ref'] = self

            result.append(newEntry)

        return result
