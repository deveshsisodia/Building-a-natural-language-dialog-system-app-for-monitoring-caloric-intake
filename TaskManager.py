from TTSGenerator import TTSGenerator
from SpeechProcessor import SpeechProcessor
from NaturalLanguageProcessor import NaturalLanguageProcessor
from DialogTracer import DialogTracer
from DB import DB


class TaskManager:
    def __init__(self, complete_db_overhaul):
        self.speech_obj = SpeechProcessor()
        self.nlp_obj = NaturalLanguageProcessor()
        self.text_to_speech_obj = TTSGenerator()
        self.db_obj = DB()
        self.csv_objects_list = self._fill_csv_objects_list()
        if complete_db_overhaul:
            self.db_obj.update_db_full()
            self.db_obj.update_csv_objects_to_db()

    # Extract tokens from Audio
    def get_tokens_from_audio(self, input_text):
        second_tokens = self.get_matched_tokens(input_text)
        second_tokens = self.nlp_obj.remove_stop_words(second_tokens)
        return second_tokens

    # Converting Text to Audio
    def text_to_audio(self, input_text):
        print("\n[ASSISTANT QUERY]:")
        print(input_text)
        self.text_to_speech_obj.text_to_audio(input_text)

    # Convert Audio to Text
    def audio_to_text(self):
        print("\n[USER RESPONSE]:")
        response = self.speech_obj.audio_to_text()
        print(response)
        return response

    # Extracts user Name from Text
    def extract_user_name_from_text(self, user_input):
        return self.nlp_obj.extract_user_name_from_text(user_input)

    #
    def refractor_tokens_to_spoken_string(self, food_tokens):
        return self.nlp_obj.refractor_tokens_to_spoken_string(food_tokens)

    # Generate frequency of all the set of tokens of item in the Contener List
    def freq_generator(self, contender_list, token_set):
        dict_freq = {}
        if len(contender_list) == 0:
            return dict_freq
        for contender in contender_list:
            tokens = contender.split('-')
            for item in tokens:
                if item in dict_freq:
                    dict_freq.update({item: dict_freq[item] + 1})
                else:
                    dict_freq.update({item: 1})
        for token in token_set:
            del dict_freq[token]
        len_list = len(contender_list)
        del_list = []
        for key, value in dict_freq.items():
            if value >= len_list:
                del_list.append(key)
        for item in del_list:
            del dict_freq[item]
        self.nlp_obj.remove_stop_words_dict(dict_freq)
        dict_freq = self._filter_small_words(dict_freq)
        # sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
        return dict_freq

    # Getting Matching Tokens
    def get_matched_tokens(self, query):
        result = []
        food_tokens_set = self._create_food_tokens_set()
        query_tokens_unigrams = query.split()
        query_tokens_bigrams = self.nlp_obj.construct_bigrams(query_tokens_unigrams)
        query_tokens_trigrams = self.nlp_obj.construct_trigrams(query_tokens_unigrams)
        for food_item in query_tokens_unigrams:
            if food_item in food_tokens_set:
                result.append(food_item)
            else:
                is_plural, singular = self.nlp_obj.get_singular(food_item)
                if is_plural:
                    if singular in food_tokens_set:
                        result.append(singular)
        for food_item in query_tokens_bigrams:
            if food_item in food_tokens_set:
                result.append(food_item)
            else:
                is_plural, singular = self.nlp_obj.get_singular(food_item)
                if is_plural:
                    if singular in food_tokens_set:
                        result.append(singular)
        for food_item in query_tokens_trigrams:
            if food_item in food_tokens_set:
                result.append(food_item)
            else:
                is_plural, singular = self.nlp_obj.get_singular(food_item)
                if is_plural:
                    if singular in food_tokens_set:
                        result.append(singular)
        return result

    # Getting the Set of Contender that match a set of tokens
    def get_fully_matched_food_results(self, tokens):
        result = set()
        token_len = len(tokens)
        for item in self.csv_objects_list:
            curr_item_tokens = item.food_tokens.split('-')
            c = 0
            for element in tokens:
                if element in curr_item_tokens:
                    c += 1
            if c == token_len:
                result.add(item.food_tokens)
        return list(result)

    # Reduce the list of Contender and freq item when user select a descriptor corresponding to its food item
    def reduce_list(self, contender_list, response, dict_freq):
        new_list = []
        for contender in contender_list:
            tokens = contender.split('-')
            if response in tokens:
                new_list.append(contender)
        contender_list = new_list

        for key, value in dict_freq.items():
            dict_freq[key] = 0

        for contender in contender_list:
            tokens = contender.split('-')
            for item in tokens:
                if item in dict_freq:
                    dict_freq.update({item: dict_freq[item] + 1})

        removal_list = []

        for key, value in dict_freq.items():
            if dict_freq[key] == 0 or dict_freq[key] >= len(contender_list):
                removal_list.append(key)

        for token in removal_list:
            del dict_freq[token]

        # for keys,values in dict_freq.items():
        # print(keys,"====",values)

        return new_list, dict_freq

    # When user select None of these those set of descriptors are removed
    # All set of contender corresponding to those descriptors are also removed
    def dict_contender_updator_for_none(self, dict_freq, token_set, contender_list):
        removal_list = []
        contender_removed = []
        new_contender_list = []
        for token in token_set:
            removal_list.append(token[0])

        for contender in contender_list:
            tokens = contender.split('-')
            for removed_token in removal_list:
                if removed_token in tokens:
                    contender_removed.append(contender)

        for contender in contender_list:
            if contender not in contender_removed:
                new_contender_list.append(contender)

        for key, value in dict_freq.items():
            dict_freq[key] = 0

        for contender in new_contender_list:
            tokens = contender.split('-')
            for item in tokens:
                if item in dict_freq:
                    dict_freq.update({item: dict_freq[item] + 1})

        for key, value in dict_freq.items():
            if dict_freq[key] == 0 or dict_freq[key] >= len(new_contender_list):
                removal_list.append(key)

        for token in removal_list:
            if token in dict_freq:
                del dict_freq[token]

        if len(new_contender_list) == 0:
            return contender_list[:1], dict_freq

        contender_list = new_contender_list

        # for keys,values in dict_freq.items():
        # print(keys,"====",values)
        print('dict_size  :', len(dict_freq))
        # sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
        return contender_list, dict_freq

    # Reducing the Frequency Dictionary when user is not sure
    def reduce_list_for_no_match(self, sorted_list_freq, contender_list):
        rejected_token_list = []
        new_contender_list = []
        for item in sorted_list_freq:
            rejected_token_list.append(item[0])
        for contender in contender_list:
            c = 0
            for item in rejected_token_list:
                if item in contender:
                    c = 1
                    break
            if c == 0:
                new_contender_list.append(contender)
        return new_contender_list

    # Fill the SCV Objects List
    def _fill_csv_objects_list(self):
        return self.db_obj.get_csv_objects_list()

    # Creating Food Tokens Set
    def _create_food_tokens_set(self):
        food_tokens_set = set()
        for csv_obj in self.csv_objects_list:
            for tokens in csv_obj.food_tokens.split('-'):
                food_tokens_set.add(tokens)
        return food_tokens_set

    def _filter_small_words(self, dict_freq):
        del_list = []
        for key, value in dict_freq.items():
            if len(key) <= 2:
                del_list.append(key)
        for item in del_list:
            del dict_freq[item]
        return dict_freq

    # Extracting the quantity with the Standard Measure
    def extract(self, quan_list):
        items = quan_list.split(' ')
        standard = items[-1]
        quantity = items[-2]
        return standard, quantity

    # Displaying the Calorific intake of the food item
    def display_item(self, food_item):
        dict_food_item = {}
        print(food_item)
        for csv_obj in self.csv_objects_list:
            curr_item_tokens = csv_obj.food_tokens
            if food_item == curr_item_tokens:
                # print("Item is : ", food_item)
                # print("file_path  : ", csv_obj.file_path)
                # print("food_tokens  : ", csv_obj.food_tokens)
                # print("data_dict  : ", csv_obj.data_dict)
                nutrient = csv_obj.data_dict['Proximates']
                for item in nutrient:
                    if item[0] == 'Energy':
                        dict_food_item['Energy'] = item[2] + item[1]
                    if item[0] == 'Protein':
                        dict_food_item['Protein'] = item[2] + item[1]
                    if 'Carbohydrate' in item[0]:
                        dict_food_item['Carbohydrate'] = item[2] + item[1]
                    if 'Fiber' in item[0]:
                        dict_food_item['Fiber'] = item[2] + item[1]
                    if 'fat' in item[0]:
                        dict_food_item['Fat'] = item[2] + item[1]
                    if 'Sugars' in item[0]:
                        dict_food_item['Sugar'] = item[2] + item[1]
                nutri = csv_obj.data_dict['Nutrient']
                standard_specific, specific_quantity = self.extract(nutri[0][3])
                # print("Standard :  ",specific_quantity , "Standard  : ",standard_specific)
                standard, standard_quantity = self.extract(nutri[0][2])
                if specific_quantity == '=':
                    specific_quantity = standard_specific.split(standard)[0]
                dict_food_item['Standard Quantity'] = standard_quantity + standard
                # dict_food_item['Specific Quantity'] = specific_quantity
        for key, value in dict_food_item.items():
            print(key, " : ", value)
        # standard_quantity_no =
        unit = standard
        if standard == 'g':
            unit = 'gram'
        print()
        self.text_to_audio(
            "Intake of per {0} {1} of {2} will correspond to {3}".format(standard_quantity, unit, food_item,
                                                                         dict_food_item['Energy']))

