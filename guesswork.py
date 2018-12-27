#!/usr/bin/env python3
import markovify as mk
from get_articles import YourEDMArticleDownloader, PitchforkArticleDownloader
__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.0.1'


def look_at_edm():
    get_corpus(YourEDMArticleDownloader)



def make_random_article_newline(model):
    print('-------------------------------')
    print(model.make_sentence())
    print(model.make_sentence())
    print(model.make_sentence())
    print(model.make_sentence())
    print(model.make_sentence())



def look_at_pitcfork():
    get_corpus(PitchforkArticleDownloader)



def get_corpus(class_obj,**kwargs):
    obj = class_obj(**kwargs)
    obj.main()
    obj.df_articles.to_excel('corpus\\%s_%s.xlsx' %(obj.name, str(obj.max_search)))
    data = obj.df_articles['Body'].tolist()

    no_breaks = ' '.join([' '.join(article) for article in data])
    full_article_breaks = '\n'.join([' '.join(article) for article in data])
    paragraph_breaks = '\n'.join(['\n'.join(article) for article in data])
    for state in [2,3,4]:
        for model in [mk.Text(input_text=no_breaks, state_size=state),
                      mk.NewlineText(input_text=paragraph_breaks, state_size=state),
                      mk.NewlineText(input_text=full_article_breaks, state_size=state)]:
            print(state,model)
            make_random_article_newline(model=model)
    # make_random_article_newline(model=mk.Text(input_text=no_breaks, state_size=4))
    # make_random_article_newline(model=mk.NewlineText(input_text=paragraph_breaks, state_size=4))
    # make_random_article_newline(model=mk.NewlineText(input_text=full_article_breaks, state_size=4))
#
if __name__ == '__main__':
    # make_random_article_edm()
    # look_at_pitcfork()

    look_at_edm()