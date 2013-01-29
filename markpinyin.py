#!/usr/bin/python3
import os
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig
from dirwalk import walkIndex


config = MyConfig()

#default pinyin total frequency
default = config.getDefaultPinyinTotalFrequency()

#minimum pinyin frequency
minimum = config.getMinimumPinyinFrequency()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done


atomic_words_dict = {}
merged_words_dict = {}


def load_atomic_words(filename):
    wordsfile = open(filename)
    for oneline in wordsfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)

        if word in atomic_words_dict:
            atomic_words_dict[word].append((pinyin, freq))
        else:
            atomic_words_dict[word] = [(pinyin, freq)]

    wordsfile.close()


def load_merged_words(filename):
    wordsfile = open(filename)
    for oneline in wordsfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, prefix, postfix, freq) = oneline.split(None, 3)
        freq = int(freq)

        if word in merged_words_dict:
            merged_words_dict[word].append((prefix, postfix, freq))
        else:
            merged_words_dict[word] = [(prefix, postfix, freq)]

    wordsfile.close()


def mergePinyin(pinyin_list):
    print(pinyin_list)
    pinyins = {}

    for (pinyin, freq) in pinyin_list:
        if pinyin in pinyins:
            pinyins[pinyin] += freq
        else:
            pinyins[pinyin] = freq

    pinyins = list(pinyins.items())
    total_freq = sum([ freq for pinyin, freq in pinyins ])

    results = []
    for (pinyin, freq) in pinyins:
        freq = default * freq / total_freq
        freq = int(freq)
        if freq < minimum:
            freq = minimum
        results.append((pinyin, freq))
    print(results)
    return results


def markAtomicWord(word):
    assert word in atomic_words_dict
    results = atomic_words_dict[word]
    return mergePinyin(results)


def markMergedWord(word):
    assert word in merged_words_dict

    merged_list = merged_words_dict[word]
    print(merged_list)
    merged_sum = sum([ freq for prefix, postfix, freq in merged_list ])

    results = []
    for (prefix, postfix, freq) in merged_list:
        prefix_list = markPinyin(prefix)
        prefix_sum = sum([ freq for pinyin, freq in prefix_list ])

        postfix_list = markPinyin(postfix)
        postfix_sum = sum([ freq for pinyin, freq in postfix_list ])

        for prefix_pinyin, prefix_freq in prefix_list:
            for postfix_pinyin, postfix_freq in postfix_list:
                merged_pinyin = prefix_pinyin + "'" + postfix_pinyin
                merged_freq = default * freq * prefix_freq * postfix_freq / \
                    merged_sum / prefix_sum / postfix_sum
                results.append((merged_pinyin, merged_freq))

    return mergePinyin(results)


def markPinyin(word):
    print(word)

    if word in atomic_words_dict:
        return markAtomicWord(word)
    elif word in merged_words_dict:
        return markMergedWord(word)
    else:
        assert False, "missed word.\n"


def markPinyins(workdir):
    print(workdir)

    merged_words_dict = {}

    filename = config.getPartialWordFileName()
    filepath = workdir + os.sep + filename
    load_merged_words(filepath)

    filename = config.getNewWordFileName()
    filepath = workdir + os.sep + filename
    newwordfile = open(filepath, "r")

    filename = config.getRecognizedWordFileName()
    filepath = workdir + os.sep + filename
    recordfile = open(filepath, "w")

    for oneline in newwordfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        word = oneline

        pinyin_list = markPinyin(word)

        for pinyin, freq in pinyin_list:
            freq = str(freq)
            oneline = '\t'.join((word, pinyin, freq))
            recordfile.writelines([oneline, os.linesep])

    recordfile.close()
    newwordfile.close()


#loading old words
load_atomic_words(config.getWordsWithPinyinFileName())
#print(atomic_words_dict)
