import json
import logging
from datetime import datetime

import requests
import xmltodict
from bs4 import BeautifulSoup as BSoup

from .models import Headline
from .models import vocabulary


logger = logging.getLogger(__name__)

# # scratch code
import re
import math
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Get the list of English stop words
stop_words = stopwords.words("english")
custom_stop_words = [
    "post",
    "today",
    "news",
    "portal",
    "aarthiknews",
    "nepal",
    "kathmandu",
    "along",
    "two",
    "take",
    "nepali",
    "economic",
    "march",
    "one",
]


def clean_text(text):
    # Convert to lower case and remove non-alphanumeric character
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9]", "", text)

    # Common word with semantic meaning
    semantic_dictionary = {
        "game": ["run", "wicket", "icc", "cricket", "bat", "bowl", "series", "match", "cup", "sport", "odi", "t20", "toss",],
        "finance": ["gold", "tola", "silver", "rs", "billion", "price", "market", "tourist", ],
        "politics": ["election", "government", "minister", "maoist", "congress", "rpp", "nc", "party",],
        "environment": ["pollution", "fire", "forest", "polluted", "evs", "ev", "park", "earthquake", "earthquakes",],
    }

    # Replace common word with semantic
    for semantic, word_list in semantic_dictionary.items():
        for word in word_list:
            if text == word:
                return semantic
    return text


def lemmatize_word(word):
    # Convert all verb to v1
    lemma = WordNetLemmatizer()
    return lemma.lemmatize(word, "v")


def get_cosine_similarity(vec1, vec2):
    # Calculate the dot product
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))

    # Calculate the magnitudes
    magnitude1 = math.sqrt(sum(v**2 for v in vec1))
    magnitude2 = math.sqrt(sum(v**2 for v in vec2))

    # Calculate the cosine similarity
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    else:
        return dot_product / (magnitude1 * magnitude2)


def get_vector(sentence, vocab):
    # Calculate how many time each word of sentence is repeated
    sentence_token = [lemmatize_word(clean_text(word)) for word in sentence.split()]
    text_counter = Counter(sentence_token)

    # Select count of only those word present in vocabulary. (i.e all word of all news)
    vector = [text_counter[word] for word in vocab]

    return vector


def get_similar_news(news_id):
    # Get all headlines data excluding the user's news
    all_news_total_data = Headline.objects.exclude(id=news_id)

    # Convert news paragraph to lower case and remove special characters for all news
    all_news_vectors = [json.loads(news.vector) for news in all_news_total_data]

    # Get the user's news description
    user_news = Headline.objects.get(id=news_id)
    user_news_vector = json.loads(user_news.vector)

    similarities = [
        get_cosine_similarity(user_news_vector, vector) for vector in all_news_vectors
    ]

    # Sort indices based on similarity scores
    sorted_indices = sorted(
        range(len(similarities)), key=lambda x: similarities[x], reverse=True
    )

    # Include news with similarity more than 0.1 only
    sorted_indices = list(filter(lambda x:similarities[x] > 0.1, sorted_indices))

    similar_news_list = [all_news_total_data[i] for i in sorted_indices]
    logger.info(sorted_indices)
    similar_news_dictionary = {
        all_news_total_data[i].title: similarities[i] for i in sorted_indices
    }

    logger.info(f"Selected News: {user_news.title}")
    logger.info(f"Similarity Value: {similar_news_dictionary}")
    return similar_news_list


