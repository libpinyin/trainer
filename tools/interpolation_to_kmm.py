#!/usr/bin/python3

import os
import sys
from argparse import ArgumentParser

items = []
arraycount = {}
unigram = {}

phrases = {}
seen_in_unigram = set()

def writeRestUnigram(outfile):
    # Write out
    for token, count in arraycount.items():
        if token in seen_in_unigram:
            pass
        else:
            string = phrases[token]
            count = unigram[token] if token in unigram else 0
            inline = "\item {0} {1} count {2}".format(token, string, count)
            outline = writeUnigramItem(inline)
            outfile.writelines([outline, os.linesep])
    for token, freq in unigram.items():
        if token in seen_in_unigram:
            pass
        else:
            string = phrases[token]
            count = unigram[token]
            inline = "\item {0} {1} count {2}".format(token, string, count)
            outline = writeUnigramItem(inline)
            outfile.writelines([outline, os.linesep])

def parseUnigramItem(oneline):
    assert oneline.startswith("\\item")


def parseBigramItem(oneline):
    assert oneline.startswith("\\item")
    (linetype, firsttoken, firststring,
     secondtoken, secondstring, tagcount, count) = oneline.split(" ")
    assert linetype == "\\item"
    assert tagcount == "count"
    firsttoken = int(firsttoken)
    secondtoken = int(secondtoken)
    count = int(count)
    items.append((firsttoken, secondtoken, count))

    if firsttoken in arraycount:
        arraycount[firsttoken] += count
    else:
        arraycount[firsttoken] = count
        
    if secondtoken in unigram:
        unigram[secondtoken] += count
    else:
        unigram[secondtoken] = count

    # save in phrases
    if firsttoken in phrases:
        assert firststring == phrases[firsttoken]
    else:
        phrases[firsttoken] = firststring

    if secondtoken in phrases:
        assert secondstring == phrases[secondtoken]
    else:
        phrases[secondtoken] = secondstring


def parseHeader(oneline):
    assert oneline == "\\data model interpolation"

def parseEnd(oneline):
    assert oneline == "\\end"

def parseBody(infile):
    state = None
    for oneline in infile.readlines():
        oneline = oneline.rstrip(os.linesep)
        if oneline.startswith("\\data"):
            parseHeader(oneline)
            continue
        if oneline.startswith("\\1-gram"):
            state = "1-gram"
            continue
        if oneline.startswith("\\2-gram"):
            state = "2-gram"
            continue
        if oneline.startswith("\\end"):
            state = None
            parseEnd(oneline)
            continue
        if oneline.startswith("\\item"):
            if "1-gram" == state:
                parseUnigramItem(oneline)
                continue
            if "2-gram" == state:
                parseBigramItem(oneline)
                continue

def writeUnigramItem(inline):
    assert inline.startswith("\\item")
    (linetype, token, string, tagcount, count) = inline.split(" ")
    assert linetype == "\\item"
    assert tagcount == "count"
    token = int(token)
    oldfreq = int(count)

    count = 0
    if token in arraycount:
        count = arraycount[token]
    freq = 0
    if token in unigram:
        freq = unigram[token]

    assert oldfreq == freq
    outline = "\\item {0} {1} count {2} freq {3}".format(
        token, string, count, freq)

    # write out already
    seen_in_unigram.add(token)

    return outline


def writeBigramItem(inline):
    assert inline.startswith("\\item")
    (linetype, firsttoken, firststring, secondtoken, secondstring, tagcount, count) = inline.split(" ")
    assert linetype == "\\item"
    assert tagcount == "count"
    firsttoken = int(firsttoken)
    secondtoken = int(secondtoken)
    count = int(count)
    T = count
    N_n_0 = 1
    n_1 = 1 if count == 1 else 0
    Mr = count
    outline = "\\item {0} {1} {2} {3} count {4} T {5} N_n_0 {6} n_1 {7} Mr {8}".format(firsttoken, firststring, secondtoken, secondstring, count, T, N_n_0, n_1, Mr)
    return outline

def writeHeader(inline):
    assert inline == "\\data model interpolation"
    count = sum([x[2] for x in items])
    N = 1
    total_freq = count
    outline = "\data model \"k mixture model\" count {0} N {1} total_freq {2}".format(count, N, total_freq)
    return outline

def writeEnd(inline):
    assert inline == "\\end"
    outline = "\\end"
    return outline

def writeBody(infile, outfile):
    state = None
    for inline in infile.readlines():
        inline = inline.rstrip(os.linesep)
        if inline.startswith("\\data"):
            outline = writeHeader(inline)
            outfile.writelines([outline, os.linesep])
            continue
        if inline.startswith("\\1-gram"):
            state = "1-gram"
            outline = "\\1-gram"
            outfile.writelines([outline, os.linesep])
            # write the <start> tag value
            outline = writeUnigramItem("\item 1 <start> count 0")
            outfile.writelines([outline, os.linesep])
            continue
        if inline.startswith("\\2-gram"):
            # assume \2-gram is after \1-gram
            writeRestUnigram(outfile)
            state = "2-gram"
            outline = "\\2-gram"
            outfile.writelines([outline, os.linesep])
            continue
        if inline.startswith("\\end"):
            state = None
            outline = writeEnd(inline)
            outfile.writelines([outline, os.linesep])
            continue
        if inline.startswith("\\item"):
            if "1-gram" == state:
                outline = writeUnigramItem(inline)
                outfile.writelines([outline, os.linesep])
                continue
            if "2-gram" == state:
                outline = writeBigramItem(inline)
                outfile.writelines([outline, os.linesep])
                continue


if __name__ == '__main__':
    parser = ArgumentParser(description='Simple converter.')
    parser.add_argument('infile', help='input file')
    parser.add_argument('outfile', help='output file')

    args = parser.parse_args()
    print(args)

    infile = open(args.infile, "r")
    parseBody(infile)
    infile.close()

    infile = open(args.infile, "r")
    outfile = open(args.outfile, "w")
    writeBody(infile, outfile)
    outfile.close()
    infile.close()
