import sys
from TaskManager import TaskManager
import operator


class DialogManager:
    def __init__(self, complete_db_overhaul=False):
        self.task_manager_obj = TaskManager(complete_db_overhaul)
        print("Dialog Manager setup complete..")

    def get_all_usda_food_items_from_user(self, food_items_tokens):
        self.task_manager_obj.text_to_audio('Let me get more information from you about these items to figure out '
                                            'your exact intake')
        result_list = []
        counter = 1
        while len(food_items_tokens) != 0:
            count = self._get_current_food_item_from_user(food_items_tokens, counter)
            counter += 1
            result = self.get_standard_item(food_items_tokens[:count])
            del food_items_tokens[:count]
            if result != "null":
                result_list.append(result)
        return result_list

    def _get_current_food_item_from_user(self, food_items_tokens, counter):
        counter_dict = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth'}
        if len(food_items_tokens) == 1:
            return 1
        if len(food_items_tokens) == 2:
            self.task_manager_obj.text_to_audio(
                'Please help me finalize your {0} food item. Say, \"I had the first item\" for {1}, or, '
                '\"I had the second item\" for {1} {2}'.format(counter_dict[counter], food_items_tokens[0],
                                                               food_items_tokens[1]))
        else:
            self.task_manager_obj.text_to_audio(
                'Please help me finalize your {0} food item. Say, \"I had the first item\" for {1}, or, '
                '\"I had the second item\" for {1} {2}, or, \"I had the third item\" '
                'for {1} {2}  {3}'.format(counter_dict[counter], food_items_tokens[0], food_items_tokens[1],
                                          food_items_tokens[2]))
        result = self._get_current_food_combination_from_user()
        return result

    def _get_current_food_combination_from_user(self):
        user_input = self.task_manager_obj.audio_to_text()
        user_input = user_input.lower().strip()
        if any(word in user_input for word in ['first', 'second', 'third', 'one', 'two', 'three']):
            self.task_manager_obj.text_to_audio('Thanks for your response')
        else:
            self.task_manager_obj.text_to_audio('I could not understand, please provide your choice again.')
            user_input = self.task_manager_obj.audio_to_text()
            user_input = user_input.lower().strip()
            if any(word in user_input for word in ['first', 'second', 'third' 'one', 'two', 'three']):
                self.task_manager_obj.text_to_audio('Thanks for your response')
        return 3 if 'third' in user_input else 2 if 'second' in user_input else 1

    def get_user_name_from_user(self):
        self.task_manager_obj.text_to_audio('Hello! Who am I speaking to?')
        user_input = self.task_manager_obj.audio_to_text()
        google_cloud_result = self.task_manager_obj.extract_user_name_from_text(user_input)
        if len(google_cloud_result) > 0:
            name = google_cloud_result[0].split()[0]
            self.task_manager_obj.text_to_audio('{0}, Did I get your name right? '
                                                'Say yes to confirm, No to try again'.format(name))
            result = self.task_manager_obj.audio_to_text()
            result = result.lower().strip()
            if len(result) == 0:
                self.task_manager_obj.text_to_audio('I could not understand your response. '
                                                    'Say yes if you think I correctly identified your name. '
                                                    'Say No otherwise')
                result = self.task_manager_obj.audio_to_text()
                result = result.lower().strip()
            if any(word in result for word in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct',
                                               'sure']):
                self.task_manager_obj.text_to_audio('Great! Nice to meet you, {0}'.format(name))
                return name
        self.task_manager_obj.text_to_audio('Sorry! I did not understand your name. Let us try one more time. '
                                            'May be use your full name in a sentence')
        user_input = self.task_manager_obj.audio_to_text()
        google_cloud_result = self.task_manager_obj.extract_user_name_from_text(user_input)
        if len(google_cloud_result) > 0:
            name = google_cloud_result[0].split()[0]
            self.task_manager_obj.text_to_audio('{0}, Did I get it right this time? Say yes to confirm.'.format(name))
            result = self.task_manager_obj.audio_to_text()
            result = result.lower().strip()
            if len(result) == 0:
                self.task_manager_obj.text_to_audio('I could not understand your response. '
                                                    'Say yes if you think I correctly identified your name.'
                                                    'Say No otherwise')
                result = self.task_manager_obj.audio_to_text()
                result = result.lower().strip()
            if any(word in result for word in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct',
                                               'sure']):
                self.task_manager_obj.text_to_audio('Great! Nice to meet you, {0}'.format(name))
                return name
        self.task_manager_obj.text_to_audio('Sorry! I could not understand your name.'
                                            'For now, let me address you as, User')
        return 'user'

    def get_food_items_tokens_from_user(self, user_name):
        food_tokens = self._get_food_consumption_from_user(user_name, False)
        satisfied = self._confirm_food_items_from_user(user_name, food_tokens)

        if not satisfied:
            food_tokens, food_token_text = self._get_food_consumption_from_user(user_name, True)
            satisfied = self._confirm_food_items_from_user(user_name, food_tokens)

        if not satisfied:
            self.task_manager_obj.text_to_audio('I am sorry {0}, But the food items mentioned by you did not match '
                                                'my knowledge'.format(user_name))
            sys.exit()
        return food_tokens

    def _get_food_consumption_from_user(self, user_name, second):
        if second:
            self.task_manager_obj.text_to_audio(' {0}, Mention the food items you had today with more detail'
                                                .format(user_name))
        else:
            self.task_manager_obj.text_to_audio('Let us work on your caloric intake. What did you eat today, {0}? '
                                                'Mention only the food item names.'.format(user_name))
        google_cloud_result = self.task_manager_obj.audio_to_text().lower()
        food_tokens = self.task_manager_obj.get_tokens_from_audio(google_cloud_result)

        if len(food_tokens) == 0:
            self.task_manager_obj.text_to_audio('Sorry {0}, can you repeat the food items names again.'
                                                .format(user_name))
            google_cloud_result = self.task_manager_obj.audio_to_text().lower()
            food_tokens = self.task_manager_obj.get_tokens_from_audio(google_cloud_result)

        if len(food_tokens) == 0:
            self.task_manager_obj.text_to_audio('I am sorry {0}, But the food items mentioned by you did not match '
                                                'my knowledge'.format(user_name))
            sys.exit()
        return food_tokens

    def _confirm_food_items_from_user(self, user, food_tokens):
        output = self.task_manager_obj.refractor_tokens_to_spoken_string(food_tokens)
        self.task_manager_obj.text_to_audio('Based on My Knowledge, these are the food items consumed '
                                            'by you! {0}'.format(output))
        self.task_manager_obj.text_to_audio('{0},Please acknowledge by saying yes, if all the food items are covered.'
                                            .format(user))
        result = self.task_manager_obj.audio_to_text()
        result = result.lower().strip()
        if any(word in result for word in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct',
                                           'sure']):
            return True
        return False

    def get_usda_obj(self, food_item_token):
        token_set = set()
        for i in range(0, len(food_item_token)):
            token_set.add(food_item_token[i])
        S = ""
        for item in food_item_token:
            S = S + item
            S += " "
        result = self.task_manager_obj.get_fully_matched_food_results(token_set)
        if len(result) == 0:
            self.task_manager_obj.text_to_audio("Sorry, I could not find any information for your selection, {0}. "
                                                "Let us move to the next item".format(S))
            return token_set, {}, result
        print(result)
        dict_freq = self.task_manager_obj.freq_generator(result, token_set)
        sorted_x = sorted(dict_freq.items(), key=operator.itemgetter(1))
        high_freq_item = []
        for item in sorted_x:
            high_freq_item.append(item[0])
        # print (sorted_x)
        # print (high_freq_item)
        if len(high_freq_item) > 3:
            high_freq_item = high_freq_item[-3:]
        # print (high_freq_item)

        descriptors = ""
        for word in high_freq_item:
            descriptors = descriptors + word
            descriptors += "  ,  "
        print(descriptors)
        if len(descriptors) == 0:
            return token_set
        self.task_manager_obj.text_to_audio('For your selection {0}, would you like to provide some description? '
                                            'For instance, you could tell me which restaurant you ate it from, or '
                                            'provide preparation information like raw, or cooked, boiled, or fried,'
                                            'roasted or grilled etcetra. Few suggestions for your current '
                                            'selection are: '
                                            '{1}.. Say, \'No description\' if you want to skip'.format(S, descriptors))
        google_cloud_result = self.task_manager_obj.audio_to_text().lower()
        if any(word in google_cloud_result for word in ['no description', 'nope', 'no' 'no, thanks', 'no, thank you']):
            self.task_manager_obj.text_to_audio('Thanks. Let\'s proceed further.')
            return token_set, dict_freq, result
        token = self.task_manager_obj.get_tokens_from_audio(google_cloud_result)
        if len(google_cloud_result) == 0 or len(token) == 0:
            self.task_manager_obj.text_to_audio('Sorry, I could not find matches for your description. '
                                                'Please try explaining in a sentence. For example, \'I '
                                                'ate my dish at Burger King\', or, \' My chicken was fried.\'.. Say, \''
                                                'No description\' if you want to skip')
            google_cloud_result = self.task_manager_obj.audio_to_text().lower()
        if any(word in google_cloud_result for word in ['no description', 'nope', 'no' 'no, thanks', 'no, thank you']):
            self.task_manager_obj.text_to_audio('Thanks. Let\'s proceed further.')
            return token_set, dict_freq, result
        self.task_manager_obj.text_to_audio('Thanks. Let\'s proceed further.')
        token_set = token_set.union(set(token))
        temp_result = self.task_manager_obj.get_fully_matched_food_results(token_set)
        if len(temp_result) == 0:
            token_set = token_set.difference(set(token))
            for i in range(0, len(token)):
                token_set.add(token[i])
                temp_result = self.task_manager_obj.get_fully_matched_food_results(token_set)
                if len(temp_result) == 0:
                    token_set.remove(token[i])
                else:
                    for element in temp_result:
                        result.append(element)
        else:
            result = temp_result
        dict_freq = self.task_manager_obj.freq_generator(result, token_set)
        print(token_set)
        return token_set, dict_freq, list(set(result))

    def ask_user_choice_from_items(self, item_list, contender_list, dict_freq):
        item_1 = item_list[0][0]
        item_2 = item_list[1][0]
        item_3 = item_list[2][0]
        print(item_list[0])
        print(item_list[1])
        print(item_list[2])
        contender_len = len(contender_list)
        print("Contender List Strength : ", contender_len)
        print("Size of Dictionary : ", len(dict_freq))
        self.task_manager_obj.text_to_audio('Currently we have {3} choices which match your food item description. '
                                            '. Say, \"My food item relates to first choice.\" for {0}.  Or, \"My food '
                                            'item relates to second choice.\" for {1}.  Or,  \"My food item relates '
                                            'to third choice.\" for {2} .  If you have no descriptor matches please '
                                            'Say, \" None of the these matches\" . If Not sure please Say \" I am not '
                                            'sure \"'.format(item_1, item_2, item_3, contender_len))

        audio_response = self.task_manager_obj.audio_to_text()
        audio_response = audio_response.lower().strip()
        self.task_manager_obj.text_to_audio('Thanks for your response')
        if not ('first' in audio_response or 'second' in audio_response or 'third' in audio_response or
                'none' in audio_response or ('sure' in audio_response and 'not' in audio_response)):
            self.task_manager_obj.text_to_audio(' I could not understand your response, kindly speak again')
            audio_response = self.task_manager_obj.audio_to_text()
            audio_response = audio_response.lower().strip()
            self.task_manager_obj.text_to_audio('Thanks for your response')
        if 'first' in audio_response:
            return item_1
        if 'second' in audio_response:
            return item_2
        if 'third' in audio_response:
            return item_3
        if 'none' in audio_response:
            return 'none'
        if 'sure' in audio_response and 'not' in audio_response:
            return 'not sure'
        return 'not sure'

    def get_final_item(self, contender_list):
        if len(contender_list) == 2:
            self.task_manager_obj.text_to_audio(
                'Based on your input, two items best match your food item Say, \"My food item relates to '
                'first item.\" for {0}. Or Say, \"My food item relates to second item.\" for '
                '{1}'.format(contender_list[0], contender_list[1]))
            audio_response = self.task_manager_obj.audio_to_text()
            audio_response = audio_response.lower().strip()
            self.task_manager_obj.text_to_audio('Thanks for your response')
            if 'first' in audio_response:
                return contender_list[0]
            if 'second' in audio_response:
                return contender_list[1]
            return contender_list[0]
        else:
            self.task_manager_obj.text_to_audio(
                'Based on your input, three items best match your food item Say, \"My food item relates to '
                'first item.\" for {0}. Or Say, \"My food item relates to second item.\" for {1}.Or Say, '
                '\"My food item relates to third item.\" for '
                '{2}'.format(contender_list[0], contender_list[1], contender_list[2]))
            audio_response = self.task_manager_obj.audio_to_text()
            audio_response = audio_response.lower().strip()
            self.task_manager_obj.text_to_audio('Thanks for your response')
            if 'first' in audio_response:
                return contender_list[0]
            if 'second' in audio_response:
                return contender_list[1]
            if 'third' in audio_response:
                return contender_list[2]
            return contender_list[0]

    def get_response(self, sorted_list_freq, contender_list, dict_freq):
        if len(sorted_list_freq) < 3 or len(dict_freq) < 3:
            return "-----", contender_list, dict_freq
        response = self.ask_user_choice_from_items(sorted_list_freq[-3:], contender_list, dict_freq)
        while response == 'none' or response == 'not sure':
            if response == 'none':
                contender_list, dict_freq = self.task_manager_obj.dict_contender_updator_for_none(
                    dict_freq, sorted_list_freq[-3:], contender_list)
                sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
            else:
                if len(sorted_list_freq) >= 3:
                    for i in range(-3, 0):
                        del dict_freq[sorted_list_freq[i][0]]
                    sorted_list_freq = sorted_list_freq[:-3]
            if len(sorted_list_freq) < 3 or len(dict_freq) < 3:
                return "-----", contender_list, dict_freq
            response = self.ask_user_choice_from_items(sorted_list_freq[-3:], contender_list, dict_freq)
        return response, contender_list, dict_freq

    def narrow_list(self, contender_list, dict_freq):
        while len(contender_list) > 3:
            # print("Contender List Length : ",len(contender_list))
            # print(contender_list)
            sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
            response, contender_list, dict_freq = self.get_response(sorted_list_freq, contender_list, dict_freq)
            if response == "-----":
                break
            contender_list, dict_freq = self.task_manager_obj.reduce_list(contender_list, response, dict_freq)
        if len(contender_list) == 1:
            return contender_list[0]
        result = self.get_final_item(contender_list)
        return result

    # We are doing it collectively will do one by one in future
    def get_standard_item(self, food_items):
        token_set, dict_freq, contender_list = self.get_usda_obj(food_items)
        if len(contender_list) == 0:
            return "null"
        result = self.narrow_list(contender_list, dict_freq)
        print(result)
        return result