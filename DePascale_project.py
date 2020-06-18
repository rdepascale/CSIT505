#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 15:31:36 2020

@author: ryanrien
"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import operator
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
from nltk import ngrams

# operator
# allows us to create more advanced sorting based on sublist element
# sorted(list_name, key = operator.itemgetter(sublist element number)) <= ascending order
# sorted(list_name, key = operator.itemgetter(sublist element number), reverse = True) <= descending order

# function to remove sublists providing the nth index in the sublist is zero
def trim_list( list_name, n ):
    i = 0
    while True:
        try:
            if list_name[i][n] == 0:  # verify quantity is zero
                del list_name[i]      # delete the entry
            else:                     # i is only increased when the value is non-zero
                i += 1
        except IndexError:            # an IndexError means we have trimmed all non-unique entries, end the loop
            break
    return(list_name)

# import words from dataset to list split at ',' and make lowercase
def read_words(word_str):
    with open(word_str, 'r') as file:
        words = file.read().lower().split(',')
    file.close()
    # create a sublist of WORD, COUNT for later analysis
    for i in range( len(words) ):
        words[i] = [words[i], 0]
    return words

# create count of word form word_list by iterating through the list_lines
def word_count(word_list):
    for i in range( len(list_lines) ):
        for j in range( len(word_list) ):
            if word_list[j][0] in list_lines[i]:        # if a match is found
                word_list[j][1] += 1                    # count is incremented by 1
                word_list[j].append(list_lines[i][0])   # append name of speaker of word
    return(word_list)

# format trimed word list as [ [word, count], [character1, count], [character2, count], etc.]
def word_tally(word_list):
    tally = []                              
    for i in range(len(word_list)):                             # iterate through all elements in a given "row"          
        tally.append([word_list[i][:2]])                        # append current word and total count to first index as sublist
        count = 1
        for j in range(2, len(word_list[i])):                   # iterate through "row" looking at who spoke the word
            try:
                if word_list[i][j] == word_list[i][j+1]:        # if the speaker matches
                    count += 1                                  # increase speaker wordcount
                else:                                           # no more instance of speaker
                    tally[i].append([word_list[i][j], count])   # append speaker and wordcount to sublist
                    count = 1                                   # reset wordcount to 1
            except IndexError:                                  # catch when we end the row
                tally[i].append([word_list[i][j], count])       # append speaker and wordcount to sublist
                count = 1                                       # reset the count
    return(tally)                                               # return final list

# take list of [character, line#, word# ] and amend to have count of pos/neg word in substring
# tally should be list_tally
# words should be pos_words or neg_words
# n = index in sublist to update count, specified in code
def tally_amend(tally, words, n):
    for i in range( len(tally) ):
        tally[i].extend([0])
    for i in range( len(tally) ):
        for j in range( len(words) ):
            for k in range(2, len(words[j]) ):
                if tally[i][0] == words[j][k]:
                    tally[i][n] +=1
    return tally

# takes names of focus characters and creates a list with [name1, all dialog, name2, all dialog, etc.]
# takes prior list and sublists [[name1, all dialog], [name1, all dialog], etc.]
def name_grams(list_grams, sub_grams):
    # create list of [CHARACTER1, all dialog, CHARACTER2, all dialog, etc.]
    for i in range( len( graph_name_values )-1 ):
        list_grams.append(graph_name_values[i])
        for j in range( len( list_lines ) ):
            if list_lines[j][0] == graph_name_values[i]:
                list_grams.extend( list_lines[j][1:] )
    a = 0                                       # index 0 is first name in list_grams
    for i in range( 1, len(list_grams) ):       # ignore index 0 as it is a NAME
        if list_grams[i].isupper():             # when the current index is a NAME
            sub_grams.append(list_grams[a:i])   # append a sublist from prior name to current name
            a = i                               # store value of new NAME
        elif i == len(list_grams)-1:            # captures end of iteration over list_grams
            sub_grams.append(list_grams[a:i+1]) # appends next NAME to first element in next sublist
    return(list_grams, sub_grams)

