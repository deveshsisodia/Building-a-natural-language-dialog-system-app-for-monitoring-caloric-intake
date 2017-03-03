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



class Main_Interface:
    def __init__():
        print("Main Interface started")


if __name__ == '__main__':

    #OBJECTS
    introduce_obj = Introduction()
    response_obj =  Response_Generator()
    dialogue_mnj_obj = Dialogue_Manager()

    #STARTING INTRODUCTION
    food_token,food_token_result,user_name = introduce_obj.start_introduction()

    #NARROW CHOICES
    result = dialogue_mnj_obj.narrow_choice(food_token,food_token_result,user_name)

    #Result
    tts = response_obj.get_tts(result)
    response_obj.text_to_audio(tts,file_name="items")

    #TODO: Class for Displaying Calorific Value of Result


    print("Food Tokens")
    print(food_token)
    print("Introduction Finished")