from sudachipy import tokenizer
from sudachipy import dictionary

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def analyze_japanese(text):
    tokens = [m for m in tokenizer_obj.tokenize(text, mode)]
    return {
        'tokens': [token.surface() for token in tokens],
        'base_tokens': [token.normalized_form() for token in tokens]
    }