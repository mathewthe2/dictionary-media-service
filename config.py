from pathlib import Path
import os

bundle_path = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
MEDIA_FILE_HOST = 'https://dictionary-media.netlify.app/media'
EXAMPLE_LIMIT = 20
CATEGORY_LIMIT = 100