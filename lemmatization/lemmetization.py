from nltk.tokenize import word_tokenize
import string
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def lemmetize_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    words = word_tokenize(text)
    lemm_words = []
    for word in words:
        word = word.lower()
        word = word.translate(str.maketrans('', '', string.punctuation))
        if word not in stop_words:
            lemm_words.append(lemmatizer.lemmatize(word))
    return " ".join([word for word in lemm_words])

