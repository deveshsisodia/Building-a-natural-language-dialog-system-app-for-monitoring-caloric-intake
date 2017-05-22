											CSE 523 Project
			Building a natural language dialog system app for monitoring caloric intake 


	Contributors:
	Prasoon Rai (prrai@cs.stonybrook.edu)
	Devesh Sisodia (dsisodia@cs.stonybrook.edu)

	For detailed explaination and logical flow, we recommend to go through our report in the repository.

	1 Introduction
	"A Natural Dialogue System is a form of dialogue system that tries to improve usability and user satisfaction
	by imitating human behaviour" [1] (Berg, 2014). It addresses the features of a human-to-human
	dialog (e.g. sub dialogues and topic changes) and aims to integrate them into dialog systems for humanmachine
	interaction.
	In this project, we aim to build command line interface (CLI) that implements a natural language dialog
	system, which, given a description of food intake instance from an end user, reports the total caloric and
	related dietary information about the consumption. The system exercises a series of dialogues with the
	user in order to extract precise information about the food items consumed, before finalizing the best
	match with the database and reporting calorie values.

	2 Spoken Dialog Systems
	Before discussing our design, we briefly list the components involved typically in a speech based dialog
	system[2]:
	 Automatic Speech Recognizer (ASR): The ASR decodes speech input from the user into text
	that acts as an input to the natural language understanding module in the system.
	 Natural language understanding: It transforms a recognition into a concept structure that can
	drive system behavior. Thus, the translated input text from ASR is interpreted in context of the
	current application to extract requisite information.
	 Dialog manager: The dialog manager controls turn-by-turn behavior. A simple dialog system
	may ask the user questions then act on the response. Such directed dialog systems use a tree-like
	structure for control.
	 Text-to-speech Generator (TTS): It realizes an intended utterance as speech. Depending on
	the application, TTS may be based on concatenation of pre-recorded material produced by voice
	professionals, or a voice assistant like Google assistant, Apple Siri etc.
	 Response Generator: It is similar to text-based natural language generation, but takes into
	account the needs of spoken communication. This might include the use of simpler grammatical
	constructions, managing the amount of information in any one output utterance and introducing
	prosodic markers to help the human participant absorb information more easily.
	 Domain Reasoner/Task Manager: The domain reasoner, or more simply the back-end, makes
	use of a knowledge base to retrieve information and helps formulate system responses. In simple
	systems, this may be a database which is queried using information collected through the dialog.

	3.) Installation Procedure :
	Make sure to install below python modules before running the script:
	import re
	import os
	import sys
	import slugify 
	import urllib.request 
	import urllib.request 
	import bs4 
	import pathlib 
	import glob 
	import pickle
	import operator
	import nltk
	import contextlib
	import speech_recognition

	In case your system needs additional package import, proceed as suggested.
