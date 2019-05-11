#!/usr/bin/env python3
from parsers.pitchfork_parser import PitchforkArticleDownloader
from utils import random_wait
import os
__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.1.1'


def slowly_gather():
    max_range = 10000
    increment = 5
    # name = 'Pitchfork Feature' # complete
    # search_pages = PitchforkArticleDownloader.SearchPages.FEATURE
    name = 'Pitchfork Albums'
    search_pages = PitchforkArticleDownloader.SearchPages.ALBUMS
    # name = 'Pitchfork Songs' # complete
    # search_pages = PitchforkArticleDownloader.SearchPages.TRACKS
    try:
        current_start_page = 1 + len([f for f in os.listdir('scraping\\' + name) if '.xlsx' in f]) * increment
    except FileNotFoundError:
        os.mkdir('scraping\\' + name)
        current_start_page = 1
    while current_start_page < max_range:
        print('Start Page %s' % current_start_page)
        parser = PitchforkArticleDownloader(name=name, start_page=current_start_page, search_limit=increment,search_pages=search_pages)
        parser.main()
        current_start_page += increment
        # random_wait(60)


def main():
    # get_all()
    slowly_gather()

if __name__ == '__main__':
    main()