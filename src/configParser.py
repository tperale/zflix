import ConfigParser
import os


# Option present in the file
# [general]
# player = [mpv, vlc, ...]
# destdir = [default: '~/Download']
# not_verified = [True, False]


def create_default_file():
    """
    Default config copy if files don't exist in your system
    """
    with open('defaultFile') as default:
        f = open(os.path.expanduser('~/.zflixrc'))
        for line in default.readlines():
            f.write(line)
        f.close()


def parse_config():
    config = ConfigParser.ConfigParser()
    user = os.path.expanduser('~')
    try:
        print('Trying to parse ~/.zflixrc')
        config.readfp(open(user + '/.zflixrc'))
    except IOError:
        try:
            print('Failed')
            print('Trying to parse ~/.config/zflix/config')
            config.readfp(open(user + '/.config/zflix/config'))
        except IOError:
            create_default_file()
            config.readfp(open(user + '/.zflixrc'))

    return config
