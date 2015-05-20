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

def save_file(toSave, outputPath):
    """
    Save a webpage in a specified file
    """
    try:
        print('Writting')
        with open(outputPath, "w") as openedFile:
            openedFile.write(toSave)

        print("Torrent Saved: %s" % (outputPath))

        res = True

    except Exception as e:
        res = False
        print(e)

    return res


def main(option):
    # trackers = json.load('trackers.json')
    # TODO Should find a way to import all of the trackers
    from trackers.torrentz import Torrentz
    from multiprocessing import Process, Manager

    trackers = [Torrentz]

    queryResult = {}

    for tracker in trackers:
        #process = Process(target=tracker.search_torrent,
        #                  args=(option.search, queryResult, ))
        #process.start()
        # TODO launch torrent in processes
        tracker().search_torrent(option.search, queryResult)

    outputList = []


    # CREATING the torrent selection output.
    # for a number of torrent the user specified in the option.
    i = 0
    while i < option.number_of_output and \
            max(map(lambda x, y=queryResult: len(y[x]), queryResult)):
        # while there is torrent to display.
        maxSeeds = max(map(lambda x: queryResult[x][0]['seeds'], queryResult))
        out = queryResult[maxSeeds].pop(0)
        outputList.append(out)

        print('%2i) %50s: Size: %5sMB Seeds: %3s Peers: %3s' %
              (i,
               out['title'] if len(out['title']) < 50 else out['title'][:50],
               out['size'],
               bcolors.GREEN + str(out['seeds']) + bcolors.ENDC,
               bcolors.WARNING + str(out['peers']) + bcolors.ENDC
               )
              )
        i += 1

    # ASKING the user wich torrent he want to retrive.
    torrentNum = input('Enter the torrent number you want to get. ')

    if torrentNum == 'q' or torrentNum == 'Q' or torrentNum < len(outputList):
        exit()

    pageLink = outputList[torrentNum]
    if option.magnet:
        # Download and save the torrent.
        download = pageLink['ref'].download(pageLink['link'])
        torrentToStream = option.destdir + '/' + pageLink['title'] + '.torrent'
        save_file(download, torrentToStream)

    else:
        # Use magne link to save the torrent.
        pass  # TODO

    # Launch peerflix
    command = "peerflix '%s' --%s --path %s"\
        % (torrentToStream, option.player, option.destdir)

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
                            help='Destination of the downloaded torrent'
                            )

        parser.add_argument('-m', '--no_magnet',
                            default=config.getboolean('general', 'no_magnet'),
                            action='store_true',
                            type=bool,
                            help=("Use magnet link (no torrent download.")
                            )
        # This option will call the get_magnet option of a tracker.
        # instead of the .download one.

        #parser.add_argument('-n', '--not_verified',
        #                    default=config.getboolean('general',
        #                                              'not_verified'),
        #                    action='store_true',
        #                    help='Option to do unverified search'
        #                    )
        # Deprecated with the new way to arrange data.

        #parser.add_argument('-c', '--check',
        #                    default=config.getboolean('general', 'check'),
        #                    action='store_true',
        #                    help=('Check link before to output them. This '
        #                          + 'function is heavily slower but some '
        #                          + 'torrent are often deleted so it may '
        #                          + 'be usefull.')
        #                    )
        # Deprecated

        #parser.add_argument('-nr', '--not_remove', default=False,
        #                    action='store_true',
        #                    help=("Don't erase the torrent you downloaded when "
        #                          + "the stream is interrupted")
        #                    )
        # Can be deprecated with the --magnet option

        parser.add_argument('-p', '--player',
                            default=config.get('general', 'player'),
                            type=str,
                            help=("Choose the player you want to use to watch"
                                  + " your streamed torrent")
                            )

        parser.add_argument('-no', '--number_of_output',
                            default=config.get('general', 'number_of_output'),
                            type=int,
                            help=("Number of torrent displayed with your search.")
                            )

        option = parser.parse_args()
    except Exception as e:
        # Would happen if config file is lacking of argument
        # TODO if an option is not in the config file add the line needed with
        # TODO default value.
        print('Error parsing in the config file.')
        print(e)

    else:
        option.destdir = os.path.expanduser(option.destdir)
        main(option)
