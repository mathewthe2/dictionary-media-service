from pathlib import Path
import os

bundle_path = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = Path(bundle_path, 'resources')
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
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

# Serving
MEDIA_FILE_HOST = 'https://media.immersionkit.com/media'
EXAMPLE_LIMIT = 100
RESULTS_LIMIT = 3000
NEW_WORDS_TO_USER_PER_SENTENCE = 1