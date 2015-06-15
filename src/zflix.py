#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
from configParser import parse_config, parse_default
from multiprocessing import Process, Manager
from torrent_info import get_info
from subtitle.opensubtitle import opensubtitle

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

def start_search(tracker, query, queryResult):
    """
    Funtion used to make tracker query easier (the tracker module can just send
    back a dict and don't have to mess with the dict)
    """
    result = tracker().search_torrent(query)
    if result:
        # If they are result to display else no need to include it in
        # the dict
        queryResult[tracker] = result


def main(option):
    # trackers = json.load('trackers.json')
    # TODO Should find a way to import all of the trackers
    from trackers.torrentz import torrentz
    from trackers.kat import kat

    trackers = [torrentz, kat]

    manager = Manager()
    tmpResult = manager.dict()
    processes = []

    for x in trackers:
        # Create all processes and stock them in a list to be sure that
        # they are all finished.
        print("Searching %s with %s" % (option.search, x))
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
    while i < option.number_of_output and queryResult:
        # while there is torrent to display.
        maxSeeds = max(queryResult,
                       key=lambda x: int(queryResult[x][0]['seeds'])
                       )
        # Find the torrent with the most seeder trough all tracker result.
        # It's basicly a merge of all the result of the trackers.
        out = queryResult[maxSeeds].pop(0)
        if not len(queryResult[maxSeeds]):
            # If the list is empty delete so they are no error
            del queryResult[maxSeeds]

        # TODO Add the reference here
        # out["ref"] = maxSeeds # Set a reference so the program can call the
                              # class later.

        outputList.append(out)

        print('%2i| % 50s | Size:% 9s | S:% 5s | P:% 5s' %
              (i,
               out['title'] if len(out['title']) < 50 else out['title'][:50],
               #bcolors.UNDERLINE + out['size'] + bcolors.ENDC,
               out['size'],
               #bcolors.BOLD + bcolors.BLUE + out['seeds'] + bcolors.ENDC,
               out['seeds'],
               out['peers']
               )
              )
        i += 1

    if not outputList:
        # If no result found
        print("No result found, exiting...")
        exit()

    # ASKING the user wich torrent he want to retrive.
    try:
        print("Enter the torrent number you want to get. ", end="")
        torrentNum = input()

    except KeyboardInterrupt:
        print("\nExiting.")
        exit()

    if (not torrentNum.isdigit() or int(torrentNum) > len(outputList)):
        # Good  value check.
        print("Exiting.")
        exit()
    else:
        torrentNum = int(torrentNum)

    pageLink = outputList[torrentNum]
    torrentLink = pageLink['link']

    ###############################################################
    # Getting the torrent.
    # Use magne link to save the torrent.
    ref = pageLink['ref']  # Reference to the tracker.
    magnetLink = ref.get_magnet(torrentLink)

    ###############################################################
    # Getting the torrent metadata.
    info = get_info(magnetLink, option.destdir)
    # TODO add the aptitude to save the torrent.

    ###############################################################
    # Getting the subtitle.
    if option.subtitle:
        os = opensubtitle()
        print("Getting the subtitle from OpenSubtitle...", end="  ")
        # TODO Add a better support for multifiles torrents.
        fileInfo = info[0]
        # For now we wiil just use the first one
        subtitle = os.get_subtitle(fileInfo['name'],
                                   option.language,
                                   fileInfo['length'],
                                   option.destdir)
        # TODO ADD SIZE
        print("Saved as " + subtitle)

    # Launch peerflix
    command = "peerflix '%s' --%s --path %s --subtitles %s"\
        % (magnetLink, option.player, option.destdir, subtitle)
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
        # remove = raw_input("Do you want to remove the file ? [(y)es/(n)o]")
        print("Do you want to remove the file ? [(y)es/(n)o] ", end="")
        remove = sys.stdin.readline().strip()
        if remove.lower() in ['yes', 'y', 'ye', 'ys']:
            toRemove = info[0]['folder']
            if toRemove is None:
                toRemove = info[0]['name']
            os.remove(toRemove)

    except:
        print('Peerflix is not installed, please type the following command'
              + ' to install it (if npm is installed):')
        print('sudo npm install -g peerflix')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    config = parse_config()  # User config file
    default = parse_default()  # Default config file

    try:
        parser.add_argument('search',
                            nargs='?',
                            default=None,
                            type=str
                            )

        ####################################################################
        try:
            defaultDestdir = config.get('general', 'destdir')
        except:
            # If no argument.
            print('No destination dir specified in the config file.')
            defaultDestdir = default.get('general', 'destdir')
            print('Using: ' + defaultDestdir)

        parser.add_argument('-d', '--destdir',
                            default=defaultDestdir,
                            type=str,
                            help='Destination of the downloaded torrent'
                            )

        ####################################################################
        try:
            defaultMagnet = config.getboolean('general', 'magnet')
        except:
            # If no argument.
            print('No magnet preference specified in the config file.')
            defaultMagnet = default.getboolean('general', 'magnet')
        actionMagnet = "store_false" if defaultMagnet else "store_true"

        parser.add_argument('-m', '--magnet',
                            default=defaultMagnet,
                            action=actionMagnet,
                            help=("Use magnet link (no torrent download.")
                            )
        # This option will call the get_magnet option of a tracker.
        # instead of the .download one.

        ####################################################################
        try:
            defaultPlayer = config.get('general', 'player')
        except:
            # If no argument.
            print('No player specified in the config file.')
            defaultPlayer = default.get('general', 'player')

        parser.add_argument('-p', '--player',
                            default=defaultPlayer,
                            type=str,
                            help=("Choose the player you want to use to watch"
                                  + " your streamed torrent")
                            )

        ####################################################################
        try:
            defaultLang = config.get('general', 'language')
        except:
            # If no argument.
            print('No language specified in the config file.')
            defaultLang = default.get('general', 'language')

        parser.add_argument('-l', '--language',
                            default=defaultLang,
                            type=str,
                            help=("Set the language you want to use for the "
                                  + "subtitles")
                            )

        ####################################################################
        try:
            defaultSub = config.getboolean('general', 'subtitle')
        except:
            # If no argument.
            print('No subtitle option specified in the config file.')
            defaultSub = default.getboolean('general', 'subtitle')
        actionSub = "store_false" if defaultSub else "store_true"

        parser.add_argument('-s', '--subtitle',
                            default=defaultSub,
                            action=actionSub,
                            help=("Make the program download subtitle (or not "
                                  + "if the option is already set to 'True'  in"
                                  + "your config file (default))")
                            )

        ####################################################################
        try:
            defaultNumber = config.get('general', 'number_of_output')
        except:
            # If no argument.
            print('No number_of_output specified in the config file.')
            defaultNumber = default.get('general', 'number_of_output')

        parser.add_argument('-out', '--number_of_output',
                            default=defaultNumber,
                            type=int,
                            help=("Set the number of torrent displayed with "
                                  + "your search.")
                            )

        ####################################################################
        parser.add_argument('-no', '--no_data',
                            default=False,
                            action='store_true',
                            help="No data are saved, stream goes into /tmp"
                            )

        option = parser.parse_args()

    except Exception as e:
        # Would happen if config file is lacking of argument
        print('Error parsing in the config file.')
        print(e)

    else:
        if option.search is None:
            # If the user entered no "search" option.
            print("Enter keywords you want to search: ", end="")
            option.search = input()

        if option.no_data:
            # option.magnet = True
            option.destdir = "/tmp"

        option.destdir = os.path.expanduser(option.destdir)
        main(option)
