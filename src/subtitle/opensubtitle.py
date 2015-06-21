from xmlrpc.client import ServerProxy
import struct, os
import requests
import zipfile


class NoSubtitleFound(Exception):
    def __init__(self, arg=None):
        print("No subtitle found.")

class opensubtitle:
    def __init__(self):
        self.domain = "http://api.opensubtitles.org/xml-rpc"
        self.xmlrpc_server = ServerProxy(self.domain)

        login = self.xmlrpc_server.LogIn("", "", "eng" , "OSTestUserAgent")
        self.token = login["token"]
        # Save the token to use it to query the webapi.

    def hash_name(self, name):
        """
        Code from:
        http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        Used to return a movie hash, from the name of a movie.
        """
        try:
            longlongformat = '<q'  # little-endian long long
            bytesize = struct.calcsize(longlongformat)

            f = open(name, "rb")

            filesize = os.path.getsize(name)
            hash = filesize

            if filesize < 65536 * 2:
                return "SizeError"

            for x in range(65536/bytesize):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF # to remain as 64bit number

            f.seek(max(0,filesize-65536),0)
            for x in range(65536/bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash = "%016x" % hash
            return returnedhash

        except(IOError):
            return "IOError"

    def search_query(self, query, lang):
        """
        Return type: a list of movies, returned by the opensubtitle api.
        """
        res = self.xmlrpc_server.SearchSubtitles(self.token,
                                                 [{"query": query,
                                                   "sublanguageid": lang,
                                                   }]
                                                 )["data"]
        return res

    def search_hash(self, name, lang, length):
        """
        """
        hashed_name = self.hash_name(name)

        searchTerms = [{"sublanguageid": lang,
                        "moviehash": hashed_name,
                        "moviebytesize": length,
                         }]

        res = self.xmlrpc_server.SearchSubtitles(self.token, searchTerms
                                                 )['data']

        # If there is no result, the api return False.
        return res

    def download(self, link, location, name):
        """
        ARGUMENTS:
            archive: The archive file to extract.
            location: Destination dir of the streamed torrent.
            name: Name of your streamed torrent

        RETURN VALUE:
            the name of extracted files
        """
        if location[-1] != '/':
            # Double checking.
            location += '/'

        archive = requests.get(link).content  # .content get the bytes.

        newName = '/tmp/' + name + '.zip'
        tmpZipFile = open(newName, "wb")
        tmpZipFile.write(archive)
        tmpZipFile.close()

        zfile = zipfile.ZipFile(newName)
        for name in zfile.namelist():
            if '.nfo' not in name:
                extractedFile = location + name
                zfile.extract(name, location)

        # TODO OS remove zip file creted and jk
        return extractedFile

    def get_subtitle(self, name, lang, length, location):
        """
        Try to find the best subtitle. according to the name the user pass in
        argument. And the download them in the movie folder.
        """
        subtitle = self.search_hash(name, lang, length)

        if subtitle is False:
            print('not hash')
            # Research by query are often more flexible and give more result.
            subtitle = self.search_query(name, lang)
            if subtitle:
                subtitle = subtitle.pop(0)
            else:
                raise NoSubtitleFound
        # for now we get the first subtitle of "subtitle", then we will try
        # to be more precise

        # Get the download.
        return self.download(subtitle["ZipDownloadLink"], location, name)
