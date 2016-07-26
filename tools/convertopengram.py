#!/usr/bin/python3
import os
from argparse import ArgumentParser

from distill import strip_tone

'''
convert the opengram dictionary file format
to libpinyin input file format,
the same format as utils/storage/gen_pinyin_table.cpp .
'''

#minimum pinyin frequency
minimum = 3

#default pinyin total frequency
total_frequency = 100


def handle_pinyin(outfile, word, num, pinyin):
    # no tones in opengram dictionary
    stripped = strip_tone(pinyin)
    assert stripped == pinyin

    freq = 0
    if not ":" in pinyin:
        freq = total_frequency / num
    else:
        (py, freq) = pinyin.split(":", 1)
        assert freq.endswith("%")
        freq = freq.rstrip("%")
        freq = float(freq)
        freq = total_frequency * freq
        pinyin = py

    freq = int(freq)
    freq = max(freq, minimum)
    freq = str(freq)
    oneline = "\t".join((word, pinyin, freq))
    outfile.writelines([oneline, os.linesep])


def handle_line(outfile, line):
    (word, pinyins) = line.split(None, 1)
    pinyin_list = pinyins.split(None)
    num = len(pinyin_list)
    for pinyin in pinyin_list:
        handle_pinyin(outfile, word, num, pinyin)


def handle_file(infilename, outfilename):
    infile = open(infilename, "r")
    outfile = open(outfilename, "w")
    for oneline in infile.readlines():
        oneline = oneline.rstrip(os.linesep)
        handle_line(outfile, oneline)
    outfile.close()
    infile.close()


if __name__ == "__main__":
    parser = ArgumentParser(description='convert opengram dictionary.')
    parser.add_argument('infile', help='input file')
    parser.add_argument('outfile', help='output file')
    args = parser.parse_args()
    print(args)

    handle_file(args.infile, args.outfile)
