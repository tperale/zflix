### zflix
A python CLI to seek torrent on torrentz and directly stream them with peerflix.
Essentially based on gelim/torrentz repository (https://github.com/gelim/torrentz).

## Requirements
- item python2
- item [feedparser](https://pypi.python.org/pypi/feedparser) module
- item [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html) module
- item [peerflix](https://github.com/mafintosh/peerflix)

> npm install -g peerflix

## Usage
Show this help:
> python zflix.py -h

>usage: zflix.py [-h] [-v] [-d DESTDIR] [-t TEAM] [-n] search
>
>positional arguments:
>  search
>
>optional arguments:
>  -h, --help            show this help message and exit
>  -v, --verbose         Show more information the execution
>  -d DESTDIR, --destdir DESTDIR
>                        Destination of the downloaded torrent

## TODO
- item Implement an external file to write personal preference for the video player (mpv is used by default here)
- item Get rid of BeautifulSoup module which is deprecated

