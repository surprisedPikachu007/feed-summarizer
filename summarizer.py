import requests
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def filterEnergyFeed(articles: list) -> list:
    """
    return only the articles about science and technology
    """
    non_energy = ['actor', 'actors', 'movie', 'cinema']
    for article in articles:
        in_title = any(word in article.get('title').lower() for word in non_energy)
        in_description = any(word in article.get('description').lower() for word in non_energy)
        in_summary = any(word in article.get('summary').lower() for word in non_energy)

        if in_title or in_description or in_summary:
            articles.remove(article)


def htmlSummarizer(url: str, sentences_count: int, language: str = 'english') -> str:
    """
    Summarizes text from URL
    """
    parser = HtmlParser.from_url(url, Tokenizer(language))
    stemmer = Stemmer(language)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)

    summary = ''
    for sentence in summarizer(parser.document, sentences_count):
        if not summary:
            summary += str(sentence)
        else:
            summary += ' ' + str(sentence)

    return summary


def newsAPI(url: str, **kwargs) -> list:
    """
    Sends GET request to News API endpoint
    """
    params = kwargs
    res = requests.get(url, params=params)
    articles = res.json().get('articles')
    return articles


def summarizeArticles(articles: list, sentences_count: int) -> list:
    """
    Summarizes text at each URL in articles
    """
    for article in articles:
        summary = htmlSummarizer(article.get('url'), sentences_count)
        article.update({'summary': summary})

    return articles


def getLlatestArticles(sentences_count: int, **kwargs) -> list:
    """
    Sends GET request to News API /v2/top-headlines endpoint,
    """
    url = 'https://newsapi.org/v2/everything/?pageSize=10'
    articles = newsAPI(url, **kwargs)
    summaries = summarizeArticles(articles, sentences_count)
    filterEnergyFeed(summaries)

    return summaries
