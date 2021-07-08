from wanakana import to_hiragana, is_japanese
from tokenizer.englishtokenizer import analyze_english, is_english_word
from tokenizer.japanesetokenizer import analyze_japanese, KANA_MAPPING
from config import DEFAULT_CATEGORY, EXAMPLE_LIMIT, RESULTS_LIMIT, NEW_WORDS_TO_USER_PER_SENTENCE
from tagger import Tagger
from decks.decksmanager import DecksManager
from dictionary import Dictionary
from dictionarytags import word_is_within_difficulty

tagger = Tagger()
tagger.load_tags()

dictionary = Dictionary()
dictionary.load_dictionary('JMdict+')

decks = DecksManager()
decks.load_decks()

def get_deck_by_id(deck_name, category=DEFAULT_CATEGORY):
    decks.set_category(category)
    return dict(data=decks.get_deck_by_name(deck_name))

def get_sentence_by_id(sentence_id, category=DEFAULT_CATEGORY):
    decks.set_category(category)
    return decks.get_sentence(sentence_id)

def deconstruct_combinatory_sentence_id(sentence_id):
    if '-' in sentence_id:
        print(sentence_id)
        return {
            'category': sentence_id.split('-', 1)[0],
            'example_id': sentence_id.split('-', 1)[1]
        }
    else:
        return None

def get_sentences_with_combinatory_ids(combinatory_sentence_ids):
    result = []
    for combinatory_sentence_id in combinatory_sentence_ids:
        sentence = deconstruct_combinatory_sentence_id(combinatory_sentence_id)
        if sentence:
            result.append(get_sentence_by_id(sentence['example_id'], sentence['category'].lower()))
    return dict(data=result)

def get_sentence_with_context(sentence_id, category=DEFAULT_CATEGORY):
    sentence = get_sentence_by_id(sentence_id, category)
    if sentence is None:
        return None
    sentence["pretext_sentences"] = [get_sentence_by_id(sentence_id) for sentence_id in sentence["pretext"]]
    sentence["posttext_sentences"] = [get_sentence_by_id(sentence_id) for sentence_id in sentence["posttext"]]
    return sentence

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
        return filter_fields(examples, excluded_fields=["image", "sound", "translation_word_base_list", "word_base_list", "pretext", "posttext"])
    else:
        return []

def filter_fields(examples, excluded_fields):
    filtered_examples =[]
    for example in examples:
        filtered_example= {}
        for key in example:
            if key not in excluded_fields:
                filtered_example[key] = example[key]
        filtered_examples.append(filtered_example)
    return filtered_examples

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

def look_up(text, sorting, category=DEFAULT_CATEGORY, tags=[], user_levels={}):

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
    
    if not is_exact_match:
        is_word_in_dictionary = text_is_japanese and dictionary.is_entry(text)
        is_exact_match = is_word_in_dictionary
    decks.set_category(category)
    words_map = decks.get_sentence_map() if text_is_japanese else decks.get_sentence_translation_map()
    text = text.replace(" ", "") if text_is_japanese else text
    word_bases = analyze_japanese(text)['base_tokens'] if text_is_japanese else analyze_english(text)['base_tokens']
    examples = get_examples(text_is_japanese, words_map, text, word_bases, tags, user_levels, is_exact_match)
    if sorting:
        examples = sort_examples(examples, sorting)
    dictionary_words = [] if not text_is_japanese else [word for word in word_bases if dictionary.is_entry(word)]
    result = [{
        'dictionary': get_text_definition(text, dictionary_words),
        'examples': examples
    }]
    return dict(data=result)

def sort_examples(examples, sorting):
    if sorting.lower() == 'sentence length':
        return sorted(examples, key=lambda example: len(example['sentence']))
    return examples

def get_text_definition(text, dictionary_words):
    if dictionary.is_entry(text):
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
            if dictionary.is_entry(word):
                first_entry = dictionary.get_first_entry(word)
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