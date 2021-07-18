# Dictionary Media Service

Provides full-text search for Japanese and English text in Anki decks.

## Prerequisities

### [Echant](https://abiword.github.io/enchant/)

#### Mac
```bash
brew install enchant
```

#### Ubuntu
```
apt-get install enchant

```

## Connect to Redis 

Add **REDIS_URL=[Your Redis Connection URL]** to `config.py`

## Develop

```bash
python -m venv .env
source .env/bin/activate
pip install -u pip setuptools wheel
pip install -r requirements.txt
python -m spacy download en
python main.py
```
## Features

- Parse JSON Anki decks exported from CrowdAnki
- Tokenize decks for Japanese, English, and Romaji lookup
- Filer decks by tags
- Filter text by JLPT and WK tags in JMdict+ dictionary

## Run

```bash
python main.py
```

## Add a Deck

1. Export the deck to JSON with [CrowdAnki](https://ankiweb.net/shared/info/1788670778) to the folder */resources/anime/*
2. Add a *deck-structure.json* to define the data of each column.

    ```json
    {
      "id-column": 0,
      "text-column": 1,
      "translation-column": 2,
      "text-with-furigana-column": 3,
      "image-column": 4,
      "sound-column": 5
    }
    ```
    
3. Add a *tags.json* file to the folder:

   ```json
    [
      "Action", 
      "Slice Of Life"
    ]
    ```
4. Parse the deck:

    ```python
    from deckparser import parse_deck 
    parse_deck('foldernameofyourdeck')
    ```
    This extracts media data from `deck.json`, adds tokenized word lists and exports to `data.json`.
    
## How to get decks

[Create a deck from Aozora Epub files](https://github.com/mathewthe2/Aozora-Epub-Extractor)

## Acknowledgements

[SudachiPy](https://github.com/WorksApplications/SudachiPy)

[spaCy](https://github.com/explosion/spaCy)

[wanakana-py](https://github.com/Starwort/wanakana-py)

[JMdict+](https://community.wanikani.com/t/yomichan-and-wanikanijlpt-tags/37535/14)

[genanki](https://github.com/kerrickstaley/genanki)

## References

[Python – Lemmatization Approaches with Examples](https://www.geeksforgeeks.org/python-lemmatization-approaches-with-examples/)

[Building a full-text search engine in 150 lines of Python code](https://bart.degoe.de/building-a-full-text-search-engine-150-lines-of-code/)
