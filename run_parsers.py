#!/usr/bin/env python3
from parsers.pitchfork_parser import PitchforkArticleDownloader
from utils import random_wait
import os
__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.1.0'


def slowly_gather():
    max_range = 10000
    increment = 1
    current_start_page = 1 + len([f for f in os.listdir('scraping') if '.xlsx' in f]) * increment

    while current_start_page < max_range:
        print('Start Page %s' % current_start_page)
        parser = PitchforkArticleDownloader(start_page=current_start_page, search_limit=increment)
        parser.main()
        current_start_page += increment
        random_wait(60)

def main():
    # get_all()
    slowly_gather()

if __name__ == '__main__':
    main()