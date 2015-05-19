#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import os
import argparse
import subprocess
from configParser import parse_config
from trackersParser import TrackersPage, save_file
from torrentSearch import Torrentz


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()


def main(option, torrentz):
    torrentz.search_torrent(option.search.replace(' ', '+'), option.check)

    trackersPage = TrackersPage(torrentz.trackerIndex)
    # trackers var contain the source of the torrentz selectioned torrent page

    if trackersPage.torrentFile:
        outputPath = option.destdir + '/' + torrentz.torrentTitle + '.torrent'
        save_file(trackersPage.torrentFile, outputPath)

        # Launch peerflix
        command = 'peerflix %s --%s' % (outputPath, option.player)
        print(command)
        subprocess.Popen(command, shell=True).split()


if __name__ == "__main__":
    domain = 'https://www.torrentz.com'
    config = parse_config()

    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('search', type=str)
        parser.add_argument('-d', '--destdir',
                            default=config.get('general', 'destdir'),
                            type=str,
                            help='Destination of the downloaded torrent')
        parser.add_argument('-n', '--not_verified',
                            default=config.getboolean('general',
                                                      'not_verified'),
                            action='store_true',
                            help='Option to do unverified search')
        parser.add_argument('-c', '--check',
                            default=config.getboolean('general', 'check'),
                            action='store_true',
                            help=('Check link before to output them. This '
                                  + 'function is heavily slower but some '
                                  + 'torrent are often deleted so it may '
                                  + 'be usefull.'))
        parser.add_argument('-nr', '--not_remove', default=False,
                            action='store_true',
                            help=("Don't erase the torrent you downloaded when "
                                  + "the stream is interrupted"))
        # TODO
        parser.add_argument('-p', '--player',
                            default=config.get('general', 'player'),
                            type=str,
                            help=("Choose the player you want to use to watch"
                                  + " your streamed torrent"))
        option = parser.parse_args()
    except Exception as e:
        # Would happen if config file is lacking of argument
        print('Error parsing in the config file.')
        print(e)

    else:
        site = Torrentz(option.not_verified)

        option.destdir = os.path.expanduser(option.destdir)

        main(option, site)
