import urllib
import bs4


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()


class Torrentz:
    def __init__(self, not_verified):
        self.domain = 'https://www.torrentz.com'
        if not_verified:
            self.domain += '/feedP'
        else:
            self.domain += '/feed_verifiedP'

        self.trackerIndex = None
        self.torrentTitle = None

    def search_torrent(self, search, queryResult):
        """
        Add to the dic "queryResult" with the key "torrentz" a list of returned
        torrent link with a specific search term.
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
            queryResult['torrentz'] = None
            return

        for i in range(len(feedTitle)):
            newEntry = {}
            newEntry['title'] = feedTitle[i].get_text()
            newEntry['link'] = feedLink[i].get_text()

            description = feedDescription[i].get_text().split()
            # We parse something like
            # <description>Size: 4780 MB Seeds: 27 Peers: 17 Hash:
            # a000000a00a0aaaa00aa0000a0aaa0a0000aa0aa </description>
            newEntry['size'] = description[1]
            newEntry['seeds'] = description[4]
            newEntry['peers'] = description[6]

            queryResult['torrentz'].append(newEntry)
