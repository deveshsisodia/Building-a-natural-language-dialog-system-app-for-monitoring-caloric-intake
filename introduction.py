from db import DB
import nltk
import re
from speechProcessor import SpeechProcessor
from gtts import gTTS
import os
import sys


class Introduction:
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
        self.speech_obj = SpeechProcessor()

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
        speech_audio = self.speech_obj.get_audio_from_mic()
        google_cloud_result = self.speech_obj.google_cloud_speech_recognizer(speech_audio)
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
                        'May be use your full name in a sentence', lang='en')
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

    def get_fully_matched_food_results(self, tokens):
        result = set()
        token_len = len(tokens)
        for item in self.csv_objects_list:
            curr_item_tokens = item.food_tokens.split('-')
            c = 0 
            for element in tokens:
                if element in curr_item_tokens:
                    c = c + 1
            if( c == token_len):
                result.add(item.food_tokens)
        return list(result)

    def _get_audio_response_and_extract_user_name(self):
        google_cloud_result = []
        cloud_result = self.get_audio_responses()
        if len(cloud_result) == 0:
            return google_cloud_result
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

    def get_tokens_from_audio(self):
        google_cloud_result = self.get_audio_responses().lower()
        second_tokens = self.get_matched_tokens(google_cloud_result)
        print("Before stop words removal:")
        print(second_tokens)
        second_tokens = self.remove_stop_words(second_tokens)
        print("After stop words removal:")
        print(second_tokens)
        second_matched_results = self.get_matched_food_results(second_tokens)
        return second_tokens, second_matched_results

    def get_output_confirm(self, token):
        text = ''
        l = len(token)
        if l == 1:
            text = text + token[0]
            return text
        for i in range(0, l - 1):
            text += ','
            text = text + token[i]
        text += ' and '
        text = text + token[l - 1]
        text = text[1:]
        return text

    def get_food_token_response(self, user_name, second):
        if second:
            tts = gTTS(text=' {0}, Mention the food items you had today '
                            'With more detail'.format(user_name), lang='en')
        else:
            tts = gTTS(text='Let us work on your caloric intake. What did you eat today, {0}? '
                            'Mention only the food item names.'.format(user_name), lang='en')
        self.text_to_audio(tts, file_name="items")

        food_token, food_token_result = self.get_tokens_from_audio()

        if len(food_token) == 0:
            tts = gTTS(text='Sorry {0}, '
                            'can you repeat the food items names again.'.format(user_name), lang='en')
            self.text_to_audio(tts, file_name="items")
            food_token, food_token_result = self.get_tokens_from_audio()

        if len(food_token) == 0:
            tts = gTTS(text='I am sorry {0}, '
                            'But the food items mentioned by you did not match my knowledge'.format(user_name),
                       lang='en')
            self.text_to_audio(tts, file_name="items")
            sys.exit()
        output = self.get_output_confirm(food_token)
        tts = gTTS(text='Based on My Knowledge'
                        'These are the food items consumed by you!'
                        '{0}.'.format(output), lang='en')
        self.text_to_audio(tts, file_name="items")
        return food_token, food_token_result, output

    def client_satisfaction(self, user, output):
        tts = gTTS(text='{0},Please acknowledge by saying yes'
                        'If all the food items are covered.'.format(user), lang='en')
        self.text_to_audio(tts, file_name="items")
        result = self.get_audio_responses()
        result = result.lower().strip()
        if result in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct', 'sure']:
            return True
        return False


    def start_introduction(self):
        #interface_obj = Introduction()
        print("****************************************")
        print("*******Speech Based Dialog System*******")
        print("****************************************\n")
        user_name = self.get_user_name()
        print('Final name: {0}'.format(user_name))
        food_token, food_token_result, food_token_text = self.get_food_token_response( user_name,
                                                                                               False)
        satisfied = self.client_satisfaction( user_name, food_token_text)
        if not satisfied:
            food_token, food_token_result, output = self.get_food_token_response( user_name, True)
            satisfied = self.client_satisfaction(user_name, food_token_text)
        if not satisfied:
            tts = gTTS(text='I am sorry {0}, '
                            'But the food items mentioned by you did not match my knowledge'.format(user_name),
                       lang='en')
            self.text_to_audio(tts, file_name="items")
            sys.exit()
        tts = gTTS(text='Following are the {0} items that match your description {1}'
                   .format(len(food_token_result), user_name), lang='en')
        self.text_to_audio(tts, file_name="items")
        # TODO: Display results based on a ranking mechanism
        print("Total matched items: {0}".format(len(food_token_result)))
        #print(food_token_result)
        tts = gTTS(text='Let me get more information from you about these items to figure out your exact intake', lang='en')
        self.text_to_audio(tts, file_name="items")
        return food_token, food_token_result, user_name
        # TODO: Enhance dialog system to reduce search space
