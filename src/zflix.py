#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import os
import argparse
import subprocess
from configParser import parse_config
import json


class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US)" + \
        "AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0"

urllib._urlopener = AppURLopener()

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


def main(option):
    # trackers = json.load('trackers.json')
    # for tacker in trackers:
    # Should find a way to import all of the trackers
    from trackers.torrentz import Torrentz
    from multiprocessing import Process, Manager

    trackers = [Torrentz]

    queryResult = {}

    for tracker in trackers:
        #process = Process(target=tracker.search_torrent,
        #                  args=(option.search, queryResult, ))
        #process.start()
        tracker().search_torrent(option.search, queryResult)


    outputList = []

    outputNum = 10 # TODO DELETE.
    for i in range(outputNum):
        # Creating the torrent selection output.
        output = max(queryResult, key=lambda x: queryResult[x][0]['seeds'])
        output = queryResult[output].pop(0)
        outputList.append(output)

        print('%2i) %50s: Size: %5sMB Seeds: %3s Peers: %3s' %
              (i,
               output['title'] if len(output['title']) < 50 else output['title'][:50],
               output['size'],
               bcolors.GREEN + str(output['seeds']) + bcolors.ENDC,
               bcolors.WARNING + str(output['peers']) + bcolors.ENDC
               )
              )


    torrentNum = input('Enter the torrent number you want to get. ')

    if torrentNum != 'q' and torrentNum != 'Q':
        pageLink = outputList[torrentNum]
        download = pageLink['ref'].download(pageLink['link'])
        if download:
            outputPath = option.destdir + '/' + torrentz.torrentTitle + '.torrent'
            save_file(trackersPage.torrentFile, outputPath)

            # Launch peerflix
            command = 'peerflix %s --%s' % (outputPath, option.player)
            subprocess.Popen(command, shell=True)


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
        option.destdir = os.path.expanduser(option.destdir)
        main(option)
