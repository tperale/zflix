#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib
import os
import argparse
import subprocess
from configParser import parse_config
# import json
from multiprocessing import Process, Manager


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
    Save "toSave" file (a .torrent file for example), to the "outputPath"
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


def start_search(tracker, query, queryResult):
    """
    Funtion used to make tracker query easier (the tracker module can just send
    back a dict and don't have to mess with the dict)
    """
    queryResult[tracker] = tracker().search_torrent(query)


def main(option):
    # trackers = json.load('trackers.json')
    # TODO Should find a way to import all of the trackers
    from trackers.torrentz import torrentz

    trackers = [torrentz]

    manager = Manager()
    tmpResult = manager.dict()
    processes = []

    for x in trackers:
        # Create all processes and stock them in a list to be sure that
        # they are all finished.
        tmpProcess = Process(target=start_search,
                             args=(x, option.search, tmpResult)
                             )
        tmpProcess.start()
        processes.append(tmpProcess)

    for process in processes:
        # Wait for every process to be finished.
        process.join()

    queryResult = dict(tmpResult)
    # Convert into a traditionnal dict to be more easy to work with


    # CREATING the torrent selection output.
    # for a number of torrent the user specified in the option.
    i = 0
    outputList = []
    while i < option.number_of_output and \
            max(map(lambda x, y=queryResult: len(y[x]), queryResult)):
        # while there is torrent to display.
        maxSeeds = max(queryResult, key=lambda x: queryResult[x][0]['seeds'])
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

    if torrentNum == 'q' or torrentNum == 'Q' or (torrentNum > len(outputList)):
        exit()

    pageLink = outputList[torrentNum]
    torrentName = pageLink['title']
    if option.no_magnet:
        # Download and save the torrent.
        download = pageLink['ref'].get_torrent(pageLink['link'])
        torrentToStream = option.destdir + '/' + pageLink['title'] + '.torrent'
        save_file(download, torrentToStream)

    else:
        # Use magne link to save the torrent.
        torrentToStream = pageLink['ref'].get_magnet(pageLink['link'])

    # Launch peerflix
    command = "peerflix '%s' --%s --path %s"\
        % (torrentToStream, option.player, option.destdir)
    try:
        peerflix = subprocess.Popen(command, shell=True)
        peerflix.wait()

    except KeyboardInterrupt:
        # If during the stream trhe user exit it, the program will ask if he
        # want to remove the download because maybe it's not ended.
        if option.destdir == '/tmp':
            print('Exiting')
            exit()

        #for dirFile in os.path.dirname(option.destdir):
        #    for i in range(min(len()))
        # TODO not functionnal
        remove = raw_input("Do you want to remove the file ? [(y)es/(n)o]")
        if remove.lower() in ['yes', 'y', 'ye', 'ys']:
            toRemove = option.destdir
            if option.destdir[-1] != '/':
                toRemove += '/'
            toRemove += torrentName
            os.remove(toRemove)

    except:
        print('Peerflix is not installed, please type the following command'
              + ' to install it (if npm is installed):')
        print('sudo npm install -g peerflix')


if __name__ == "__main__":
    config = parse_config()

    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('search',
                            nargs='?',
                            default=None,
                            type=str
                            )

        parser.add_argument('-d', '--destdir',
                            default=config.get('general', 'destdir'),
                            type=str,
                            help='Destination of the downloaded torrent'
                            )

        parser.add_argument('-m', '--no_magnet',
                            default=config.getboolean('general', 'no_magnet'),
                            action='store_true',
                            help=("Use magnet link (no torrent download.")
                            )
        # This option will call the get_magnet option of a tracker.
        # instead of the .download one.

        parser.add_argument('-p', '--player',
                            default=config.get('general', 'player'),
                            type=str,
                            help=("Choose the player you want to use to watch"
                                  + " your streamed torrent")
                            )

        parser.add_argument('-out', '--number_of_output',
                            default=config.get('general', 'number_of_output'),
                            type=int,
                            help=("Number of torrent displayed with your search.")
                            )

        parser.add_argument('-no', '--no_data',
                            default=False,
                            action='store_true',
                            help="No data are saved, stream goes into /tmp"
                            )

        option = parser.parse_args()

    except Exception as e:
        # Would happen if config file is lacking of argument
        # TODO if an option is not in the config file add the line needed with
        # TODO default value.
        print('Error parsing in the config file.')
        print(e)

    else:
        while option.search is None or option.search.strip() == "":
            # If the user entered no "search" option.
            option.search = raw_input("Enter keywords you want to search: ")

        if option.no_data:
            option.magnet = True
            option.destdir = "/tmp"

        option.destdir = os.path.expanduser(option.destdir)
        main(option)
