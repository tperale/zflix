### zflix
[![GitHub issues](http://img.shields.io/github/issues/thomacer/zflix.svg?style=flat)](https://github.com/thomacer/zflix/issues)
[![Build Status](https://travis-ci.org/thomacer/zflix.svg?branch=master)](https://travis-ci.org/thomacer/zflix)

A python CLI to seek torrent on torrentz and directly stream them with peerflix.
Essentially based on gelim/torrentz repository (https://github.com/gelim/torrentz).

## Requirements
- [python2](https://www.python.org/download/releases/2.7.8/)
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) module
- [peerflix](https://github.com/mafintosh/peerflix)

> npm install -g peerflix

## Usage
To show help type:
> python zflix.py -h

It will output:
>usage: zflix.py [-h] [-d DESTDIR] [-m] [-p PLAYER] [-no NUMBER_OF_OUTPUT] search
>
>positional arguments:
>  search
>
>optional arguments:
>  -h, --help            show this help message and exit.
    -d DESTDIR, --destdir DESTDIR
                          Destination of the downloaded torrent
    -m, --no_magnet       Use magnet link (no torrent download).
    -p PLAYER, --player PLAYER
                          Choose the player you want to use to watch your
                          streamed torrent
    -no NUMBER_OF_OUTPUT, --number_of_output NUMBER_OF_OUTPUT
                          Number of torrent displayed with your search.
