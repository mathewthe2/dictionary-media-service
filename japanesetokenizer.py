from sudachipy import tokenizer
from sudachipy import dictionary

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def normalize_japanese_word(word):
    return tokenizer_obj.tokenize(word, mode)[0].normalized_form()

def analyze_japanese(text):
    tokens = [m for m in tokenizer_obj.tokenize(text, mode)]
    return {
        'tokens': [token.surface() for token in tokens],
        'base_tokens': [token.normalized_form() for token in tokens]
    }