import logging
import warnings
from collections import Counter
from datetime import datetime

import spacy
from nltk.corpus import stopwords
from transformers import logging as transformers_logging
from transformers import pipeline

warnings.filterwarnings("ignore", message="`resume_download` is deprecated and will be removed in version 1.0.0")

# Disable transformers library logging
transformers_logging.set_verbosity_warning()  # or set_verbosity_error()
transformers_logging.enable_explicit_format()

# Optional: Disable logging for the 'transformers' logger entirely
logging.getLogger('transformers').setLevel(logging.ERROR)
# Disable nltk library logging
logging.getLogger('nltk').setLevel(logging.ERROR)
# Disable spacy library logging
logging.getLogger('spacy').setLevel(logging.ERROR)
# Disable torch library logging
logging.getLogger('torch').setLevel(logging.ERROR)
# Disable sentencepiece library logging
logging.getLogger('sentencepiece').setLevel(logging.ERROR)

nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline("sentiment-analysis")
summarizer = pipeline("summarization")


class NlpUtils:
    content: str

    def __init__(self, content: str):
        self.content = content

    def emotional_analysis(self):
        result = sentiment_analyzer(self.content)
        sentiment = result[0]['label']
        score = result[0]['score']
        return sentiment, score

    def summarize(self):
        result = summarizer(self.content, max_length=50, min_length=25, do_sample=False)
        return result[0]['summary_text']

    @staticmethod
    def get_pretty_date():
        return datetime.now().strftime("%A, %B %d, %Y %I:%M %p")

    def generate_title(self):
        stop_words = set(stopwords.words('english'))
        doc = nlp(self.content)
        words = [token.text.lower() for token in doc if token.is_alpha and token.text.lower() not in stop_words]
        most_common_words = Counter(words).most_common(3)
        title = " ".join([word for word, _ in most_common_words])
        return title.capitalize()
