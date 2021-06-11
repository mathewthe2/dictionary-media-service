from pathlib import Path
import os

bundle_path = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
MEDIA_FILE_HOST = 'https://media.immersionkit.com/media'
EXAMPLE_LIMIT = 20
RESULTS_LIMIT = 500
NEW_WORDS_TO_USER_PER_SENTENCE = 1