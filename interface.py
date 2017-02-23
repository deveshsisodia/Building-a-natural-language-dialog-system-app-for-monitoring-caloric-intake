from db import DB
import nltk
import re
from speechProcessor import SpeechProcessor
from gtts import gTTS
import os
import warnings

warnings.filterwarnings("ignore")

class Interface:
    def __init__(self, complete_db_overhaul=False):
        if complete_db_overhaul:
            db_obj = DB()
            db_obj.update_db_full()
            db_obj.update_csv_objects_to_db()
        self.csv_objects_list = self._fill_csv_objects_list()
        self.food_tokens_set = set()
        self._create_food_tokens_set()
        self.cached_stop_words = nltk.corpus.stopwords.words('English')
        self.word_net_lemmatizer = nltk.stem.WordNetLemmatizer()

    def get_matched_tokens(self, query):
        result = []
        query_tokens_unigrams = query.split()
        query_tokens_bigrams = self._construct_bigrams(query_tokens_unigrams)
        query_tokens_trigrams = self._construct_trigrams(query_tokens_unigrams)
        print('Unigrams: {0}'.format(query_tokens_unigrams))
        print('Bigrams: {0}'.format(query_tokens_bigrams))
        print('Trigrams: {0}'.format(query_tokens_trigrams))
        for food_item in query_tokens_unigrams:
            if food_item in self.food_tokens_set:
                result.append(food_item)
            else:
                is_plural, singular = self._is_plural(food_item)
                if is_plural:
                    if singular in self.food_tokens_set:
                        result.append(singular)
        for food_item in query_tokens_bigrams:
            if food_item in self.food_tokens_set:
                result.append(food_item)
            else:
                is_plural, singular = self._is_plural(food_item)
                if is_plural:
                    if singular in self.food_tokens_set:
                        result.append(singular)
        for food_item in query_tokens_trigrams:
            if food_item in self.food_tokens_set:
                result.append(food_item)
            else:
                is_plural, singular = self._is_plural(food_item)
                if is_plural:
                    if singular in self.food_tokens_set:
                        result.append(singular)
        return result

    def get_audio_responses(self):
        speech_obj = SpeechProcessor()
        speech_audio = speech_obj.get_audio_from_mic()
        google_cloud_result = speech_obj.google_cloud_speech_recognizer(speech_audio)
        return google_cloud_result

    def get_user_name(self):
        tts = gTTS(text='Hello! Who am I speaking to?', lang='en')
        self.text_to_audio(tts, "intro")
        google_cloud_result = self._get_audio_response_and_extract_user_name()
        if len(google_cloud_result) > 0:
            name = google_cloud_result[0].split()[0]
            tts = gTTS(text='{0}, Did I get your name right? Say yes to confirm, No to try again'
                       .format(name), lang='en')
            self.text_to_audio(tts, "intro")
            result = self.get_audio_responses()
            result = result.lower().strip()
            if result in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct', 'sure']:
                tts = gTTS(text='Great! Nice to meet you, {0}'.format(name),
                           lang='en')
                self.text_to_audio(tts, "intro")
                return name
        tts = gTTS(text='Sorry! I did not understand your name. Let us try one more time. '
                        'May be try just your full name', lang='en')
        self.text_to_audio(tts, "intro")
        google_cloud_result = self._get_audio_response_and_extract_user_name()
        if len(google_cloud_result) > 0:
            name = google_cloud_result[0].split()[0]
            tts = gTTS(text='{0}, Did I get it right this time? Say yes to confirm'.format(name), lang='en')
            self.text_to_audio(tts, "intro")
            result = self.get_audio_responses()
            result = result.lower().strip()
            if result in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct', 'sure']:
                tts = gTTS(text='Great! Nice to meet you, {0}'.format(name),
                           lang='en')
                self.text_to_audio(tts, "intro")
                return name
        tts = gTTS(text='Sorry! I could not understand your name. For now, let me address you as, User', lang='en')
        self.text_to_audio(tts, "intro")
        return 'user'

    def remove_stop_words(self, word_list):
        filtered_words = [word for word in word_list if word not in self.cached_stop_words]
        return filtered_words

    def get_matched_food_results(self, tokens):
        result = set()
        for item in self.csv_objects_list:
            curr_item_tokens = item.food_tokens.split('-')
            for element in tokens:
                if element in curr_item_tokens:
                    result.add(item.food_tokens)
        return list(result)

    def _get_audio_response_and_extract_user_name(self):
        google_cloud_result = []
        cloud_result = self.get_audio_responses()
        if len(cloud_result) == 0:
            return  google_cloud_result
        google_cloud_result = self._match_name_from_template(cloud_result.lower())
        if len(google_cloud_result) == 0:
            google_cloud_result = self._get_human_names(cloud_result)
        if len(google_cloud_result) == 0:
            regex = re.compile('([A-Z]\w+(?=[\s\-][A-Z])(?:[\s\-][A-Z]\w+)+)',
                               re.UNICODE)
            google_cloud_result = regex.findall(cloud_result)
        if len(google_cloud_result) == 0:
            google_cloud_result.append(cloud_result)
        return google_cloud_result

    def _match_name_from_template(self, s):
        p = re.compile(r'(?:name is|i am|i\'m|call me|this is) (.*)')
        return p.findall(s)

    def text_to_audio(self, tts, file_name='dummy', delete_after_use='true'):
        tts.save(file_name + '.mp3')
        os.system("afplay {0}.mp3".format(file_name))
        if delete_after_use:
            os.remove(file_name + '.mp3')

    def _construct_bigrams(self, unigrams):
        bigrams = []
        if len(unigrams) < 2:
            return bigrams
        for i in range(1, len(unigrams)):
            bigrams.append(unigrams[i - 1] + unigrams[i])
        return bigrams

    def _is_plural(self, word):
        lemma = self.word_net_lemmatizer.lemmatize(word, 'n')
        plural = True if word is not lemma else False
        return plural, lemma

    def _construct_trigrams(self, unigrams):
        trigrams = []
        if len(unigrams) < 3:
            return trigrams
        for i in range(2, len(unigrams)):
            trigrams.append(unigrams[i - 2] + unigrams[i - 1] + unigrams[i])
        return trigrams

    def _fill_csv_objects_list(self):
        db_obj = DB()
        return db_obj.get_csv_objects_list()

    def _create_food_tokens_set(self):
        for csv_obj in self.csv_objects_list:
            for tokens in csv_obj.food_tokens.split('-'):
                self.food_tokens_set.add(tokens)
        print('Unique tokens: {0}'.format(len(self.food_tokens_set)))

    def _get_human_names(self, text):
        tokens = nltk.tokenize.word_tokenize(text)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary=False)
        person_list = []
        person = []
        name = ""
        for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
            for leaf in subtree.leaves():
                person.append(leaf[0])
            for part in person:
                name = name + part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
            person = []
        return (person_list)


if __name__ == '__main__':
    interface_obj = Interface()
    print("****************************************")
    print("*******Speech Based Dialog System*******")
    print("****************************************\n")
    speech_obj = SpeechProcessor()
    user_name = interface_obj.get_user_name()
    print('Final name: {0}'.format(user_name))
    tts = gTTS(text='Let us work on your caloric intake. What did you eat today, {0}? '
                    'Mention only the food item names.'.format(user_name), lang='en')
    # TODO: Convert the instance below into a robust dialog that ensures correct food item inputs from the user
    interface_obj.text_to_audio(tts, file_name="items")
    speech_audio = speech_obj.get_audio_from_mic()
    google_cloud_result = speech_obj.google_cloud_speech_recognizer(speech_audio)
    google_cloud_result = google_cloud_result.lower()
    second_tokens = interface_obj.get_matched_tokens(google_cloud_result)
    print("Before stop words removal:")
    print(second_tokens)
    second_tokens = interface_obj.remove_stop_words(second_tokens)
    print("After stop words removal:")
    print(second_tokens)

    # Result matching: TODO: Design a ranking mechanism and build on the dialog system accordingly.
    second_matched_results = interface_obj.get_matched_food_results(second_tokens)
    print(second_matched_results)








