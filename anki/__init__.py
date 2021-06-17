import genanki
import random
import requests
import os

# model_id = random.randrange(1 << 30, 1 << 31)

my_model = genanki.Model(
     1239585222,
    'Immersion Kit Default',
  fields=[
    {'name': 'ID'},
    {'name': 'Expression'},
    {'name': 'English'},
    {'name': 'Reading'},
    {'name': 'Screenshot'},
    {'name': 'Audio Sentence'},
  ],
  templates=[
    {
      'name': 'Sentence',
      'qfmt': '<h1>{{Expression}}</h1>{{Screenshot}}',
      'afmt': '{{FrontSide}}<hr id="answer"><div style="font-size: 20px">{{Audio Sentence}} {{furigana:Reading}}</div ><br/><div style="font-size: 20px">{{English}}</div>',
    },
  ])

def generate_deck(sentence):
  deck_id = random.randrange(1 << 30, 1 << 31)

  my_deck = genanki.Deck(
    deck_id,
    sentence['deck_name'])

  # Download Image
  response = requests.get(sentence["image_url"])
  image_file_name = "resources/images/{}".format(sentence["image"])
  file = open(image_file_name, "wb")
  file.write(response.content)
  file.close()

  # Download Sound
  response = requests.get(sentence["sound_url"])
  sound_file_name = "resources/sound/{}".format(sentence["sound"])
  file = open(sound_file_name, "wb")
  file.write(response.content)
  file.close()

  my_note = genanki.Note(
  model=my_model,
  fields=[
    sentence["id"], 
    sentence["sentence"], 
    sentence["translation"], 
    sentence["sentence_with_furigana"], 
    '<img src="{}">'.format(sentence["image"]), 
    '[sound:{}]'.format(sentence["sound"])
  ])

  my_deck.add_note(my_note)
  my_package = genanki.Package(my_deck)
  my_package.media_files = [image_file_name, sound_file_name]
  file_name = '{}.apkg'.format(sentence['id'])
  my_package.write_to_file('resources/decks/{}'.format(file_name))
  os.remove(image_file_name)
  os.remove(sound_file_name)
  return file_name
