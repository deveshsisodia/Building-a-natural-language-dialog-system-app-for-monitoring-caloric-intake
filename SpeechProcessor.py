import speech_recognition as sr
import contextlib
import os
import sys
from DialogTracer import DialogTracer


@contextlib.contextmanager
def ignore_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
  "type": "service_account",
  "project_id": "sound-utility-159401",
  "private_key_id": "19b0db5d6246fd063bcfa4f7aeb04d36f33deb7b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxwA3wngubP2KU\njpm+iZ9k6IQwRBXeBTTptfZm+hj8EzrulrE1H1DTkXCIJ6Q4UpuHUqWlss6jh6+d\n5xb09kbARopbvsFV2HST/7L+akowjZGxWZhfPgQIku9K/lhP6K/gSVVwp/TDlaQ9\nQnH+TSfYyS+gXe8V5agYAwfDChbGuYsWhL+bp9FYvh2t59BkwC+KhkK4ro9ga6tC\nA0TmzPyARKSx/bDxQ64iDR6EGYe7LKN42ziffBLBTgL9H5FkdTnE014SjSXPm7jM\nyEutf2JzEzwTeJPGzmGt1hOz2WpPG2upGgt+VnDxBz2+8o/yi2KileAbVRU5YuWH\nxztPeVERAgMBAAECggEBAKmGKcVadmdSRIq6lhcK2mI7ABeoV9Kv1I8xZBdCX6HK\nFWKHherMOyIMi+7PH+g3oO2m/STTLBD6z5shUtu+JiwrGrn1bB6bmlOsguHyLV+x\nJUqn0JLFasNin6Y+fat4mISobDxNczs19LYYMPAAVgiDmFCyRdv0dCSyfyyc6qwL\noh6mTBlXvB7FZjNpodF5iBHiuG0pbB6lBoP9F1WlfBvgepqs7KLRk3WXDgsUyc0O\ncGQgLKaAqye08EhP5yU/GngBZ8bX3KFO79mNdN4fPJgGhyq1VTOphOFaW3yTk659\n8u4x+/j1u4WSjpB3QfL2KrXYY9cyYy8fl/jjQFEvtaECgYEA4CRt33cdbDi+m0N0\n2jOtLR8S6gxKzv47FUj1WK3ndDSJeoTNgp0RfANo8ywaZXEfBU0iwhYRryheFk4H\nN3Z9xPFsH31nG8E5Z9PMC0rpHtC+eBE6j5VpTme0nuccjszUgfq3mSxGcQsQ6sAW\nCWc4UTScyJzbCd4RIEDkqAyl818CgYEAywOeDnFDPOUDY2IYLb/8Q3qTtanb7nwi\nvMva/azeQE22BteKQdvBhVk3Z4akx0IOrUPup5e+yYfVQM4oDGJkG/fjfmB2Zlpa\ng2W2siqbIpvt0Yk4JtKK81C//ZoNfkgLmcfr/SufASE+XAbMuPY9OQbxvsxmvElR\nzpz7C+MNAY8CgYBqOJlhN3/YE6QwzG0KI0dEhN9fz2d8ZPr3AVZUKkXvyh4E0/7Y\nkTsB/FO2OgZgYJWE26NHO1IyIf1EsMG2xQ6hUJAe9Dzy6EUeMT8Xcu67Tc2V9QQ9\nm18Gaxsr2varreJfnsN3cYYIeGgR9+n5ltMXmMlcQQmEyZpwIJC8GxJiHQKBgEbZ\nxFeV/7lI053jpjyRPCDwrow/85mPiTAKlSrjIc2fUV+h6YaCg09ei4991hQUYbrm\ncmva8aKz3SD40dFApV99a8+3Kpsd/WjOHqyfYfT6Jk1ybj5eTFAOZnLDSOJBkorg\n0uNQTfW+/FxxoxEKHuPAIK5N96zOidZpwtOrMebRAoGAB+gcr2hjwlhfAO2A6VIU\nFdBYBTAjzZt928PVknvy+XGYuH2fNAauRIFe1+7fsT6ALtqRaQOvidQhXzSpnH0N\nV3t5Yn5gzI0CtYQSQ4g+vyCPjPLOcTYvqaHxag/2DGu3AOYf+XL/FSFG8FcK8UYl\no0mdLYDjqqBfhXIP+FLiW9Y=\n-----END PRIVATE KEY-----\n",
  "client_email": "prasoon@sound-utility-159401.iam.gserviceaccount.com",
  "client_id": "105524698821060613808",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/prasoon%40sound-utility-159401.iam.gserviceaccount.com"
}"""


class SpeechProcessor:
    def __init__(self):
        self.rec_obj = sr.Recognizer()
        self.tracer_obj = DialogTracer(True)

    def _get_audio_from_mic(self, timeout = 10):
        with ignore_stderr():
            with sr.Microphone() as source:
                audio = self.rec_obj.listen(source, timeout=timeout)
            return audio

    def _google_speech_recognizer(self, audio):
        result = ''
        try:
            result = self.rec_obj.recognize_google(audio)
        except sr.UnknownValueError:
            self.tracer_obj.sys_msg("Speech Recognition module could not understand audio")
        except sr.RequestError as e:
            self.tracer_obj.sys_msg("Could not request results from Speech Recognition service; {0}".format(e))
        return result

    def _google_cloud_speech_recognizer(self, audio):
        result = ''
        try:
            result = self.rec_obj.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        except sr.UnknownValueError:
            self.tracer_obj.sys_msg("Speech Recognition module could not understand audio")
        except sr.RequestError as e:
            self.tracer_obj.sys_msg("Could not request results from Speech Recognition service; {0}".format(e))
        return result

    def audio_to_text(self):
        speech_audio = self._get_audio_from_mic()
        google_cloud_result = self._google_cloud_speech_recognizer(speech_audio)
        return google_cloud_result

