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

    def narrow_result(self,contender_list,token_set):

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

    	self.introduction_obj.remove_stop_words_dict(dict_freq)


    	for keys,values in dict_freq.items():
    		print(keys,"====",values)
    	print('dict_size  :',len(dict_freq))
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
    	dict_freq = self.narrow_result(result,token_set)
    	sorted_x = sorted(dict_freq.items(), key=operator.itemgetter(1))
    	high_freq_item = []
    	for item in sorted_x:
    	    high_freq_item.append(item[0])
    	print (sorted_x)
    	print (high_freq_item)
    	if(len(high_freq_item) > 3):
    		high_freq_item = high_freq_item[-3:]
    	print (high_freq_item)
        
    	descriptors = ""
    	for word in high_freq_item:
    		descriptors = descriptors + word
    		descriptors = descriptors  + ", "
    	print (descriptors)
    	if(len(descriptors)==0):
    		return(token_set)
    	tts = gTTS(text='For your selection {0}, would you like to add some descriptorsl like {1}'.format(S,descriptors),lang='en')
    	self.response_obj.text_to_audio(tts, "intro")
    	token ,token_result = self.introduction_obj.get_tokens_from_audio()
    	for i in range(0,len(token)):
    		token_set.add(token[i])
    	print(token_set)
    	return(token_set)



    # We are doing it collectively will do one by one in future
    def get_standard_item(self,food_items):
    	token_set  = self.get_usda_obj(food_items)
    	result  = self.introduction_obj.get_fully_matched_food_results(token_set)
    	if(len(result) == 0):
    		return
    	dict_freq = self.narrow_result(result,token_set)
    	print('Printing Result')
    	print(result)



