### zflix
[![GitHub issues](http://img.shields.io/github/issues/thomacer/zflix.svg?style=flat)](https://github.com/thomacer/zflix/issues)
[![Build Status](https://travis-ci.org/thomacer/zflix.svg?branch=master)](https://travis-ci.org/thomacer/zflix)

A python CLI to seek torrent and directly stream them with peerflix.

## Requirements
- [python2](https://www.python.org/download/releases/2.7.8/)
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) module
- [peerflix](https://github.com/mafintosh/peerflix)

> npm install -g peerflix

## Usage

>zflix.py [-h] [-d DESTDIR] [-m] [-p PLAYER] [-no NUMBER_OF_OUTPUT] search

positional arguments:                                     |
--------------------------------------------------------- | ------------------------------------------------------------
search                                                    |


optional arguments:                                       | Help message.
--------------------------------------------------------- | ------------------------------------------------------------
-h, --help                                                | Show this help message and exit.
-d DESTDIR, --destdir DESTDIR                             | Destination of the downloaded torrent.
-m, --magnet                                              | Use magnet link (no torrent download).
-p PLAYER, --player PLAYER                                | Choose the player you want to use to watch your streamed torrent.
-no NUMBER_OF_OUTPUT, --number_of_output NUMBER_OF_OUTPUT | Number of torrent displayed with your search.

## Example

>python2 zflix.py "Revolution OS"


## Want to contribute ?

It would be awesome !! Check out the wiki, you will find some documentation.

## License

[GPLv3](https://github.com/thomacer/zflix/blob/master/LICENSE).
