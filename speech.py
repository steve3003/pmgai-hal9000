import time
import threading
import subprocess

import speech_recognition as speech
import win32com.client


class SpeechMixin(object):
    """Support for voice interactions as both input with speech-to-text and output with
    text-to-speech.  Derive your Bot from this mixin class to expose this functionality
    to all your AI functions.
    """

    def __init__(self, audio_threshold=1000):
        self.voice = win32com.client.Dispatch("SAPI.SpVoice")

        # The threshold of the recognizer is very important for the speech
        # library
        # to be able to segment audio into utterances.  If it's a loud room you
        # may
        # have to bump it up to 4000, otherwise 1000 seems reasonable if you
        # speak
        # clearly into the microphone.
        self.recognizer = speech.Recognizer()
        self.recognizer.energy_threshold = audio_threshold
        self._stop = False

        self.speak_message = None
        self.speak_thread = threading.Thread(target=self.speak)
        self.speak_thread.daemon = True
        self.speak_thread.start()

        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self._stop = True
        self.thread.join()
        self.speak_thread.join()

    def speak(self):
        while not self._stop:
            time.sleep(1.0)
            if self.speak_message:
                self.voice.Speak(self.speak_message)
                self.speak_message = None

    def listen(self):
        """Entry point for the speech-to-text thread."""

        # It's ideal to start listening before the game starts, but the
        # down-side
        # is that object construction may not be done yet.  Here we pause
        # shortly
        # to let initialization finish, so all functionality (e.g.  self.log)
        # is
        # available.
        time.sleep(0.1)

        for st in self.sentences():
            if st:
                self.onMessage(source=None, message=st)

    def sentences(self):
        while not self._stop:
            with speech.Microphone() as source:
                self.log("Listening to microphone...")
                audio = self.recognizer.listen(source)
                self.log("Analysing audio data.")

            try:
                sentence = self.recognizer.recognize_google(audio)
                yield sentence

            except speech.UnknownValueError:
                self.log("Could not understand.")
                yield ""