# takes a blank list as input and populates it with sublist of ['NAME', {dict of trigrams}]
# notworking attempt to trim dictionaries where value is 1
def dict_grams(list_dict_grams):
    for i in range( len(graph_name_values)-1 ):
        d = {}
        # adapted from https://stackoverflow.com/a/28304388
        for ngram, freq in nltk.collocations.TrigramCollocationFinder.from_words(sub_grams[i][1:]).ngram_fd.items():                                        # iterate over object
            d[ngram] = freq                # create key of trigram, value frequency
        list_dict_grams.append([graph_name_values[i],d])
    return(list_dict_grams)
'''    for n in range( len(list_dict_grams) ):
        ldg_sort = sorted(list_dict_grams[n][1].items(), key = lambda kv:(kv[1], kv[0]), reverse = True)
        i = 0
        while True:
            try:
                if ldg_sort[i][1] < 2:
                    del ldg_sort[i]
                else:
                        i += 1
            except IndexError:
                break
        list_dict_grams[n][1] = dict(ldg_sort)
    return(list_dict_grams)'''

# Datasets to be used in analysis
file_str = "datasets/datasets_25491_32521_SW_EpisodeV.txt"
pos_word_str = "datasets/positive_words.txt"
neg_word_str = "datasets/negative_words.txt"

''' Star Wars Episode V Script '''
# read script into a list for manipulation
# split at space, text lowercase, no punctuation
# translate() adapted from:
# https://stackoverflow.com/questions/34293875/how-to-remove-punctuation-marks-from-a-string-in-python-3-x-using-translate
with open(file_str, 'r') as file:
    list_lines = [line.lower().translate( str.maketrans('', '', string.punctuation) ).split() for line in file]
file.close()

# delete first row of non-useful data in list_lines
del list_lines[0]

# first index in list_lines after first line is a number, remove it
# character name is now first index, make it uppercase so that we can
# differentiate with when they are mentioned in script if needed
for i in range(len(list_lines)):
    del list_lines[i][0]
    list_lines[i][0] = list_lines[i][0].upper()

# sort row to begin looking at calculations
list_lines.sort()

#This will insert the character name and number of words into a new list
list_tally = []
for i in range( len(list_lines) ):
    # inserts character name then the count of words by counting elements AFTER name in list
    list_tally.append( [ list_lines[i][0], len(list_lines[i][1 : len(list_lines[0]) ] ) ] )
    # inserts blank element between name and word count for purposes of line count
    list_tally[i].insert(1,1)


# continuing from above we are adding in the line count and word count to the associated name
i = 0
while True:
    try:
        if list_tally[i][0] == list_tally[i+1][0]:  # verify if the names are the same
            list_tally[i][1] += 1                   # increment the # of spoken lines
            list_tally[i][2] += list_tally[i+1][2]  # sum the number of spoken words
            del list_tally[i+1]                     # delete the next entry
        else:                                       # i is only increased when the next entry name is unique
            i += 1
    except IndexError:                              # IndexError means all non-unique entries trimmed
        break                                       # end the loop

''' Postiive and Negative Words '''
# import dataset to lists
pos_words = read_words(pos_word_str)
neg_words = read_words(neg_word_str)

# get count of occurance of word type and append speaker
word_count(pos_words)
word_count(neg_words)

# trim out entries with count of zero for each list
trim_list(neg_words, 1)
trim_list(pos_words, 1)

# get tally of [ [word, count], [char1, count], [char2, count], etc.]
pos_word_tally = word_tally(pos_words)
neg_word_tally = word_tally(neg_words)

# amend list_tally to be formatted with sublist elements [name, #lines, #words, #pos, #neg]
tally_amend(list_tally, pos_words, 3)
tally_amend(list_tally, neg_words, 4)


