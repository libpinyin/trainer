#!/usr/bin/python3
import os
from operator import itemgetter

words_set = set([])
words_dict = {}


def add_words_set(word):
    if len(word) < 2:
        return
    if not word in words_set:
        words_set.add(word)

def strip_tone(old_pinyin_str):
    oldpinyins = old_pinyin_str.split("'")
    newpinyins = []
    for pinyin in oldpinyins:
        if pinyin[-1].isdigit():
            pinyin = pinyin[:-1]
        newpinyins.append(pinyin)
    new_pinyin_str = "'".join(newpinyins)
    return new_pinyin_str


def add_words_dict(word, pinyin, freq):
    pinyin = strip_tone(pinyin)
    if not (word, pinyin) in words_dict:
        words_dict[(word, pinyin)] = freq
    else:
        words_dict[(word, pinyin)] += freq


def load_phrase(filename):
    phrasefile = open(filename, "r")

    for line in phrasefile.readlines():
        line = line.rstrip(os.linesep)
        (pinyin, word, token, freq) = line.split(None, 3)
        freq = int(freq)
        add_words_set(word)
        add_words_dict(word, pinyin, freq)

    phrasefile.close()


load_phrase("gb_char.table")
load_phrase("gbk_char.table")


#sorting
words_list = list(words_set)
words_list.sort()

oldwords_list = []
for key, value in words_dict.items():
    (word, pinyin) = key
    freq = value
    oldwords_list.append((word, pinyin, freq))
oldwords_list.sort(key=itemgetter(0))


def save_words_list(filename):
    wordsfile = open(filename, 'w')
    for word in words_list:
        wordsfile.writelines([word, os.linesep])
    wordsfile.close()


def save_words_dict(filename):
    wordsfile = open(filename, 'w')
    for (word, pinyin, freq) in oldwords_list:
        freq = str(freq)
        line = "\t".join((word, pinyin, freq))
        wordsfile.writelines([line, os.linesep])
    wordsfile.close()


if __name__ == "__main__":
    save_words_list("words.txt")
    save_words_dict("oldwords.txt")
