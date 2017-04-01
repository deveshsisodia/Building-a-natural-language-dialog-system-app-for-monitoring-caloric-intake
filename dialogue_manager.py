from db import DB
import nltk
import re
from speechProcessor import SpeechProcessor
from response_generator import Response_Generator
from gtts import gTTS
import os
import sys
from introduction import Introduction
from gtts import gTTS
from introduction import Introduction
import operator



class Dialogue_Manager:
    def __init__(self):
    	self.speech_obj = SpeechProcessor()
    	self.response_obj = Response_Generator()
    	self.introduction_obj = Introduction()
    	print(" Dialogue  Manager  started")

    def freq_generator(self,contender_list,token_set):

    	dict_freq = {}
    	if(len(contender_list) == 0):
    		return dict_freq
    	for contender in contender_list:
        	tokens = contender.split('-')
        	for item in tokens:
        		if item in dict_freq:
        			dict_freq.update({item : dict_freq[item] +1 })
        		else:
        			dict_freq.update({item : 1 })
    	print("Printing Frequencies")
    	
    	# Removing token from dict
    	for token in token_set:
    		del dict_freq[token]
    	len_list = len(contender_list)
    	del_list = []
    	for key,value in dict_freq.items():
    		if(value>=len_list):
    			del_list.append(key)

    	for item in del_list:
    		del dict_freq[item]

    	self.introduction_obj.remove_stop_words_dict(dict_freq)
    	dict_freq = self.remove_small_words(dict_freq)

    	#for keys,values in dict_freq.items():
    	#	print(keys,"====",values)
    	print('dict_size  :',len(dict_freq))
        #sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
    	return dict_freq
        
    def get_usda_obj(self,food_item_token):
    	token_set = set()
    	for i in range(0,len(food_item_token)):
    		token_set.add(food_item_token[i])

    	print("token before " ,token_set)
    	S = ""
    	for item in food_item_token:
    		S = S + item
    		S = S + " "

    	result  = self.introduction_obj.get_fully_matched_food_results(token_set)
    	dict_freq = self.freq_generator(result,token_set)
    	sorted_x = sorted(dict_freq.items(), key=operator.itemgetter(1))
    	high_freq_item = []
    	for item in sorted_x:
    	    high_freq_item.append(item[0])
    	#print (sorted_x)
    	#print (high_freq_item)
    	if(len(high_freq_item) > 3):
    		high_freq_item = high_freq_item[-3:]
    	#print (high_freq_item)
        
    	descriptors = ""
    	for word in high_freq_item:
    		descriptors = descriptors + word
    		descriptors = descriptors  + "  ,  "
    	print (descriptors)
    	if(len(descriptors)==0):
    		return(token_set)
    	tts = gTTS(text='For your selection {0}, would you like to add some descriptors like, {1}'.format(S,descriptors),lang='en')
    	self.response_obj.text_to_audio(tts, "intro")
    	token ,token_result = self.introduction_obj.get_tokens_from_audio()
    	for i in range(0,len(token)):
    		token_set.add(token[i])
    	print(token_set)
    	return(token_set,dict_freq,result)

    def remove_small_words(self,dict_freq):
    	del_list = []
    	for key,value in dict_freq.items():
            if( len(key) <= 2):
                del_list.append(key) 
    	for item in del_list:
    		del dict_freq[item]
    	return dict_freq


    def dict_contender_updator_for_none(self,dict_freq,token_set,contender_list):
    	removal_list = []
    	new_list = []
    	contender_removed = []
    	new_contender_list = []
    	for token in token_set:
    		removal_list.append(token[0])


    	for contender in contender_list:
    		tokens = contender.split('-')
    		for removed_token in removal_list:
    			if(removed_token in tokens):
    				contender_removed.append(contender)

        
    	for contender in contender_list:
    		if (contender not in contender_removed):
    			new_contender_list.append(contender)

    	for key,value in dict_freq.items():
    		dict_freq[key]=0

        

    	for contender in new_contender_list:
    		tokens = contender.split('-')
    		for item in tokens:
    			if item in dict_freq:
    				dict_freq.update({item : dict_freq[item] +1 })

    	for key,value in dict_freq.items():
    		if (dict_freq[key] == 0 or dict_freq[key]  >= len(new_contender_list)):
        		removal_list.append(key)

    	for token in removal_list:
    		if(token in dict_freq):
    			del dict_freq[token]

    	if(len(new_contender_list) == 0):
    		return (contender_list[:1],dict_freq)

    	contender_list = new_contender_list

    	#for keys,values in dict_freq.items():
    	#	print(keys,"====",values)
    	print('dict_size  :',len(dict_freq))
    	#sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
    	return contender_list,dict_freq

    def get_scoring(self,contender_list,token_set,dict_freq):
    	dict_freq = self.freq_updator(contender_list,token_set,dict_freq)
    	sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
    	return sorted_list_freq

    def ask_user_choice_from_items(self,item_list,contender_list):
    	item_1 = item_list[0][0]
    	item_2 = item_list[1][0]
    	item_3 = item_list[2][0]
    	print(item_list[0])
    	print(item_list[1])
    	print(item_list[2])
    	contender_len = len(contender_list)
    	print("Contender List Strength : ",contender_len)
    	print("Size of Dictionary : " , len(dict_freq))
    	tts = gTTS(text='Still,we have {3} choices which match your input food item. Inorder to precisely figure out your calorie intake for this item.If any of the three descriptors corelate with the food item. Say, \"My food item relates to first choice.\" for {0}.  Or, \"My food item relates to second choice.\" for {1}.  Or,  \"My food item relates to third choice.\" for {2} .  If you have no descriptor matches please Say, \" None of the these matches\" . If Not sure please Say \" I am not sure \"'.format(item_1 ,item_2,item_3,contender_len), lang='en')
    	self.response_obj.text_to_audio(tts, file_name="items")
    	audio_respose = self.response_obj.get_audio_responses()
    	audio_respose = audio_respose.lower().strip()
    	tts = gTTS(text='Thanks for your response',lang='en')
    	self.response_obj.text_to_audio(tts, "intro")
    	if(not('first' in audio_respose or 'second' in audio_respose or 'third' in audio_respose or 'none' in audio_respose or ('sure' in audio_respose and 'not' in audio_respose))):
    		tts = gTTS(text=' I could not understand your response, please provide response again'.format(item_1 ,item_2,item_3), lang='en')
    		self.response_obj.text_to_audio(tts, file_name="items")
    		audio_respose = self.response_obj.get_audio_responses()
    		audio_respose = audio_respose.lower().strip()
    		tts = gTTS(text='Thanks for your response',lang='en')
    		self.response_obj.text_to_audio(tts, "intro")
    	if('first' in audio_respose):
    		return item_1
    	if('second' in audio_respose):
    		return item_2
    	if ('third' in audio_respose):
    		return item_3
    	if('none' in audio_respose):
    		return 'none'
    	if('sure' in audio_respose and 'not' in audio_respose):
    		return 'not sure'
    	return 'not sure'

    def get_choice(self,sorted_list_freq):
    	#response = self.ask_user_choice_from_items[-3:]
    	if(response != 'null'):
    		return response_obj
    		c = 1

    def reduce_list(self, contender_list,response,dict_freq):
    	new_list = []
    	for contender in contender_list:
    		tokens = contender.split('-')
    		if response in  tokens:
    			new_list.append(contender)
    	contender_list = new_list

    	for key,value in dict_freq.items():
    		dict_freq[key]=0

    	for contender in contender_list:
    		tokens = contender.split('-')
    		for item in tokens:
    			if item in dict_freq:
    				dict_freq.update({item : dict_freq[item] +1 })

    	removal_list = []

    	for key,value in dict_freq.items():
    		if (dict_freq[key] == 0 or dict_freq[key]  >= len(contender_list)):
    			removal_list.append(key)

    	for token in removal_list:
    		del dict_freq[token]

    	#for keys,values in dict_freq.items():
    	#	print(keys,"====",values)

    	return new_list,dict_freq

    def get_final_item(self,contender_list):
    	if len(contender_list) == 2 : 
    		tts = gTTS(text=' Based on your input these two items best match your food item Say, \"My food item relates to first item.\" for {0}. Or Say, \"My food item relates to second item.\" for {1}'.format(contender_list[0] ,contender_list[1]), lang='en')
    		self.response_obj.text_to_audio(tts, file_name="items")
    		audio_respose = self.response_obj.get_audio_responses()
    		audio_respose = audio_respose.lower().strip()
    		tts = gTTS(text='Thanks for your response',lang='en')
    		if('first' in audio_respose):
        		return contender_list[0]
    		if('second' in audio_respose):
    			return contender_list[1]
    		return contender_list[0]
    	else:
    		tts = gTTS(text=' Based on your input these two items best match your food item Say, \"My food item relates to first item.\" for {0}. Or Say, \"My food item relates to second item.\" for {1}.Or Say, \"My food item relates to third item.\" for {2}'.format(contender_list[0] ,contender_list[1],contender_list[2]), lang='en')
    		self.response_obj.text_to_audio(tts, file_name="items")
    		audio_respose = self.response_obj.get_audio_responses()
    		audio_respose = audio_respose.lower().strip()
    		tts = gTTS(text='Thanks for your response',lang='en')
    		if('first' in audio_respose):
        		return contender_list[0]
    		if('second' in audio_respose):
        		return contender_list[1]
    		if('third' in audio_respose):
    			return contender_list[2]
    		return contender_list[0]

    def reduce_list_for_no_match(self,sorted_list_freq,contender_list):
    	rejected_token_list = []
    	new_contender_list = []
    	for item in sorted_list_freq:
    		rejected_token_list.append(item[0])
    	for contender in contender_list:
        	c=0
        	for item in rejected_token_list:
        		if(item in contender):
        			c=1
        			break
        	if(c==0):
        		new_contender_list.append(contender)
    	return new_contender_list

    def get_response(self,sorted_list_freq,contender_list,dict_freq):
    	if(len(sorted_list_freq) < 3 or len(dict_freq)<3):
    		return "-----",contender_list,dict_freq
    	response = self.ask_user_choice_from_items(sorted_list_freq[-3:],contender_list,dict_freq)
    	while(response == 'none' or response == 'not sure'):
    		if(response == 'none'):
    			contender_list , dict_freq =self.dict_contender_updator_for_none(dict_freq,sorted_list_freq[-3:],contender_list,dict_freq)
    			sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
    		else:
    			if(len(sorted_list_freq)>=3):
    				for i in range(-3,0):
    					del dict_freq[sorted_list_freq[i][0]]
    				sorted_list_freq = sorted_list_freq[:-3]
    		if(len(sorted_list_freq) < 3 or len(dict_freq)<3):
    			return "-----",contender_list,dict_freq
    		response = self.ask_user_choice_from_items(sorted_list_freq[-3:],contender_list)
    	return response,contender_list,dict_freq

            

    def narrow_list(self,contender_list,token_set,dict_freq):
    	while (len(contender_list) > 3 ):
    		#print("Contender List Length : ",len(contender_list))
    		#print(contender_list)
    		sorted_list_freq = sorted(dict_freq.items(), key=operator.itemgetter(1))
    		response,contender_list,dict_freq = self.get_response(sorted_list_freq,contender_list,dict_freq)
    		if response == "-----" :
    			break
    		contender_list,dict_freq = self.reduce_list(contender_list,response,dict_freq)

    		
    	if len(contender_list) == 1 :
    		return contender_list[0]
    	result = self.get_final_item(contender_list)
    	return result

    # We are doing it collectively will do one by one in future
    def get_standard_item(self,food_items):
    	token_set,dict_freq,contender_list  = self.get_usda_obj(food_items)
    	#contender_list  = self.introduction_obj.get_fully_matched_food_results(token_set)
    	if(len(contender_list) == 0):
    		return "null"
    	result = self.narrow_list(contender_list,token_set,dict_freq)
    	print(result)
    	return result



