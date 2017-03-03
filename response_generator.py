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
        tts = gTTS(text='{0},Please acknowledge by saying yes'.format(user), lang='en')
        self.text_to_audio(tts, file_name="items")
        result = self.get_audio_responses()
        result = result.lower().strip()
        if result in ['yes', 'yeah', 'yup', 'yep', 'yo', 'ok', 'okay', 'right', 'correct', 'sure']:
            return True
        return False


