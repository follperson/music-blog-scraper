#!/usr/bin/env python3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from time import time as curtime, sleep
from datetime import date
import os
from utils import *
from cleaners import TextCleaners

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}

class AbstractParser(object):

    def __str__(self):
        return 'Blog Parser for ' + self.name

    def __init__(self, name, base_url, search_pages, parse_functions, search_limit=2, start_page=1,
                 exclude_link_flags=None, cleaner=TextCleaners.AbstractCleaner):
        self.name = name
        self.base_url = base_url
        self.search_pages = search_pages
        self.search_limit = search_limit
        self.start_page = start_page
        self.exclude_link_flags = exclude_link_flags if exclude_link_flags is not None else []
        self.parse_functions = parse_functions
        self.cleaner = cleaner
        self.HEADERS = HEADERS
        self.data = {}

    def get_urls_to_parse(self):
        for search_url_base in self.search_pages:
            search_url = self.base_url + '/' + search_url_base + '/?page='
            pageno = self.start_page
            search_page = self.get_url(search_url + str(pageno))
            soup = BeautifulSoup(search_page.content)
            while search_page.status_code != 404 and self.search_limit > (pageno - self.start_page):
                if search_page.status_code == 503:  # temporary off
                    random_wait(60)
                    continue
                soup = BeautifulSoup(search_page.content, features='lxml')
                links = self.parse_search_page(soup, self.search_pages[search_url_base])
                link_dict = {
                    self.base_url + url if self.base_url not in url else url: {'search_url_base': search_url_base} for
                    url in links}
                self.data.update(link_dict)
                pageno += 1
                random_wait(5)
                search_page = self.get_url(url=search_url + str(pageno))

    def get_author(self, soup):
        raise NotImplementedError

    def get_title(self, soup):
        raise NotImplementedError

    def get_article_body(self, soup):
        raise NotImplementedError

    def get_review_score(self, soup):
        raise NotImplementedError

    def get_date_pub(self, soup):
        raise NotImplementedError

    def get_article_type(self, soup):
        raise NotImplementedError

    def parse_search_page(self, soup, func):
        raise NotImplementedError('meant to be overwritten')

    def call_function(self, func, **kwargs):
        try:
            resp = func(**kwargs)
        except Exception as hmm:
            print(func.__name__, hmm)
            resp = 'Error'
        return resp

    def get_url(self, url):
        try:
            resp = requests.get(url, headers=HEADERS)
        except requests.exceptions.ConnectionError as nointernet:
            sleep(60)
            resp = self.get_url(url)
        if resp.status_code == 404:
            print("Cannot find %s" % url)
            return
        if resp.status_code == 503:
            random_wait(20)
            resp = requests.get(url, headers=HEADERS)
        return resp

    def parse_article_page(self, soup):
        data = dict()
        for name in self.parse_functions:
            func, kwargs_orig = self.parse_functions[name]
            kwargs = {'soup':soup}
            kwargs.update(kwargs_orig)
            data[name] = self.call_function(func, **kwargs)
        return data

    def collect_articles(self):
        folder = self.base_url.split('://')[-1].strip('.')
        for url in self.data:
            local_html ='html-downloads/%s/%s.html' % \
                        (folder, url.replace(self.base_url,'').strip('/').replace('/','-'))
            if len(local_html) > (255 - len(os.getcwd())):
                local_html = local_html[:255 - len(os.getcwd())]
            if os.path.exists(local_html):
                print("Using Local Copy %s" % url)
                with open(local_html, 'rb') as html:
                    content = html.read()
            else:
                print("Using live copy %s" % url)
                random_wait(5)
                resp = self.get_url(url)
                if resp is None:
                    continue
                content = resp.content
                if not os.path.exists(os.path.dirname(local_html)):
                    os.makedirs(os.path.dirname(local_html))
                with open(local_html, 'wb') as html:
                    html.write(content)
            soup = BeautifulSoup(content)
            try:
                info = self.parse_article_page(soup)
            except Exception as wow:
                print('Serious error with url %s, : %s' % (url, wow))
                continue
            self.data[url].update(info)


    def main(self):
        self.get_urls_to_parse()
        self.collect_articles()
        self.reformat_data()

    def reformat_data(self):
        df = pd.DataFrame().from_dict(self.data).T
        for col in self.cleaner['list']:
            df[col + '_cleaned'] = df[col].apply(lambda x: post_processing_list(x, self.cleaner['list'][col]))
        for col in self.cleaner['str']:
            df[col + '_cleaned'] = df[col].apply(lambda x: post_processing_element(x, self.cleaner['str'][col].INLINE))
        if not os.path.exists('scraping\\' + self.name):
            os.makedirs('scraping\\' + self.name)
        df.to_excel('scraping\\%s\\page %s to %s data scraping_%s.xlsx' % (
                    self.name, str(self.start_page), str(self.start_page + self.search_limit), str(date.today())))



if __name__ == '__main__':
    pass