#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
import re, math

import nltk
from nltk.tokenize.punkt import PunktWordTokenizer

import pyphen

'''
Author: Joao Palotti <joaopalotti@gmail.com>
'''

class redabilityCalc:

    def __init__(self, text):
        self.analyse_text(text)

    def __repr__(self):
        print "Text:", self.__text
        print "Sentences:", self.__sentences
        print "Words:", self.__words
        print "# Sentences:", self.__number_sentences
        print "# Words:", self.__number_words
        print "# Chars:", self.__number_chars
        print "# Syllables:", self.__number_syllables
        print "# More 3 Syllables:", self.__number_polysyllable_words
        print "---------------------------------"
        print "Flesh Reading Ease:", self.get_flesch_reading_ease()
        print "Flesh Kincaid Grade Level:", self.get_flesch_kincaid_grade_level()
        print "Coleman Liau Index:", self.get_coleman_liau_index()
        print "Gunning Fog Index:", self.get_gunning_fog_index()
        print "SMOG Index:", self.get_smog_index()
        print "ARI Index:", self.get_ari_index()
        print "LIX Index:", self.get_lix_index()
        print "Dale-Chall Score:", self.get_dale_chall_score()
        return ""

    def analyse_text(self, text):
        self.__text = text
        self.__sentences = self.__get_sentences()
        self.__number_sentences = len(self.__sentences) 
        
        self.__words = self.__get_words()
        self.__number_words = len(self.__words) 

        self.__number_chars = self.__get_number_chars()
        
        self.__number_syllables, self.__number_polysyllable_words = self.__get_number_syllables()

    def __get_sentences(self):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentences = tokenizer.tokenize(self.__text)
        
        sentences_only_chars = []
        #Remove sentences containing only punctuation:
        for sentence in sentences:
            if re.sub("\W","", sentence):
                sentences_only_chars.append(sentence)
        
        return sentences_only_chars

    def __get_words(self):
        
        words = [ w.strip().lower() for w in PunktWordTokenizer().tokenize(self.__text) if w.strip() ]
            
        #Remove punctuation from words:
        # Ex.:  <<This is the final.>>  -> ['<<This', 'is', 'the', 'final.>>'] -> [...,'final']
        words = [re.sub("\W", '', word) for word in words]
        words = [word for word in words if word]
                    
        return words

    def __get_number_chars(self):
        """
            The list of words this method gets is a set of words without punctuation.
        """
        chars = 0
        for word in self.__words:
            chars += len(word)
        return chars

    def __get_number_syllables(self):
        dic = pyphen.Pyphen(lang='en')

        syllables = 0
        words_more_3_syllables = 0

        for word in self.__words:
            syl = len(dic.inserted(word).split("-")) 
            syllables += syl
            if syl >= 3:
                words_more_3_syllables += 1
        return syllables, words_more_3_syllables

    def __get_words_longer_than_X(self, X):
        word_longer_than_X = 0
        for word in self.__words:
            if len(word) > X:
                word_longer_than_X += 1
        return word_longer_than_X
    
    def get_flesch_reading_ease(self):
        #http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
        """
        90.0- 100.0 - sily understood by an average 11-year-old student
        60.0 - 70.0 - easily understood by 13- to 15-year-old students
        0.00 - 30.0 -  best understood by university graduates
        """
        if len(self.__sentences) == 0:
            return 100.0
        return 206.835 - 1.015 * (self.__number_words / self.__number_sentences) - 85.6 * (self.__number_syllables / self.__number_words)
    
    def get_flesch_kincaid_grade_level(self):
        #http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
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
        return ( 5.89 * self.__number_chars / self.__number_words) - ( 30.0 * (self.__number_sentences / self.__number_words) ) -15.8
    
    def get_gunning_fog_index(self):
        # http://en.wikipedia.org/wiki/Gunning_fog_index
        """
        The index estimates the years of formal education needed to understand the text on a first reading
        """
        if self.__number_sentences == 0:
            return 0.0
        return 0.4 * ( (self.__number_words / self.__number_sentences) + 100.0 * ( self.__number_polysyllable_words / self.__number_words) )
    
    def get_smog_index(self):
        # http://en.wikipedia.org/wiki/SMOG
        """
            Simple Measure of Gobbledygook (SMOG) is a simplification of Gunning Fog, also estimating the years of formal education needed
            to understand a text
        """

        if self.__number_sentences == 0:
            return 0.0
        return 1.0430 * math.sqrt( self.__number_polysyllable_words * 30.0 / self.__number_sentences ) + 3.1291

    def get_ari_index(self):
        # http://en.wikipedia.org/wiki/Automated_Readability_Index
        """
            It produces an approximate representation of the US grade level needed to comprehend the text.
        """
        if self.__number_sentences == 0:
            return 0.0
        return 4.71 * (self.__number_chars / self.__number_words) + 0.5 * (self.__number_words / self.__number_sentences)- 21.43
    
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
        long_words = self.__get_words_longer_than_X(6)
        return self.__number_words / self.__number_sentences + ( (100.0 * long_words) / self.__number_words )

    def __get_dale_chall_difficult_words(self):
        with open("dale-challWordList.txt", "r") as d:
            daleWords = set([line.strip() for line in d.readlines()])

        return len( [word for word in self.__words if word not in daleWords ] )

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
        difficult_words = self.__get_dale_chall_difficult_words()
        return 0.1579 * ( difficult_words / self.__number_words * 100.0) + 0.0496 * ( self.__number_words / self.__number_sentences )


if __name__ == "__main__":
    text = "<<This is a small text. Only a few sentences are present. What else can I talk about this text? Well, it has only four sentences!!>>"
    calculator = redabilityCalc(text)
    print calculator 