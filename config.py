from pathlib import Path
import os

bundle_path = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = Path(bundle_path, 'resources')
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
MEDIA_FILE_HOST = 'https://media.immersionkit.com/media'
EXAMPLE_LIMIT = 100
RESULTS_LIMIT = 3000
NEW_WORDS_TO_USER_PER_SENTENCE = 1