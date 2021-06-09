# Dictionary Media Service

Provides full-text search for Japanese and English text in Anki decks.

## Develop
```bash
python -m venv .env
source .env/bin/activate
pip install -u pip setuptools wheel
pip install -r requirements.txt
python -m spacy download en
```

## Add a Deck

1. Export the deck to JSON with [CrowdAnki](https://ankiweb.net/shared/info/1788670778) to the folder */resources/anime/*
2. Parse the deck:

    ```python
    from deckparser import parse_deck 
    parse_deck('foldernameofyourdeck')
    ```
    This extracts media data from `deck.json`, adds tokenized word lists and exports to `data.json`.
    
3. Add a *tags.json* file to the folder:

    ```json
    [
      "Action", 
      "Slice Of Life"
    ]
    ```
    
## Acknolwedgements

[SudachiPy](https://github.com/WorksApplications/SudachiPy)

[spaCy](https://github.com/explosion/spaCy)

## References

[Python – Lemmatization Approaches with Examples](https://www.geeksforgeeks.org/python-lemmatization-approaches-with-examples/)

[Building a full-text search engine in 150 lines of Python code](https://bart.degoe.de/building-a-full-text-search-engine-150-lines-of-code/)
