#!/usr/bin/python3
import os

from distill import strip_tone
from filteropengram import Untouched, words_dict, load_opengram_dictionary


'''
merge partial opengram into merged_gb*_opengram.txt
'''

def meet_word(outfile, word):
    if not word in words_dict:
        return

    (status, pinyins) = words_dict[word]
    assert Untouched == status

    for (pinyin, freq) in pinyins:
        freq = str(freq)
        oneline = "\t".join((word, pinyin, freq))
        outfile.writelines([oneline, os.linesep])

    del words_dict[word]


def merge_core_dictionary(infilename, outfilename):
    infile = open(infilename, "r")
    outfile = open(outfilename, "w")

    for oneline in infile.readlines():
        oneline = oneline.rstrip(os.linesep)
        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)
        meet_word(outfile, word)

    outfile.close()
    infile.close()


if __name__ == "__main__":
    print('Loading partial opengram dictionary')
    load_opengram_dictionary("partial_opengram.txt")

    print('Merging partial opengram dictionary')
    merge_core_dictionary("merged_gb_char.txt", "merged_gb_char_opengram.txt")
    merge_core_dictionary("merged_gb_phrase.txt", "merged_gb_phrase_opengram.txt")
    merge_core_dictionary("merged_gbk_char.txt", "merged_gbk_char_opengram.txt")

    print('Check remained phrases')
    assert 0 == len(words_dict)
