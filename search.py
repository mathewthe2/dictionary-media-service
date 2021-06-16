from wanakana import to_hiragana, is_japanese
from englishtokenizer import analyze_english, is_english_word
from japanesetokenizer import analyze_japanese, KANA_MAPPING
from config import EXAMPLE_LIMIT, RESULTS_LIMIT, NEW_WORDS_TO_USER_PER_SENTENCE
from tagger import Tagger
from decks import Decks
from dictionary import Dictionary
from dictionarytags import word_is_within_difficulty

tagger = Tagger()
tagger.load_tags()

dictionary = Dictionary()
dictionary.load_dictionary('JMdict+')

decks = Decks()
decks.load_decks()

def get_examples(text_is_japanese, words_map, text, word_bases, tags=[], user_levels={}, is_exact_match=False):
    results = [words_map.get(token, set()) for token in word_bases]
    if results:
        examples = [decks.get_sentence(example_id) for example_id in set.intersection(*results)]
        examples = filter_examples_by_tags(examples, tags)
        examples = filter_examples_by_level(user_levels, examples)
        if is_exact_match:
            examples = filter_examples_by_exact_match(examples, text)
        examples = limit_examples(examples)
        examples = parse_examples(examples, text_is_japanese, word_bases)
        return examples
    else:
        return []

def parse_examples(examples, text_is_japanese, word_bases):
    for example in examples:
        example['tags'] = tagger.get_tags_by_deck(example['deck_name'])
        example['word_index'] = []
        example['translation_word_index'] = []
        if text_is_japanese:
            example['word_index'] = [example['word_base_list'].index(word) for word in word_bases]
        else:
            example['translation_word_index'] = [example['translation_word_base_list'].index(word) for word in word_bases]
    return examples

def look_up(text, tags=[], user_levels={}):
    
    is_exact_match = '「' in text and '」' in text
    if is_exact_match:
        text = text.split('「')[1].split('」')[0]
    
    text_is_japanese = is_japanese(text) 
    if not text_is_japanese:
        if '"' in text: # force English search
            text = text.split('"')[1]
        else:  
            hiragana_text = to_hiragana(text, custom_kana_mapping=KANA_MAPPING)
            hiragana_text = hiragana_text.replace(" ", "") 
            if is_japanese(hiragana_text):
                text_is_english_word = " " not in text and is_english_word(text)  
                if not text_is_english_word:
                    text_is_japanese = True
                    text = hiragana_text
                else:
                    word_bases = analyze_japanese(hiragana_text)['base_tokens']
                    if len(word_bases) > 1:
                        text_is_japanese = False
                    else:
                        text_is_japanese = True
                        text = hiragana_text
                        # TODO: suggest english word in return query here
    
    dictionary_map = dictionary.get_dictionary_map()
    if not is_exact_match:
        is_word_in_dictionary = text_is_japanese and text in dictionary_map
        is_exact_match = is_word_in_dictionary
    words_map = decks.get_sentence_map() if text_is_japanese else decks.get_sentence_translation_map()
    text = text.replace(" ", "") if text_is_japanese else text
    word_bases = analyze_japanese(text)['base_tokens'] if text_is_japanese else analyze_english(text)['base_tokens']
    examples = get_examples(text_is_japanese, words_map, text, word_bases, tags, user_levels, is_exact_match)
    dictionary_words = [] if not text_is_japanese else [word for word in word_bases if word in dictionary_map]
    result = [{
        'dictionary': get_text_definition(text, dictionary_words),
        'examples': examples
    }]
    return dict(data=result)

def get_text_definition(text, dictionary_words):
    dictionary_map = dictionary.get_dictionary_map()
    if text in dictionary_map:
        return [dictionary.get_definition(text)]
    elif dictionary_words:
        return [dictionary.get_definition(word) for word in dictionary_words]
    else:
        return []

def filter_examples_by_tags(examples, tags):
    if len(tags) <= 0:
        return examples
    deck_names = tagger.get_decks_by_tags(tags)
    return [example for example in examples if example['deck_name'] in deck_names]

def filter_examples_by_level(user_levels, examples):
    if not user_levels:
        return examples
    new_examples = []
    for example in examples:
        new_word_count = 0
        for word in example['word_base_list']:
            dictionary_map = dictionary.get_dictionary_map()
            if word in dictionary_map:
                first_entry = dictionary_map[word][0]
                if not word_is_within_difficulty(user_levels, first_entry):
                    new_word_count += 1
        if new_word_count <= NEW_WORDS_TO_USER_PER_SENTENCE:
            new_examples.append(example)
    return new_examples

def filter_examples_by_exact_match(examples, text):
    return [example for example in examples if text in example['sentence']]

def limit_examples(examples):
    example_count_map = {}
    new_examples = []
    for example in examples:
        deck_name = example['deck_name']
        if deck_name not in example_count_map:
            example_count_map[deck_name] = 0
        example_count_map[deck_name] += 1
        if (example_count_map[deck_name] <= EXAMPLE_LIMIT):
            new_examples.append(example)
    return new_examples[:RESULTS_LIMIT]

