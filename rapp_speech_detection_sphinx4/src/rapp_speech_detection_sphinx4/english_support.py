#!/usr/bin/env python

#MIT License (MIT)

#Copyright (c) <2014> <Rapp Project EU>

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

# Authors: Athanassios Kintsakis, Manos Tsardoulias
# contact: akintsakis@issel.ee.auth.gr, etsardou@iti.gr


import rospy
import sys
import mmap

from global_parameters import GlobalParams

from limited_vocabulary_creator import *

class EnglishSupport(GlobalParams):

  def __init__(self):
    GlobalParams.__init__(self)

    self.generic_sphinx_configuration = {}
    self.limited_sphinx_configuration = {}

    self.vocabulary = LimitedVocabularyCreator()
    # TODO: Split the rapp_sphinx4_java_libraries package into libraries and
    # language models
    self.english_dictionary = self.language_models_url + \
        "/englishPack/cmudict-en-us.dict"
       
    jar_path = ".:" + self.sphinx_jar_files_url + "/sphinx4-core-1.0-SNAPSHOT.jar:" \
            + self.sphinx_package_url + "/src"

    # Grammar is dummy here..
    # NOTE: Check acoustic model!!
    self.generic_sphinx_configuration = { \
      'jar_path' : jar_path, \
      'configuration_path' : self.language_models_url + "/greekPack/default.config.xml", \
      'acoustic_model' : self.acoustic_models_url, \
      'grammar_name' : 'hello', \
      'grammar_folder' : self.language_models_url + "/greekPack/", \
      'dictionary' : self.language_models_url + "/englishPack/cmudict-en-us.dict", \
      'language_model' : self.language_models_url + "/englishPack/en-us.lm.dmp", \
      'grammar_disabled' : True
      }
    
    # Open the generic english dictionary file
    try:
      self.english_dict_file = open(self.english_dictionary, 'r')
    except IOError:
      print "English dictionary could not be opened!"
    # Create a mapping of the file
    self.english_dict_mapping = mmap.mmap(self.english_dict_file.fileno(), 0, \
        access = mmap.ACCESS_READ)

  # Returns [conf, status]
  # conf is the configuration
  # status is either error (string) or True (bool) 
  def getLimitedVocebularyConfiguration(self, words, grammar, sentences):
    enhanced_words = {}
    for word in words:
      index = self.english_dict_mapping.find("\n" + word + " ") 
      if  index == -1:
        return [self.limited_sphinx_configuration, \
                "ERROR: Word " + word + " does not exist in the English Dictionary"]
      else:
        self.english_dict_file.seek(index + 1) # +1 because of the extra \n
        line = self.english_dict_file.readline()
        line = line[:-1] # to erase the \n
        split_line = line.split(" ")
        enhanced_words[split_line[0]] = []
        for i in range(1, len(split_line)):
          enhanced_words[split_line[0]].append(split_line[i])

    [self.limited_sphinx_configuration, success] = \
        self.vocabulary.createConfigurationFiles(enhanced_words, grammar, sentences)

    return [self.limited_sphinx_configuration, success]
  
  def getGenericConfiguration(self):
    return [self.generic_sphinx_configuration, True]