def scrape_news():
    feed_url_list = [
        "https://english.onlinekhabar.com/feed/",
        "https://enewspolar.com/feed/",
        "https://techspecsnepal.com/feed/",
        "https://www.prasashan.com/category/english/feed/",
        "https://english.ratopati.com/feed",
        "https://en.setopati.com/feed",
        "https://english.nepalpress.com/feed/",
        "https://techmandu.com/feed/",
        "https://english.aarthiknews.com/feed",
    ]

    for feed_url in feed_url_list:
        logger.info(f"Fetching news from: {feed_url}")
        try:
            response = requests.get(feed_url)
            content = response.content
            data_dict = xmltodict.parse(content)

            news_items = data_dict.get("rss", {}).get("channel", {}).get("item")
            for news in news_items:
                title = news["title"].strip("'\"`")

                # Get Description Text
                desc = news["description"]

                if not desc:
                    continue

                soup_desc = BSoup(desc, "html.parser")
                desc = soup_desc.get_text().strip("'\"`")
                news_source = (
                    feed_url.replace("https://", "")
                    .replace(".com/feed/", "")
                    .replace("english.", "")
                    .replace("www.", "")
                    .replace(".com/category/english/feed/", "")
                    .replace("/feed", "")
                    .replace(".com", "")
                    .replace("en.", "")
                )

                url = news["link"]
                pub_date = news["pubDate"]
                pub_date_format = datetime.strptime(
                    pub_date, "%a, %d %b %Y %H:%M:%S %z"
                )

                try:
                    # For onlinekhabar, newspolar, techkajak
                    if feed_url in (
                        "https://english.onlinekhabar.com/feed/",
                        "https://enewspolar.com/feed/",
                        "https://techspecsnepal.com/feed/",
                    ):
                        content = news.get("content:encoded")
                        soup = BSoup(content, "html.parser")
                        img_tag = soup.find("img")
                        img_src = img_tag.get("src")

                    elif feed_url in (
                        "https://techmandu.com/feed/",
                        "https://www.prasashan.com/category/english/feed/",
                    ):
                        news_resp = requests.get(url)
                        img_soup = BSoup(news_resp.content, "html.parser")
                        img_src = img_soup.find("figure").find("img")["src"]

                    # For Seto Pati and Ratopati
                    if feed_url in (
                        "https://english.ratopati.com/feed",
                        "https://en.setopati.com/feed",
                    ):
                        class_name = "featured-images"
                    elif feed_url == "https://english.nepalpress.com/feed/":
                        class_name = "featured-image"
                    elif feed_url == "https://english.aarthiknews.com/feed":
                        class_name = "td-post-featured-image"

                    news_resp = requests.get(url)
                    img_soup = BSoup(news_resp.content, "html.parser")
                    img_src = img_soup.find("div", class_=class_name).find("img")["src"]

                except Exception:
                    img_src = None

                if not img_src:
                    continue

                news_obj = Headline.objects.filter(url=url)
                if not news_obj.exists():
                    head_line_obj = Headline(
                        title=title,
                        description=desc,
                        url=url,
                        image=img_src,
                        pub_date=pub_date_format,
                        news_source=news_source,
                    )
                    head_line_obj.save()
        except Exception as e:
            logger.exception(f"Error fetching data from {feed_url}: {e}")
            continue
    logger.info("Fetching news completed")


def update_news_vector():
    vocab_count = dict()

    # Create News Vocabulary
    logger.info("Creating news vocabulary")
    for news_data in Headline.objects.all():
        for word in news_data.description.split():
            lematized_word = lemmatize_word(word)
            cleaned_word = clean_text(lematized_word)

            if (
                cleaned_word
                and cleaned_word not in stop_words
                and cleaned_word not in custom_stop_words
            ):
                vocab_count[cleaned_word] = vocab_count.get(cleaned_word, 0) + 1

    word_vocabulary = [
        vocab for vocab, occurence in vocab_count.items() if occurence > 1
    ]

    if vocabulary.objects.filter(identifier=1).exists():
        logger.info("Vocab Exist. Updating")
        vocabulary.objects.filter(identifier=1).update(word_vocab=word_vocabulary)
    else:
        vocabulary.objects.create(identifier=1, word_vocab=word_vocabulary)
        logger.info("Vocab Doesn't exist. Creating")

    logger.info("Creating Vector for each news")
    for news_data in Headline.objects.all():
        news_vector = get_vector(news_data.description, word_vocabulary)
        vector_json = json.dumps(news_vector)
        news_data.vector = vector_json
        news_data.save()