''' Graph Section '''
# color codes sourced from
# https://matplotlib.org/3.1.0/gallery/color/named_colors.html
graph_colors = ['royalblue', 'orangered', 'green', 'gold', 'violet', 'silver', 'lightgreen', 'navajowhite']
line_values = sorted(list_tally, key = operator.itemgetter(1), reverse = True)
word_values = sorted(list_tally, key = operator.itemgetter(2), reverse = True)
graph_name_values = []
graph_line_values = []
graph_word_values = []
graph_pos_values = []
graph_neg_values = []

# top 7 characters in line and word are the same, focus on them for individual comparison
for i in range( 7 ):
    graph_name_values.append(line_values[i][0])
    graph_line_values.append(line_values[i][1])
    graph_word_values.append(word_values[i][2])
    graph_pos_values.append(line_values[i][3])
    graph_neg_values.append(line_values[i][4])

# all other characters occupy 8th slot as "others" to demonstrate main character share vs everyone not in top 7
graph_name_values.append("OTHERS")
graph_line_values.append(0)
graph_word_values.append(0)
graph_pos_values.append(0)
graph_neg_values.append(0)
for i in range( 8, len(line_values) ):
    graph_line_values[7] += line_values[i][1]
    graph_word_values[7] += word_values[i][2]
    graph_pos_values[7] += line_values[i][3]
    graph_neg_values[7] += line_values[i][4]
'''
# graphs adapted from
# https://matplotlib.org/3.1.3/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py

x = np.arange(len(graph_name_values))
width = 0.35

fig, ax = plt.subplots(dpi = 120)
rects1 = ax.bar(x - width/2, graph_line_values, width, label = '# of lines')
rects2 = ax.bar(x + width/2, graph_word_values, width, label = '# of words')

# grouped bar graph
ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Lines and Words per Character')
ax.set_xticks(x)
ax.set_xticklabels(graph_name_values)
ax.legend()
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.show()

# word count graph
fig, ax = plt.subplots(dpi = 120)
ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Words per Character')
ax.set_xticklabels(graph_name_values)
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.bar(graph_name_values, graph_word_values, color = graph_colors)
plt.show()

# line count graph
fig, ax = plt.subplots(dpi = 120)
ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Lines per Character')
ax.set_xticklabels(graph_name_values)
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.bar(graph_name_values, graph_line_values, color = graph_colors)
plt.show()

# pos word count graph
fig, ax = plt.subplots(dpi = 120)
ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Positive Word Count per Character')
ax.set_xticklabels(graph_name_values)
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.bar(graph_name_values, graph_pos_values, color = graph_colors)
plt.show()

# neg word count graph
fig, ax = plt.subplots(dpi = 120)
ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Negative Word Count per Character')
ax.set_xticklabels(graph_name_values)
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.bar(graph_name_values, graph_neg_values, color = graph_colors)
plt.show()

# pie charts of data for top 7 characters based on word & line counts
# adapted from
# https://matplotlib.org/3.2.1/gallery/pie_and_polar_charts/pie_demo2.html#sphx-glr-gallery-pie-and-polar-charts-pie-demo2-py
# https://matplotlib.org/3.2.1/gallery/subplots_axes_and_figures/subplots_demo.html
    
# make figure and axes
fig, (ax1, ax2) = plt.subplots(2, 1, dpi = 120)
fig.suptitle('Top 7 Speaking Characters Line Count & Word Count Share')
ax1.set_xlabel('Share By Line Count')
ax2.set_xlabel('Share By Word Count')
ax1.pie(graph_line_values, labels = graph_name_values, autopct='%1.1f%%', shadow = True, colors = graph_colors)
ax2.pie(graph_word_values, labels = graph_name_values, autopct='%1.1f%%', shadow = True, colors = graph_colors)
fig.set_size_inches(11, 8.5)
plt.show()
'''

''' nGrams Section '''
list_grams = []
sub_grams = []
name_grams(list_grams, sub_grams)

list_dict_grams = []
dict_grams(list_dict_grams)


''' TF-IDF section '''








