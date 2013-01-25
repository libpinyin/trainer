#!/usr/bin/python3
import os
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig
from dirwalk import walkIndex


config = MyConfig()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done

