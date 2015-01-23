### zflix
A python CLI to seek torrent on torrentz and directly stream them with peerflix.
Essentially based on gelim/torrentz repository (https://github.com/gelim/torrentz).

## Requirements
- item [python2](https://www.python.org/download/releases/2.7.8/)
- item [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) module
- item [peerflix](https://github.com/mafintosh/peerflix)

> npm install -g peerflix

## Usage
Type in the terminal
> python zflix.py -h

To show this help:
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
- item Implement an external file to write personal preference for the video player for example (mpv is used by default here)
