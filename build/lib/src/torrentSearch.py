import urllib
import bs4
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

    def print_torrent(self, i, feedTitle, feedDescription):
        """
        Output the torrent name and some description for the torrent
        on position i from feedTitle and feedDescription.
        """

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

    def check_link(self, link):
        """
        Check if a link specified in argument isn't an error
        """

        page = urllib.urlopen(link).read()
        soup = bs4.BeautifulSoup(page)

        # Have to use class_ bevause it's a css class
        return not(soup.find(class_='error'))

    def search_torrent(self, search, check):
        torrentzPage = urllib.urlopen(self.domain + '?q=' + search).read()
        feed = bs4.BeautifulSoup(torrentzPage)
        feedLink = feed.find_all('guid')
        feedTitle = feed.find_all('title')
        feedDescription = feed.find_all('description')

        print(bcolors.HEADER + feedTitle[0].get_text() + bcolors.ENDC)
        feedTitle.pop(0)
        feedDescription.pop(0)

        if len(feedTitle) == 0:
            print("Sorry, no torrents found.")
            # if not option.no_verified:
            #     print("Try: python " + ' '.join(sys.argv[:]) + ' -n')
            sys.exit(0)

        if check:
            i = 0
            while i < len(feedTitle):
                if self.check_link(feedLink[i].get_text()):
                    self.print_torrent(i, feedTitle, feedDescription)
                    i += 1
                else:
                    feedTitle.pop(i)
                    feedDescription.pop(i)

        else:
            for i in range(len(feedTitle)):
                self.print_torrent(i, feedTitle, feedDescription)

        print("Which torrent to retrieve ? (or q to quit) : ")
        torrentNum = sys.stdin.readline()

        if torrentNum.strip() == "q":
            print("Exiting the client.")
            sys.exit(0)

        trackerIndex = feedLink[int(torrentNum)].get_text()
        print("GET from: %s" % trackerIndex)

        # formatting for saved torrent filename
        title = feedTitle[int(torrentNum)].get_text()
        title = title.replace(' ', '_').replace('/', '_')

        self.torrentTitle = title
        self.trackerIndex = trackerIndex
