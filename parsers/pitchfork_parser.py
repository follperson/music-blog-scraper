#!/usr/bin/env python3
from parsers._abstract import AbstractParser
from parsers import Static
from cleaners import TextCleaners
from utils import merge_dicts
from typing import Callable

class PitchforkArticleDownloader(AbstractParser):
    class SearchPages:
        class FUNC:
            def FEATURE(self, soup):
                node_class = 'title-link module__title-link'
                return [node['href'] for node in soup.find_all('a', {'class': node_class})]

            def ALBUMS(self, soup):
                node_class = 'review__link'
                return [node['href'] for node in soup.find_all('a', {'class': node_class})]

            def TRACKS(self, soup):
                node_classes = ['title-link', 'track-collection-item__track-link']
                return [node['href'] for node_class in node_classes for node in soup.find_all('a', {'class': node_class})]

        class SLUG:
            FEATURE = 'features'
            ALBUMS = 'reviews/albums'
            TRACKS = 'reviews/tracks'

        ALL = (SLUG.FEATURE, SLUG.ALBUMS, SLUG.TRACKS)

    class ExcludeLinkFlags:
        LISTS = 'lists-and-guides'
        PODCAST = 'podcast'
        PHOTOGALLERY = 'photo-gallery'
        SPONSORED = 'from-our-partners'
        PFEST = 'pitchfork-music-festival'
        FEST = 'festival-report'
        ALL = [LISTS, PODCAST, PHOTOGALLERY, SPONSORED, PFEST, FEST]

    def __init__(self,
                 name: str = 'Pitchfork',
                 search_page: str = SearchPages.SLUG.ALBUMS,
                 search_page_function: Callable = SearchPages.FUNC.ALBUMS,
                 search_limit: int = 2,
                 start_page: int = 1,
                 ):
        assert search_page in self.SearchPages.ALL
        base_url = 'https://pitchfork.com'
        exclude_link_flags = self.ExcludeLinkFlags.ALL

        # parse functions as a dictionary with the key being the string name of the object, and the value being a
        # tuple of length two with the function at the first index and the kwargs as the second.
        parse_functions = {Static.TITLE: (self.get_title, {}),
                           Static.BODY: (self.get_article_body, {}),
                           Static.DATEPUBLISHED: (self.get_date_pub, {}),
                           }

        if search_page in [self.SearchPages.SLUG.ALBUMS, self.SearchPages.SLUG.TRACKS]:
            parse_functions.update({
                Static.GENRE: (self.get_genre, {}),
                Static.LABEL: (self.get_label, {})
            })

        if search_page == self.SearchPages.SLUG.ALBUMS:
            parse_functions.update({
                Static.RATING: (self.get_review_score, {}),
                Static.ARTIST: (self.get_artist, {}),
                Static.ALBUM: (self.get_album, {}),
            })
        elif search_page == self.SearchPages.SLUG.TRACKS:
            parse_functions.update({
                Static.SONGNAME: (self.get_song_name, {}),
                Static.ARTIST: (self.get_artist_track, {}),
            })
        elif search_page == self.SearchPages.SLUG.FEATURE:
            parse_functions.update({
                Static.ARTICLETYPE: (self.get_article_type, {})
            })

        cleaner = TextCleaners.PitchforkCleaner
        super(PitchforkArticleDownloader, self).__init__(name=name,
                                                         base_url=base_url,
                                                         search_page=search_page,
                                                         search_page_function=search_page_function,
                                                         parse_functions=parse_functions,
                                                         search_limit=search_limit, start_page=start_page,
                                                         exclude_link_flags=exclude_link_flags,
                                                         cleaner=cleaner
                                                         )

    def parse_search_page(self, soup, func):
        links = func(self=self, soup=soup)
        return filter(lambda x: all(exclude not in x for exclude in self.exclude_link_flags), links)

    def get_author(self, soup):
        authors = ', '.join([node.text for node in soup.find_all('a', {'class': 'authors-detail__display-name'})])
        if len(authors) == 0:
            try:
                authors += soup.find('ul', {'class': 'authors-detail'}).find_next('li').text
                print(authors)
            except Exception:
                authors = self.name + ' Generic'
        return authors

    def get_genre(self, soup):
        return [genre_link.text for genre_link in soup.find_all('a', {'class': 'genre-list__link'})]

    def get_artist(self, soup):
        return [artist_link.text for artist_link in
                soup.find('hgroup', {'class': 'single-album-tombstone__headings'}).find_all('a')]

    def get_artist_track(self, soup):
        return [artist_link.text for artist_link in soup.find_all('ul', {'class':'artist-links'})]

    def get_album(self, soup):
        return soup.find('h1', {'class': 'single-album-tombstone__review-title'}).text

    def get_title(self, soup):
        return soup.find('title').text

    def get_song_name(self, soup):
        return soup.find('h1',{'class':'title'}).text

    def get_label(self, soup):
        return soup.find('li', {'class': 'labels-list__item'}).text


    def get_article_body(self, soup):
        return [p.text for p in soup.find_all('p')]

    def get_review_score(self, soup):
        return soup.find('span', {'class':'score'}).text

    def get_date_pub(self, soup):
        node = soup.find('time',{'class':"pub-date"})
        for want in ['datetime', 'title']:
            try:
                return node[want]
            except KeyError as ok:
                pass
        return node.text

    def get_article_type(self, soup):
        return soup.find('a', {'class':"type"}).text

