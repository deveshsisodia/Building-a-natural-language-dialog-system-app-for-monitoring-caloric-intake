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
    #food_token,food_token_result,user_name = introduce_obj.start_introduction()

    result_list = []
    #Getting Food Item
    food_token = ['chicken','burger']
    counter = 1;
    while(len(food_token) !=  0):
        if(len(food_token) > 1):
            count = response_obj.get_food_item(food_token,counter)
            counter = counter+1
        else:
            count = 1
        #result = dialogue_mnj_obj.get_standard_item(food_token[:count]) Will work once narrowing is Done
        result = dialogue_mnj_obj.get_standard_item(food_token[:count])
        del food_token[:count]
        if(result!="null"):
            result_list.append(result)
    print(result_list)
    print("Introduction Finished")
