#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import requests


class kat:
    domain = 'https://kat.cr/'

    def __init__(self):
        self.results = {}

    def get_torrent(self, pageLink):
        """
        Function returning the .torrent file to save into a user specified
        directory.

        ARGUMENT:
            pageLink: The link of the page you want to get the torrent.

        RETURN VALUE:
            The .torrent file.
        """
        return (self.results[pageLink])["download"]

    def get_magnet(self, pageLink):
        """
        Function returning the magnet link for the torrent.

        ARGUMENT:
            pageLink: The link of the page you want to get the torrent.

        RETURN VALUE:
            A magnet link.
        """
        return (self.results[pageLink])["magnet"]

    def _get_torrents_from_link(self, pageLink):
        """
        """
        result = []
        request = requests.get(pageLink)
        data = request.text
        soup = bs4.BeautifulSoup(data)
        odd = soup.find_all("tr", class_="odd")
        # First torrent on the page is considered odd
        even = soup.find_all("tr", class_="even")

        for torrent1, torrent2 in zip(odd, even):
            newEntry = {}

            mainCell = torrent1.find("a", class_="cellMainLink")
            newEntry['title'] = mainCell.text
            newEntry['link'] = mainCell.get("href")

            description = torrent1.find_all("td", class_="center")

            newEntry['size'] = description[0].text
            newEntry['seeds'] = description[3].text.replace(',', '')
            newEntry['peers'] = description[4].text.replace(',', '')
            magnet = torrent2.find("a", class_="imagnet icon16")
            newEntry['magnet'] = magnet.get("href")
            download = torrent2.find("a", class_="idownload icon16")
            newEntry['download'] = download.get("href")
            newEntry['ref'] = self

            result.append(newEntry)

            self.results[newEntry["link"]] = newEntry

            # Doing the same for the second torrent.
            newEntry = {}

            mainCell = torrent2.find("a", class_="cellMainLink")
            newEntry['title'] = mainCell.text
            newEntry['link'] = mainCell.get("href")

            description = torrent2.find_all("td", class_="center")

            newEntry['size'] = description[0].text
            # Don't need to be converted in an int.
            newEntry['seeds'] = description[3].text.replace(',', '')
            newEntry['peers'] = description[4].text.replace(',', '')
            magnet = torrent2.find("a", class_="imagnet icon16")
            newEntry['magnet'] = magnet.get("href")
            download = torrent2.find("a", class_="idownload icon16")
            newEntry['download'] = download.get("href")
            newEntry['ref'] = self

            result.append(newEntry)

            self.results[newEntry["link"]] = newEntry

        return result

    def _get_popular(self):
        """
        """
        pageByType = ['https://kat.cr/movies/', 'https://kat.cr/tv/',
                      'https://kat.cr/anime/']
        pageResult = {}
        for pageLink in pageByType:
            pageResult[pageLink] = self._get_torrents_from_link(pageLink)

        result = []
        for i in range(sum([len(pageResult[x]) for x in pageResult])):
            maxSeeds = max(pageResult,
                           key=lambda x: int(pageResult[x][0]['seeds'])
                           )
            # Find the torrent with the most seeder trough all tracker result.
            out = pageResult[maxSeeds].pop(0)
            if not len(pageResult[maxSeeds]):
            # If the list is empty delete so they are no error
                del pageResult[maxSeeds]

            result.append(out)

        return result

    def search_torrent(self, search):
        """
        Add to the dic "queryResult" with a refernce used for the key
        a list of returned torrent link with a specific search term.

        ARGUMENTS:
            search: The user searched torrents arguments.
        """
        if search == '':
            # If the user just want to search through popular torrents
            return self._get_popular()

        pageLink = self.domain + "usearch/?q=" + search

        return self._get_torrents_from_link(pageLink)

