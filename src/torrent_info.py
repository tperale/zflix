import os

class bencoding:
    # http://fileformats.wikia.com/wiki/Torrent_file
    def __init__(self, toDecode):
        # struct:
        # <special><number>:<string>e
        # or
        self.special = {'i': self.integer_eval,
                        'l': self.list_eval,
                        'd': self.dict_eval
                        }

        if os.path.isfile(toDecode):
            # It's a path to a torrent file.
            self.reader = self.create_gen(toDecode)
        else:
            # It's a magnet file.
            pass

        self.result = None

    def string_eval(self, i):
        res = ''
        for x in range(i):
            res += next(self.reader)

        print(('STRING', res))
        return res

    def integer_eval(self):
        current = next(self.reader)
        res = ''
        while current != 'e':
            res += current
            current = next(self.reader)

        print(('INT', res))
        return int(res) if res else ''

    def list_eval(self):
        current = next(self.reader)
        res = []
        while current != 'e':
            if self.special.get(current, False):
                new = self.special[current]()
                res.append(new)

            elif current.isdigit():
                while current.isdigit():
                    current += next(self.reader)
                new = self.string_eval(int(current[:-1]))
                res.append(new)


            current = next(self.reader)

        print(('LIST', res))
        return res

    def dict_eval(self):
        current = next(self.reader)
        res = {}
        while current != 'e':
            if self.special.get(current, False):
                key = self.special[current]()
            elif current.isdigit():
                while current.isdigit():
                    current += next(self.reader)
                key = self.string_eval(int(current[:-1]))
            else:
                current = next(self.reader)
                continue


            current = next(self.reader)

            if self.special.get(current, False):
                value = self.special[current]()

            elif current.isdigit():
                while current.isdigit():
                    current += next(self.reader)
                value = self.string_eval(int(current[:-1]))

            current = next(self.reader)

            res[key] = value

        print(('DICT', key, value))
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



    def create_gen(self, fileName):
        """
        Create a generator from a torrent file, to return the next letter,
        each time he is called.
        """
        torrent = open(fileName, 'rb')
        current = torrent.read(1).decode("utf-8", "replace")
        while current != '':
            print(current)
            yield current
            current = torrent.read(1).decode("utf-8", "replace")

        torrent.close()


def get_info(toDecode):
    """
    Return a list of all files the torrent will output.
    """
    torrent = bencoding(toDecode)
    info = torrent.decode()['info']

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


    return res
