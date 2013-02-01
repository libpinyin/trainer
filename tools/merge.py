#!/usr/bin/python3
import os

#minimum duplicates in recognized dictionaries to be merged
threshold = 3

#minimum pinyin frequency
minimum = 3

#default pinyin total frequency
default = 100

words_dict = {}

def load_recognized_words(filename):
    print(filename)

    words = set([])
    wordfile = open(filename, "r")
    for oneline in wordfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, pinyin, freq) = oneline.split(None, 2)

        if not word in words:
            words.add(word)

    wordfile.close()

    for word in words:
        if word in words_dict:
            words_dict[word] += 1
        else:
            words_dict[word] = 1


merged_words_dict = {}

def filter_recognized_words(filename):
    print(filename)
    lines = []

    #loading
    wordfile = open(filename, "r")
    for oneline in wordfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)

        if not word in words_dict:
            lines.append(oneline)
            continue

        occurs = words_dict[word]
        if occurs < threshold:
            lines.append(oneline)
            continue

        if word in merged_words_dict:
            merged_words_dict[word].append((pinyin, freq))
        else:
            merged_words_dict[word] = [(pinyin, freq)]

    wordfile.close()

    #saving
    wordfile = open(filename, "w")
    for oneline in lines:
        wordfile.writelines([oneline, os.linesep])
    wordfile.close()


def save_merged_words(filename):
    print(filename)

    wordfile = open(filename, "w")
    for word, pairs in merged_words_dict.items():
        pinyins = {}
        for pinyin, freq in pairs:
            if pinyin in pinyins:
                pinyins[pinyin] += freq
            else:
                pinyins[pinyin] = freq

        freqsum = sum([ freq for pinyin, freq in pinyins.items() ])

        for pinyin, freq in pinyins.items():
            freq = int(default * freq / freqsum)

            if freq < minimum:
                continue

            freq = str(freq)

            oneline = '\t'.join((word, pinyin, freq))
            wordfile.writelines([oneline, os.linesep])

    wordfile.close()
