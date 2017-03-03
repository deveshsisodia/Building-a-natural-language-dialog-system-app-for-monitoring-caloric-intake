from db import DB
import nltk
import re
from speechProcessor import SpeechProcessor
from gtts import gTTS
import os
import sys
from introduction import Introduction



class Dialogue_Manager:
    def __init__(self):
        print("Dialogue_Manager  started")

    def narrow_choice(self,food_token,food_token_result,user_name):
        print("Narrowing Choices")
        return "pizza"
        


