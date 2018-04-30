#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
import re
import math
import sys
import bisect

from nltk import tokenize
from .preprocessing import preprocess_html

import pyphen

from .dalechallwords import dale_chall_words
'''
Author: Joao Palotti <joaopalotti@gmail.com>
'''


class ReadCalc:

    def __init__(self, text, language="en", preprocesshtml=None, forcePeriod=False):
        """
            ReadCalc(text, preprocesshtml = None, language="en", forcePeriod = False).

            language:
              Used by the pyphen to break words into syllables.
              Default is English (en).
              A full list of all possible languages can be found online at
              https://github.com/Kozea/Pyphen/tree/master/pyphen/dictionaries

            preprocesshtml:
              It is used to remove html tags.
              The current available options are:

                - None                  ---- Default, no preprocessing is made.
                - justext               ---- Recommended to preprocess html.
                - bs4 (beautifulsoup4)  ---- Watch out for encoding problems.

            forcePeriod:
              It is only available when preprocesshtml is used.
              Options are False (default) and True.
              In case forcePeriod is active, a period mark will be added to every sentence
              extracted by the preprocessing html method employed.
        """
        try:
            self.language = language
            self.text = preprocess_html(text, preprocesshtml, forcePeriod)
        except Exception as e:
            print(("Error %s -- %s" % (type(e), e)))
            self.text = ""
        self.analyse_text()

    def __repr__(self):
        ret = []
        ret.append("# Sentences: %d" % (self.__number_sentences))
        ret.append("# Words: %d" % (self.__number_words))
        ret.append("# Unique Words: %d" % (self.__number_types))
        ret.append("# Chars: %d" % (self.__number_chars))
        ret.append("# Syllables: %d" % (self.__number_syllables))
        ret.append("# 3 Syllables or more: %d" % (self.__number_polysyllable_words))
        ret.append("---------------------------------")
        ret.append("Flesch Reading Ease: %.3f" % (self.get_flesch_reading_ease()))
        ret.append("Flesch Kincaid Grade Level: %.3f" %\
                (self.get_flesch_kincaid_grade_level()))
        ret.append("Coleman Liau Index: %.3f" % (self.get_coleman_liau_index()))
        ret.append("Gunning Fog Index: %.3f" % (self.get_gunning_fog_index()))
        ret.append("SMOG Index: %.3f" % (self.get_smog_index()))
        ret.append("ARI Index: %.3f" % (self.get_ari_index()))
        ret.append("LIX Index: %.3f" % (self.get_lix_index()))
        ret.append("Dale-Chall Score: %.3f" % (self.get_dale_chall_score()))
        ret.append("Dale-Chall Known Faction: %.3f" % (self.get_dale_chall_known_fraction()))
        return "\n".join(ret)

    def analyse_text(self):
        # Divide text into sentences
        sentences = self.get_sentences()
        self.__number_sentences = len(sentences)

        # Divide text into words
        words = self.get_words()
        self.__number_words = len(words)
        self.__number_types = len(set(words))

        self.__number_chars = self.__get_number_chars(words)

        self.__number_syllables, self.__number_polysyllable_words =\
            self.__get_number_syllables(words)

        self.__number_words_larger_X = self.__get_word_sizes(words)
        self.__difficult_words = self.__get_dale_chall_difficult_words(words)

        # Clean up
        for s in sentences:
            del s
        for w in words:
            del w

    def get_sentences(self):
        """
            Returns a list of all sentences found in the text.
        """
        sentences = tokenize.sent_tokenize(self.text)

        sentences_only_chars = []
        # Remove sentences containing only punctuation:
        for sentence in sentences:
            if re.sub("\W", "", sentence):
                sentences_only_chars.append(sentence)

        return sentences_only_chars

    def get_words(self):
        """
            Returns a list of all words found in the text.
        """

        word_tokenizer = tokenize.TreebankWordTokenizer()
        words = [w.strip().lower() for w in word_tokenizer.tokenize(self.text) if w.strip()]

        # Remove punctuation from words:
        # Ex.:  <<This is the final.>>  becomes
        # ['<','<', 'This', 'is', 'the', 'final', '.', '>', '>'] -> ['This', 'is', 'the', 'final']
        words = [re.sub("\W", '', word) for word in words]
        words = [word for word in words if word]

        return words

    def __get_number_chars(self, words):
        """
            Returns the total number of chars in the text.
        """
        chars = 0
        for word in words:
            chars += len(word)
        return chars

    def __get_number_syllables(self, words):
        dic = pyphen.Pyphen(lang=self.language)

        syllables = 0
        words_3_syllables_more = 0

        for word in words:
            syl = len(dic.inserted(word).split("-"))
            syllables += syl
            if syl >= 3:
                words_3_syllables_more += 1
        return syllables, words_3_syllables_more

    def __get_word_sizes(self, words):
        if len(words) == 0:
            return []

        sizes = [len(word) - 0.5 for word in words]
        sorted_sizes = sorted(sizes)
        number_words = len(sizes)
        larger_size = int(sorted_sizes[-1] + 0.5)

        number_words_larger_X = {}

        for S in range(0, larger_size + 1):
            positionS = bisect.bisect_left(sorted_sizes, S)
            number_words_larger_X[S] = number_words - positionS

        return number_words_larger_X

    def get_words_longer_than_X(self, X):
        if len(self.__number_words_larger_X) == 0 or X not in self.__number_words_larger_X:
            return 0

        return self.__number_words_larger_X[X]

    def get_flesch_reading_ease(self):
        # http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
        """
        90.0- 100.0 - sily understood by an average 11-year-old student
        60.0 - 70.0 - easily understood by 13- to 15-year-old students
        0.00 - 30.0 -  best understood by university graduates
        """
        if self.__number_sentences == 0:
            return 100.0
        return 206.835 - 1.015 * (self.__number_words / self.__number_sentences) - 85.6 * (self.__number_syllables / self.__number_words)

    def get_flesch_kincaid_grade_level(self):
        # http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
        """
            It is more or less the number of years of education generally required to understand this text.
            The lowest grade level score in theory is -3.40.
        """
        if self.__number_sentences == 0:
            return 0.0
        return 0.39 * (self.__number_words / self.__number_sentences) + 11.8 * (self.__number_syllables / self.__number_words) - 15.59

    def get_coleman_liau_index(self):
        # http://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index
        """
             It approximates the U.S. grade level thought necessary to comprehend the text.
        """
        if self.__number_sentences == 0 and self.__number_words == 0:
            return 0.0
        return (5.89 * self.__number_chars / self.__number_words) - (30.0 * (self.__number_sentences / self.__number_words)) - 15.8

    def get_gunning_fog_index(self):
        # http://en.wikipedia.org/wiki/Gunning_fog_index
        """
        The index estimates the years of formal education needed to understand the text on a first reading
        """
        if self.__number_sentences == 0:
            return 0.0
        return 0.4 * ((self.__number_words / self.__number_sentences) + 100.0 * (self.__number_polysyllable_words / self.__number_words))

    def get_smog_index(self):
        # http://en.wikipedia.org/wiki/SMOG
        """
            Simple Measure of Gobbledygook (SMOG) is a simplification of Gunning Fog, also estimating the years of formal education needed
            to understand a text
        """

        if self.__number_sentences == 0:
            return 0.0
        return 1.0430 * math.sqrt(self.__number_polysyllable_words * 30.0 / self.__number_sentences) + 3.1291

    def get_ari_index(self):
        # http://en.wikipedia.org/wiki/Automated_Readability_Index
        """
            It produces an approximate representation of the US grade level needed to comprehend the text.
        """
        if self.__number_sentences == 0:
            return 0.0
        return 4.71 * (self.__number_chars / self.__number_words) + 0.5 * (self.__number_words / self.__number_sentences) - 21.43

    def get_lix_index(self):
        # http://en.wikipedia.org/wiki/LIX
        # http://www.readabilityformulas.com/the-LIX-readability-formula.php
        """
            Value interpretation:
            Very Easy      - 20, 25
            Easy           - 30, 35
            Medium         - 40. 45
            Difficult      - 50, 55
            Very Difficult - 60+
        """
        if self.__number_sentences == 0:
            return 0.0
        long_words = self.get_words_longer_than_X(6)
        return self.__number_words / self.__number_sentences + ((100.0 * long_words) / self.__number_words)

    def __get_dale_chall_difficult_words(self, words):
        return len([word for word in words if word not in dale_chall_words])

    def get_dale_chall_score(self):
        # http://en.wikipedia.org/wiki/Dale%E2%80%93Chall_readability_formula
        """
            4.9 or lower    ---  easily understood by an average 4th-grade student or lower
            5.0–5.9         ---  easily understood by an average 5th or 6th-grade student
            6.0–6.9         ---  easily understood by an average 7th or 8th-grade student
            7.0–7.9         ---  easily understood by an average 9th or 10th-grade student
            8.0–8.9         ---  easily understood by an average 11th or 12th-grade student
            9.0–9.9         ---  easily understood by an average 13th to 15th-grade (college) student
            10.0 or higher  ---  easily understood by an average college graduate
        """
        if self.__number_sentences == 0:
            return 0.0
        return 0.1579 * (self.__difficult_words / self.__number_words * 100.0) + 0.0496 * (self.__number_words / self.__number_sentences)

    def get_dale_chall_known_fraction(self):
        """
            Computes the fraction of easy words in the text, i.e., the fraction of words that could be found in the
            dale chall list of 3.000 easy words.
        """
        if self.__number_words == 0:
            return 0.0
        return 1.0 - (self.__difficult_words / self.__number_words)

    def get_internal_metrics(self):
        """
            Returns a tuple with:
             (number_chars, number_words, number_types, number_sentences, number_syllables, number_polysyllable_words,
             difficult_words, number_words_longer_4, number_words_longer_6, number_words_longer_10,
             number_words_longer_longer_13)
        """
        longer_4 = self.get_words_longer_than_X(4)
        longer_6 = self.get_words_longer_than_X(6)
        longer_10 = self.get_words_longer_than_X(10)
        longer_13 = self.get_words_longer_than_X(13)
        return self.__number_chars, self.__number_words, self.__number_types, self.__number_sentences, self.__number_syllables,\
                self.__number_polysyllable_words, self.__difficult_words, longer_4, longer_6, longer_10, longer_13

    def get_all_metrics(self):
        """
            Returns a tuple with:
             (number_chars, number_words, number_types, number_sentences, number_syllables, number_polysyllable_words,
                difficult_words, number_words_longer_4, number_words_longer_6, number_words_longer_10,
                number_words_longer_longer_13, flesch_reading_ease, flesch_kincaid_grade_level, coleman_liau_index,
                gunning_fog_index, smog_index, ari_index, lix_index, dale_chall_score)
        """
        return self.get_internal_metrics() +\
                    (self.get_flesch_reading_ease(), self.get_flesch_kincaid_grade_level(), self.get_coleman_liau_index(),
                     self.get_gunning_fog_index(), self.get_smog_index(), self.get_ari_index(), self.get_lix_index(),
                     self.get_dale_chall_score()
                    )
"""
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("USAGE: python readCalc.py <TEXT>")
        sys.exit(0)

    text = ' '.join(sys.argv[1:])
    calculator = ReadCalc(text)
    print(calculator)
    calculator.get_flesch_kincaid_grade_level()
"""
