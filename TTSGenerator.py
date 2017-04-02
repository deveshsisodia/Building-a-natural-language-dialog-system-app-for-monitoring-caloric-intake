import os
from gtts import gTTS


class TTSGenerator:
    def __init__(self):
        pass

    def text_to_audio(self, inp, file_name='dummy', delete_after_use='true', lang='en'):
        tts_obj = self._get_tts_obj(inp, lang)
        tts_obj.save(file_name + '.mp3')
        os.system("afplay {0}.mp3".format(file_name))
        if delete_after_use:
            os.remove(file_name + '.mp3')

    def _get_tts_obj(self, inp, lang):
        tts_obj = gTTS(inp, lang=lang)
        return tts_obj