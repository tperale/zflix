### [zflix](http://thomacer.github.io/zflix)
[![GitHub issues](http://img.shields.io/github/issues/thomacer/zflix.svg?style=flat)](https://github.com/thomacer/zflix/issues)
[![Build Status](https://travis-ci.org/thomacer/zflix.svg?branch=master)](https://travis-ci.org/thomacer/zflix)

A python CLI to seek torrent and directly stream them with peerflix.

## Requirements
- [python3](https://www.python.org/downloads/release/python-342/)
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
-s, --subtitle              |  Make the program download subtitle (or not if the option is already set to "True"  in your config file (default))
  -l LANGUAGE, --language LANGUAGE     |      Set the language you want to use for the subtitles (see [here](http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes) in ISO 639-2/5 column to find your language).


## Example

>python3 zflix.py "Revolution OS"

![zflix screenshot](https://github.com/thomacer/zflix/blob/master/fig/screen.png)


## Want to contribute ?

It would be awesome !! Check out the [wiki](https://github.com/thomacer/zflix/wiki), you will find some documentation.

## License

[GPLv3](https://github.com/thomacer/zflix/blob/master/LICENSE).
