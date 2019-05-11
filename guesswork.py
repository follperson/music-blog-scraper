#!/usr/bin/env python3
import markovify as mk
import pandas as pd
from get_articles import YourEDMArticleDownloader, PitchforkArticleDownloader
__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.0.2'


def look_at_edm():
    get_corpus(YourEDMArticleDownloader)



def make_random_article_newline(model):
    print('-------------------------------')
    print(model.make_sentence())
    print(model.make_sentence())
    print(model.make_sentence())
    print(model.make_sentence())
    print(model.make_sentence())



def look_at_pitchfork():
    get_corpus(PitchforkArticleDownloader)
    # get_corpus(PitchforkArticleDownloader,max_search=10)
#
def make_sentences(data):
    no_breaks = ' '.join([' '.join(article) for article in data])
    full_article_breaks = '\n'.join([' '.join(article) for article in data])
    paragraph_breaks = '\n'.join(['\n'.join(article) for article in data])
    for state in [2,3,4]:
        for model in [mk.Text(input_text=no_breaks, state_size=state),
                      mk.NewlineText(input_text=paragraph_breaks, state_size=state),
                      mk.NewlineText(input_text=full_article_breaks, state_size=state)]:
            print(state,model)
            make_random_article_newline(model=model)


def load_corpus_from_file(fp):
    df = pd.read_excel(fp)
    df['body-cleaned'] = df['body-cleaned'].apply(lambda x: eval(x))
    make_sentences(df['body-cleaned'].tolist())


def get_corpus(class_obj,**kwargs):
    obj = class_obj(**kwargs)
    obj.main()
    data = obj.df_articles['body-cleaned'].tolist()
    make_sentences(data)
    # make_random_article_newline(model=mk.Text(input_text=no_breaks, state_size=4))
    # make_random_article_newline(model=mk.NewlineText(input_text=paragraph_breaks, state_size=4))
    # make_random_article_newline(model=mk.NewlineText(input_text=full_article_breaks, state_size=4))
#
if __name__ == '__main__':
    # make_random_article_edm()
    # look_at_pitchfork()
    load_corpus_from_file('corpus/pitchfork_9999_tracks.xlsx')
    # load_corpus_from_file('corpus/pitchfork_9999_albums.xlsx')
    # load_corpus_from_file('corpus/pitchfork_9999_features.xlsx')
    # look_at_edm()