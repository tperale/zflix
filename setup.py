try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='zflix', version='0.03',
    description='Script that seek and play torrent',
<<<<<<< HEAD
    long_description=('A CLI script that search through torrentz your'
                      + ' demand and play it with peerflix'),
    classifiers=[
        'Environment :: Console',
        'Operating System :: GNU/Linux',
        'Programming Language :: Python',
        'Topic :: Torrents',
    ],
    scipts = [
        'scripts/zflix',
    ],
=======
    long_description=('A CLI script that search '
                      + ' and play torrents with peerflix'),
>>>>>>> 39709c67a0406f449ea5107ddf97e07d0cb14bc4
    author='thomacer',
    author_email='thomas.perale@openmailbox.org',
    url='https://github.com/thomacer/zflix',
    license='GPL V2',
    install_requires=[
        'beautifulsoup4', # BeautifulSoup version 4
        'ConfigParser'
    ],
    packages=['src'],
)
