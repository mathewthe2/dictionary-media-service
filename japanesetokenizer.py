from sudachipy import tokenizer
from sudachipy import dictionary

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def get_base_form(word):
    word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(word, mode)]
    return word_base_list[0]

def analyze_japanese(text):
    tokens = [m for m in tokenizer_obj.tokenize(text, mode)]
    return {
        'tokens': [token.surface() for token in tokens],
        'base_tokens': [token.normalized_form() for token in tokens]
    }