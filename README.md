### zflix
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
>usage: zflix.py [-h] [-v] [-d DESTDIR] [-t TEAM] [-n] search
>
>positional arguments:
>  search
>
>optional arguments:
>  -h, --help            show this help message and exit.
>  -p --player           Choose the player you want to use to watch your
                         streamed torrent.
>  -d --destdir          Destination of the downloaded torrent.
>  -n --not_verified     Option to do unverified search.

## TODO
- Add the possibility to download subtile.
- Auto remove the torrent downloaded at the end of the stream.
- Find a way to only output streamable movie/show from a search request on torrentz.
- Some link in the feed, send you to 404'd pages.
- If no torrent is found, do not launch peerflix
