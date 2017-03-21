from db import DB
import nltk
import re
from speechProcessor import SpeechProcessor
from gtts import gTTS
import os
import sys
from introduction import Introduction
from response_generator import Response_Generator
from dialogue_manager import Dialogue_Manager
from db import DB


class Main_Interface:
    def __init__():
        print("Main Interface started")


if __name__ == '__main__':

    #OBJECTS
    introduce_obj = Introduction()
    response_obj =  Response_Generator()
    dialogue_mnj_obj = Dialogue_Manager()
    db_obj = DB()

    #STARTING INTRODUCTION
    food_token,food_token_result,user_name = introduce_obj.start_introduction()

    result = []

    #Getting Food Item
    #food_token = ['chicken']
    while(len(food_token) !=  0):
        if(len(food_token) > 1):
            count = response_obj.get_food_item(food_token)
        else:
            count = 1
        #result = dialogue_mnj_obj.get_standard_item(food_token[:count]) Will work once narrowing is Done
        dialogue_mnj_obj.get_standard_item(food_token[:count])
        del food_token[:count]

    #dialogue_mnj_obj.get_standard_item_list(food_items)


    #NARROW CHOICES
    #result = dialogue_mnj_obj.narrow_choice(food_token,food_token_result,user_name)

    #Result
    #result = "chicken burger"
    #tts = response_obj.get_tts(result)
    #response_obj.text_to_audio(tts,file_name="items")

    #TODO: Class for Displaying Calorific Value of Result


    print("Food Tokens")
    print(food_token)
    print("Introduction Finished")