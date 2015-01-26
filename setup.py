try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='zflix', version='0.02',
    description='Script that seek and play torrent',
    long_description=('A CLI script that search through torrentz your'
                      + ' demand and play it with peerflix'),
    author='thomacer',
    author_email='thomas.perale@gmail.com',
    url='https://github.com/thomacer/zflix',
    license='GPL V2',
    install_requires=[
        'beautifulsoup4', # BeautifulSoup version 4
        'ConfigParser'
    ],
    packages=['src'],
)
