import spacy
import re
import string
nlp = spacy.load('en_core_web_sm')

PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))

STOPWORDS = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                 'do', 'at', 'this', 'but', 'his', 'by', 'from'])

def analyze(text):
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