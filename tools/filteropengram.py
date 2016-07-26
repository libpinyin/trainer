#!/usr/bin/python3
import os

from distill import strip_tone


'''
filter out the already existing libpinyin phrases from opengram dictionary.
'''

(
# not in libpinyin, move to opengram.txt
Untouched,
# only partial information in libpinyin, save to partial_opengram.txt
Partial,
# already in libpinyin, do nothing
Complete
) = range(3, 6)

# key: word, value: (status, pinyins)
# pinyins: list of (pinyin, freq)
words_dict = {}


def add_words_dict(word, pinyin, freq):
    # assume all tones are already removed
    assert pinyin == strip_tone(pinyin)

    if not word in words_dict:
        status = Untouched
        pinyins = []
        pinyins.append((pinyin, freq))
        words_dict[word] = (status, pinyins)
    else:
        (status, pinyins) = words_dict[word]
        assert Untouched == status

        for i, item in enumerate(pinyins):
            (oldpinyin, oldfreq) = item
            assert oldpinyin != pinyin

        pinyins.append((pinyin, freq))


def filter_out(word, pinyin):
    if not word in words_dict:
        return

    (status, pinyins) = words_dict[word]
    status = Partial

    found = False
    for i, item in enumerate(pinyins):
        (oldpinyin, oldfreq) = item
        if oldpinyin == pinyin:
            del pinyins[i]
            found = True

    if not found:
        print('Missing {0} and {1} in opengram'.format(word, pinyin))

    if 0 == len(pinyins):
        status = Complete

    words_dict[word] = (status, pinyins)


def load_opengram_dictionary(infilename):
    infile = open(infilename, "r")

    for oneline in infile.readlines():
        oneline = oneline.rstrip(os.linesep)
        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)
        add_words_dict(word, pinyin, freq)

    infile.close()


def filter_core_dictionary(infilename):
    infile = open(infilename, "r")

    for oneline in infile.readlines():
        oneline = oneline.rstrip(os.linesep)
        (word, pinyin, freq) = oneline.split(None, 2)
        freq = int(freq)
        filter_out(word, pinyin)

    infile.close()


def save_opengram_dictionary(outfilename):
    outfile = open(outfilename, "w")

    for word in words_dict:
        (status, pinyins) = words_dict[word]
        if Untouched == status:
            for (pinyin, freq) in pinyins:
                freq = str(freq)
                oneline = "\t".join((word, pinyin, freq))
                outfile.writelines([oneline, os.linesep])

    outfile.close()


def save_partial_dictionary(outfilename):
    outfile = open(outfilename, "w")

    for word in words_dict:
        (status, pinyins) = words_dict[word]
        if Partial == status:
            for (pinyin, freq) in pinyins:
                freq = str(freq)
                oneline = "\t".join((word, pinyin, freq))
                outfile.writelines([oneline, os.linesep])

    outfile.close()


if __name__ == "__main__":
    print('Loading opengram dictionary')
    load_opengram_dictionary("dict.full")

    print('Filtering libpinyin dictionary')
    filter_core_dictionary("merged_gb_char.txt")
    filter_core_dictionary("merged_gb_phrase.txt")
    filter_core_dictionary("merged_gbk_char.txt")

    print('Saving opengram dictionary')
    save_opengram_dictionary("opengram.txt")
    print('Saving paritial dictionary')
    save_partial_dictionary("partial_opengram.txt")
