import bs4
import urllib
import zipfile

class Subtitle:
    """
    Subtile from subscene.
    """

    def __init__(self, language, path):
        langDic = {'fr': 'french',
                   'fre': 'french',
                   'french': 'french'}

        self.lang = langDic[language]
        self.url = 'http://subscene.com'
        self.path = path

    def intersection(self, baseName, otherName):
        # TODO IMPROVE
        res = 0
        otherName =  otherName.lower()
        for word in otherName.split():
            if word in baseName:
                res += 1

        return res

    def search(self, name):
        searchName = name.replace(' ', '+')
        searchPage = urllib.urlopen(self.url +
                                    '/subtitles/title?q=' + searchName)
        searchPage = searchPage.read()

        soup = bs4.BeautifulSoup(searchPage)
        urls = soup.find_all('a')

        maxWords = 0
        res = 0
        for url in urls:
            # TODO IMPROVE
            if self.intersection(name, url.get_text()) > maxWords:
                res = url.get('href')

        subPageName = self.url + res
        self.get_subtitles(subPageName)

    def get_subtitles(self, pageUrl):
        page = urllib.urlopen(pageUrl + self.lang).read()

        soup = bs4.BeautifulSoup(page)
        links = soup.find_all('a')

        i = 0
        while '/subtiles/' not in links[i].get('href'):
            i += 1

        self.download_sub(link[i].get('href'))

    def download_sub(self, link):
        page = urllib.urlopen(self.url + link).read()
        soup = bs4.BeautifulSoup(page)

        link = soup.find(id='downloadButton')

        subFile = urllib.urlopen(link.get('href')).read()
        # A zip file is downloaded
        with open('/tmp/sub.zip', 'w') as destFile:
            destFile.write(subFile)

        zfile = zipfile.ZipFile('/tmp/sub.zip')
        zfile.extract('sub.srt', '/tmp/')
