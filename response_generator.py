from db import DB
import nltk
import re
from speechProcessor import SpeechProcessor
from gtts import gTTS
import os
import sys
from introduction import Introduction



class Response_Generator:
    def __init__(self):
        print("Response_Generator  started")
        self.speech_obj = SpeechProcessor()

    def get_audio_responses(self):
        speech_audio = self.speech_obj.get_audio_from_mic()
        google_cloud_result = self.speech_obj.google_cloud_speech_recognizer(speech_audio)
        return google_cloud_result

    def text_to_audio(self, tts, file_name='dummy', delete_after_use='true'):
        tts.save(file_name + '.mp3')
        os.system("afplay {0}.mp3".format(file_name))
        if delete_after_use:
            os.remove(file_name + '.mp3')

    def get_tts(self,input):
    	tts = gTTS(input, lang='en')
    	return tts

    def client_satisfaction(self,user):
        spee
        tts = gTTS(text='{0},Please acknowledge by saying yes'.format(user), lang='en')
        self.text_to_audio(tts, file_name="items")
        result = self.get_audio_responses()
        result = result.lower().strip()
        if result in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct', 'sure']:
            return True
        return False

    def get_response_one_two_three(self):
        #return 3 # To be Commented out , just for fast testing
        result = self.get_audio_responses()
        result = result.lower().strip()
        default = 1
        if result in ['first', 'second', 'third']:
            tts = gTTS(text='Thanks for your response',
                           lang='en')
            self.text_to_audio(tts, "intro")
            print('Sucess one')
        else:
            tts = gTTS(text='Please try to provide the choice again!',
                           lang='en')
            self.text_to_audio(tts, "intro")
            result = self.get_audio_responses()
            result = result.lower().strip()
            if result in ['one', 'two', 'three']:
                tts = gTTS(text='Thanks for your response',
                           lang='en')
                self.text_to_audio(tts, "intro")
                print('sucess two')

        if(result is 'three'):
            return 3
        elif(result is 'two'):
            return 2
        else:
            return default

    def get_food_item(self,food_token):
        len_food_token = len(food_token)
        uni = food_token[0]
        bi = food_token[1]
        tri = " "
        count = 2;
        if( len_food_token > 2):
            tri = food_token[2]
            count = 3
        tts = gTTS(text='Please help me to select the tokens for this new food item , Speak first for {0}. Speak second for {0} and {1}'.format(uni,bi), lang='en')
        self.text_to_audio(tts, file_name="items")
        if(count == 3):
            tts = gTTS(text='Speak third for {0},{1} and {2}'.format(uni,bi,tri), lang='en')
            self.text_to_audio(tts, file_name="items")
        result = self.get_response_one_two_three()
        print(result)
        return result



