#!/usr/bin/python3
import os
from argparse import ArgumentParser

from distill import strip_tone

'''
this tool accepts the same format as utils/storage/gen_pinyin_table.cpp .

addon dictionaries already removed pinyin tones by distill.py .
'''

# keep the word order and only print once
words_list = []
words_dict = {}


def add_words_dict(word, pinyin, freq):
    pinyin = strip_tone(pinyin)
    if not word in words_dict:
        pinyins = []
        pinyins.append((pinyin, freq))
        words_dict[word] = pinyins
    else:
        pinyins = words_dict[word]

        found = False
        for i, item in enumerate(pinyins):
            (oldpinyin, oldfreq) = item
            if oldpinyin == pinyin:
                # print out the collapsed word and pinyin pair
                print('Collapse: {0} and {1}'.format(word, pinyin))
                freq += oldfreq
                pinyins[i] = (pinyin, freq)
                found = True

        if not found:
            pinyins.append((pinyin, freq))


def load_phrase(filename):
    phrasefile = open(filename, "r")
    for oneline in phrasefile.readlines():
        oneline = oneline.rstrip(os.linesep)
        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)
        # save the word order into word list
        words_list.append(word)
        add_words_dict(word, pinyin, freq)

    phrasefile.close()

def save_phrase(filename):
    phrasefile = open(filename, "w")

    for word in words_list:
        if word in words_dict:
            pinyins = words_dict[word]

            for (pinyin, freq) in pinyins:
                freq = str(freq)
                oneline = "\t".join((word, pinyin, freq))
                phrasefile.writelines([oneline, os.linesep])

            del words_dict[word]

    phrasefile.close()


if __name__ == "__main__":
    parser = ArgumentParser(description='strip tones from gen_pinyin_table input file.')
    parser.add_argument('infile', help='input file')
    parser.add_argument('outfile', help='output file')
    args = parser.parse_args()
    print(args)

    load_phrase(args.infile)
    save_phrase(args.outfile)
