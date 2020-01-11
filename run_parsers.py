#!/usr/bin/env python3
from parsers.pitchfork_parser import PitchforkArticleDownloader
from utils import random_wait
import os
__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.1.1'


def slowly_gather():
    max_range = 100000
    increment = 1
    name = 'Pitchfork Albums'
    search_page = PitchforkArticleDownloader.SearchPages.ALBUMS
    # name = 'Pitchfork Songs' # complete
    # search_pages = PitchforkArticleDownloader.SearchPages.TRACKS
    if increment != max_range:
        try:
            current_start_page = 1 + len([f for f in os.listdir('scraping\\' + name) if '.xlsx' in f]) * increment
        except FileNotFoundError:
            os.mkdir('scraping\\' + name)
            current_start_page = 1
        while current_start_page < max_range:
            print('Start Page %s' % current_start_page)
            parser = PitchforkArticleDownloader(name=name,
                                                start_page=current_start_page,
                                                search_limit=increment,
                                                search_page=search_page)
            parser.main()
            current_start_page += increment
    else:
        parser = PitchforkArticleDownloader(name=name,
                                            start_page=1,
                                            search_limit=max_range,
                                            search_page=search_page)
        parser.main()




def main():
    slowly_gather()


if __name__ == '__main__':
    main()
