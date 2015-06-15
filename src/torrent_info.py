# import os
import requests


class bencoding:
    # http://fileformats.wikia.com/wiki/Torrent_file
    def __init__(self, magnet):
        self.special = {'i': self.integer_eval,
                        'l': self.list_eval,
                        'd': self.dict_eval
                        }

        # FIRST we need to decode the magnet  link and convert it in a torrent
        # file, so we can parse it and get infos.
        self.torrent = self.download_torrent(magnet)

        self.reader = self.create_gen(self.torrent)

        self.result = None

    def download_torrent(self, magnet):
        """
        Downlad from torrage a torrent file according to the magnet file passed
        on argument.

        DOC:
            https://en.wikipedia.org/wiki/Magnet_URI_scheme
        """
        url = 'https://torrage.com/torrent/'
        # First we should get the BitTorrent Info Hash ("xt=urn:btih:")
        search = "xt=urn:btih:"
        i = 0
        while (i < (len(magnet) - len(search))) \
                and ((magnet[i:i + len(search)]) != search):
            i += 1

        if i == (len(magnet) - len(search)):
            raise Exception()

        i += len(search)
        # Adding the search length to set i at the start of the BIH

        j = i # END of the info hash
        while magnet[j] != '&' and j < len(magnet):
            j += 1

        # magnet[i:j] represent the BIH
        print("Downloading the torrent from " + url + magnet[i:j])
        torrent = requests.get(url + magnet[i:j])

        return torrent.text

    def string_eval(self, i):
        res = ''
        for x in range(i):
            current = next(self.reader, None)
            if current is None:
                break
            res += current
        return res

    def integer_eval(self):
        current = next(self.reader)
        res = ''
        while current != 'e':
            res += current
            current = next(self.reader)

        return int(res) if res else ''

    def list_eval(self):
        current = next(self.reader)
        res = []
        while current != 'e' and current is not None:
            if self.special.get(current, False):
                new = self.special[current]()
                res.append(new)

            elif current.isdigit():
                while current.isdigit() and current is not None:
                    current += next(self.reader, None)
                new = self.string_eval(int(current[:-1]))
                res.append(new)

            current = next(self.reader, None)

        return res

    def dict_eval(self):
        current = next(self.reader)
        res = {}
        while (current != 'e') and (current is not None):
            if self.special.get(current, False):
                key = self.special[current]()
            elif current.isdigit():
                while current.isdigit() and (current is not None):
                    current += next(self.reader, None)

                key = self.string_eval(int(current[:-1]))

            current = next(self.reader, None)

            if self.special.get(current, False):
                value = self.special[current]()

            elif current.isdigit():
                while current.isdigit() and (current is not None):
                    current += next(self.reader, None)
                value = self.string_eval(int(current[:-1]))

            res[key] = value

            current = next(self.reader, None)

        return res

    def decode(self):
        """
        Find the first data structure to parse.
        """
        if self.result is not None:
            return self.result

        current = next(self.reader)

        if current == "d":
            res = self.dict_eval()

        if current == "l":
            res = self.list_eval()

        self.result = res

        return res

    def create_gen(self, fileContent):
        """
        Create a generator from a torrent file, to return the next letter,
        each time he is called.
        """
        # torrent = open(fileName, 'r')
        # current = torrent.read(1)
        # while current != '':
        #     yield current
        #     current = torrent.read(1)
        # torrent.close()
        for i in fileContent:
            yield i


def get_info(magnet, destdir):
    """
    Return a list of all files the torrent will output.
    """
    torrent = bencoding(magnet.upper())
    info = torrent.decode()
    info = info['info']

    if info.get('files', False):
        # If there is more than 1 file.
        res = []
        for torrentFile in info['files']:
            res.append({'name': '/'.join(torrentFile['path']),
                        'length': torrentFile['length'],
                        'folder': info['name']}
                       )
    else:
        res = [{'name': info['name'],
                'length': info['length'],
                'folder': None}]

    if destdir != "/tmp":
        # If the user want to save the torrent file.
        with open(destdir + res[0]['name'], "w") as torrent:
            torrent.write(torrent.torrent)
        print("Torrent saved in " + destdir)

    return res



if __name__ == '__main__':
    # For debugging.
    import sys
    print(get_info(sys.argv[1]))
