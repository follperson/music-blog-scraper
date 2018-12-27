#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.0.3'

class YourEDMArticleDownloader(object):
    def __init__(self, max_search=999):
        self.name = 'Your EDM'
        self.links = []
        self.max_search = max_search

    def scour_list_pages(self, soup):
        links = [node.find('a')['href'] for node in soup.find_all('h2', {'class': 'cb-post-title'})]
        self.links += links

    def get_pages(self):
        root_search = 'https://www.youredm.com/master-editorial'
        search = requests.get(root_search)
        soup = BeautifulSoup(search.content)
        page = 1
        while search.status_code != 404:
            if page > self.max_search:
                break
            soup = BeautifulSoup(search.content)
            self.scour_list_pages(soup)
            page += 1 # first page is 0, then second is 2
            search = requests.get(root_search + '/page/' + str(page))

    def get_article(self, soup):
        head = soup.find('title')
        title = head.text
        body = head.find_next('section')
        paragraphs = body.find_all_next('p',)
        text = []
        author = soup.find('span',{'class':'cb-author'}).text

        for p in paragraphs:
            try: # todo improve
                p['class']
            except KeyError as ignore:
                text.append(p.text)
        return title, author, text

    def scour_articles(self):
        data = []
        for link in self.links:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.content)
            try:
                t,a,d = self.get_article(soup)
            except Exception as huh:
                print('ERROR', huh,'\n'+link)
                continue
            data.append([link,t,a,d])
            # print(t)
        self.df_articles = pd.DataFrame(data, columns=['url','Title','Author','Body'])

    def main(self):
        self.get_pages()
        self.scour_articles()



def post_processing(body):
  in_line = {'\xa0',' '}
  body_replaces = [' ','']



def scrub_title(text, scrub):
    return text.replace(scrub,'')


class ArticleDownloader(object):
    pass


class PitchforkArticleDownloader(object):
    class ArticleTypes:
        FEATURE = 'features'
        REVIEW = 'reviews'

    class ExcludeLinkFlags:
        LISTS = 'lists-and-guides'
        PODCAST = 'podcast'
        PHOTOGALLERY = 'photo-gallery'
        SPONSORED = 'from-our-partners'
        FEST = 'pitchfork-music-festival'
        ALL = [LISTS, PODCAST, PHOTOGALLERY, SPONSORED, FEST]

    def __init__(self, max_search=999):
        self.name = 'Pitchfork'
        self.links = []
        self.root_website = 'https://www.pitchfork.com'
        self.max_search = max_search

    def scour_list_pages(self, soup, article_type):
        if article_type == self.ArticleTypes.FEATURE:
            class_name ='title-link module__title-link'
        elif article_type == self.ArticleTypes.REVIEW:
            class_name = 'review__link'
        else:
            print('what feature type')
            return

        links = [self.root_website + node['href'] for node in soup.find_all('a', {'class': class_name})]
        links = filter(lambda x: all(exclude not in x for exclude in self.ExcludeLinkFlags.ALL), links)
        self.links += links

    def get_article_list(self, article_type):
        root_search = self.root_website +'/' + article_type + '/?page='
        page = 1
        search = requests.get(root_search + str(page))
        soup = BeautifulSoup(search.content)
        while search.status_code != 404:
            if page > self.max_search:
                break
            print(page)
            self.scour_list_pages(soup, article_type)
            page += 1 # first page is 0, then second is 2
            search = requests.get(root_search + str(page))
            soup = BeautifulSoup(search.content)

    # def get_article_author(self, soup):
    #     for method in self.SoupMethods.AUTHOR:
    #         ', '.join([node.text for node in soup.find_all('a', {'class': 'authors-detail__display-name'})])

    def get_article(self, soup):
        head = soup.find('title')
        title = head.text
        # title = scrub_title(head.text,' | Your EDM')
        paragraphs = soup.find_all('p')[:-1]
        text = []

        authors = ', '.join([node.text for node in soup.find_all('a',{'class':'authors-detail__display-name'})])
        # try:
        #     soup.find('ul', {'class': 'authors-detail'}).find_next('li').text
        #     authors +=
        # except Exception:
        #     pass
        try:
            assert len(authors) > 0,'No Author %s' % title
        except AssertionError:
            print('No Author %s' % title)
            authors = 'Pitchfork'
        for p in paragraphs:
            try:
                text.append(p.text)
            except KeyError as ignore:
                pass
        return title, authors, text

    def scour_articles(self):
        data = []
        for link in self.links:
            try:
                resp = requests.get(link)
            except (requests.exceptions.ConnectionError):
                resp = requests.get(link[len(self.root_website):])
            soup = BeautifulSoup(resp.content)
            t,a,d = self.get_article(soup)
            data.append([link,t,a,d]) # pub date
            # print(t)
        self.df_articles = pd.DataFrame(data, columns=['url','Title','Author','Body'])

    def main(self):
        self.get_article_list(self.ArticleTypes.FEATURE)
        self.get_article_list(self.ArticleTypes.REVIEW)
        self.scour_articles()

if __name__ == '__main__':
    pass