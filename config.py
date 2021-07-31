from pathlib import Path
import os

bundle_path = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = Path(bundle_path, 'resources')
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
GAMEGENGO_PATH = Path(bundle_path, 'resources', 'gamegengo')
LITERATURE_EXAMPLE_PATH = Path(bundle_path, 'resources', 'literature')

# Parsing
CONTEXT_RANGE = 10

# Decks
DEFAULT_CATEGORY = 'anime'
DECK_CATEGORIES = {
    'anime': {
        'path': EXAMPLE_PATH,
        'has_image': True,
        'has_sound': True
    },
    'literature': {
        'path': LITERATURE_EXAMPLE_PATH,
        'has_image': False,
        'has_sound': True
    }
} 

# Sentence Format
SENTENCE_FIELDS = [
    "id", 
    "deck_name",
    "deck_name_japanese", # literature
    "author_japanese", # literature
    "sentence",
    "sentence_with_furigana",
    "word_base_list",
    "word_list",
    "translation_word_list",
    "translation_word_base_list",
    "translation",
    "image",
    "sound",
    "sound_begin", # literature
    "sound_end", # literature
    "pretext",
    "posttext"
]

SENTENCE_KEYS_FOR_LISTS = ['pretext', 'posttext', 'word_list', 'word_base_list', 'translation_word_list', 'translation_word_base_list']

# Serving
MEDIA_FILE_HOST = 'https://immersion-kit.sfo3.digitaloceanspaces.com/media'
EXAMPLE_LIMIT = 100 # example limit per deck
RESULTS_LIMIT = 3000 # total result limit
SENTENCES_LIMIT = 999 # SQL-bound limit
NEW_WORDS_TO_USER_PER_SENTENCE = 1