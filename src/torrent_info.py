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
            if current is None:
                break

            if self.special.get(current, False):
                value = self.special[current]()

            elif current.isdigit():
                while current.isdigit() and (current is not None):
                    current += next(self.reader, None)
                value = self.string_eval(int(current[:-1]))

            current = next(self.reader, None)
            if current is None:
                break

            res[key] = value

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
        torrent = open(fileName, 'r')
        current = torrent.read(1)#.decode("utf-8", "replace")
        while current != '':
            #if current == '\n':
            #    current = torrent.read(1).decode("utf-8", "replace")
            #    continue
            yield current
            current = torrent.read(1)#.decode("utf-8", "replace")

        torrent.close()


def get_info(toDecode):
    """
    Return a list of all files the torrent will output.
    """
    torrent = bencoding(toDecode)
    info = torrent.decode()
    try:
        info = info['info']
    except:
        info = info

    print(info)

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

if __name__ == '__main__':
    import sys
    print(get_info(sys.argv[1]))
