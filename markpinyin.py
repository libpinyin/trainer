#!/usr/bin/python3
import os
import sqlite3
from argparse import ArgumentParser
from operator import itemgetter
import utils
from myconfig import MyConfig
from dirwalk import walkIndex


config = MyConfig()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done


atomic_words_list = []
merged_words_list = []


def load_atomic_words(filename):
    wordsfile = open(filename)
    for oneline in wordsfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)

        atomic_words_list.append((word, pinyin, freq))

    wordsfile.close()
    #ascending sort
    atomic_words_list.sort(key=itemgetter(0, 1))


def load_merged_words(filename):
    wordsfile = open(filename)
    for oneline in wordsfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, prefix, postfix, freq) = oneline.split(None, 3)
        freq = int(freq)

        merged_words_list.append((word, prefix, postfix, freq))

    wordsfile.close()

    #ascending sort
    merged_words_list.sort(key=itemgetter(0, 1, 2))


#loading old words
load_atomic_words(config.getWordsWithPinyinFileName())
#print(atomic_words_list)
