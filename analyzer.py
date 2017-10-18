#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# By Liisa Rätsep

from estnltk import Disambiguator
import sys
from utils import autoanalyze
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--input", dest="in_file", help="Input file path", metavar="FILE")
    parser.add_option("--output", dest="out_file", help="Output file path", metavar="FILE")
    parser.add_option("--conll", action="store_true", dest="conll", help="For reanalyzing files in CoNLLu format", default=False)

    options, _ = parser.parse_args()

    # 'word' contains CoNLL column values
    # other possible values include:
    # sentence - entire sentence
    # index - location in the sentence
    # postag - postag according to vabamorf
    # morf - feats according to vabamorf
    # chains - verbchain that contains this word (optional)

    disambiguator = Disambiguator()

    with open(options.in_file, 'r') as f_in:
        lines = f_in.read().splitlines()

    with open(options.out_file, 'w') as f_out:
        sentence = ''

        if options.conll:
            sentence_lines = []
            for x in range(len(lines)):
                tags = lines[x].split('\t')
                if lines[x] != '':
                    sentence += tags[1] + ' '
                    sentence_lines.append(lines[x])
                if lines[x] == '':
                    for y in range(len(sentence_lines)):
                        tags = sentence_lines[y].split('\t')
                        word = {'head': tags[6], 'deprel': tags[7], 'deps': tags[8], 'misc': tags[9]}
                        f_out.write(autoanalyze(y, word, sentence, disambiguator))
                    f_out.write('\n')
                    sentence = ''
                    sentence_lines = []
        else:
            for x in range(len(lines)):
                if lines[x] != '':
                    sentence += lines[x] + ' '
                if lines[x] == '':
                    for y in range(len(sentence.split())):
                        word = {}
                        f_out.write(autoanalyze(y, word, sentence, disambiguator))
                    f_out.write('\n')
                    sentence = ''
