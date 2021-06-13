import spacy
import enchant 
import re
import string
nlp = spacy.load('en_core_web_sm')
vocabulary = enchant.Dict("en_US")

PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))

STOPWORDS = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                 'do', 'at', 'this', 'but', 'his', 'by', 'from'])

def analyze_english(text):
    # Create a Doc object
    doc = nlp(text)
    
    # Create list of tokens from given string
    tokens = []
    for token in doc:
        tokens.append(token)

    return {
        'tokens': [token.orth_ for token in tokens],
        'base_tokens': [token.lemma_ for token in doc]
    }

def is_english_word(word):
    return vocabulary.check(word)