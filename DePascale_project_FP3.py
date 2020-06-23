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
from wordcloud import WordCloud, STOPWORDS
from collections import Counter


# read script into a list for manipulation
# split at space, text lowercase, no punctuation
# translate() adapted from:
# https://stackoverflow.com/questions/34293875/how-to-remove-punctuation-marks-from-a-string-in-python-3-x-using-translate
def prepare_script(film):
    with open(file_str, 'r') as file:
        lines = [line.lower().translate( str.maketrans('', '', string.punctuation) ).split() for line in file]
    del lines[0]                            # first element is not dialog
    for i in range( len(lines) ):           # iterate through list of lines
        del lines[i][0]                     # delete the first element in the sublist b/c it is a number
        lines[i][0] = lines[i][0].upper()   # make the new first element uppercase b/c it is the speakers name
    lines.sort()                            # sort the list alphabetically by speaker
    return(lines)                           # return the list of lines to the main body


#This will insert the character name and number of words into a new list
def tally_lines(lines):
    tally = []
    for i in range( len(lines) ):
        # inserts character name then the count of words by counting elements AFTER name in list
        tally.append( [ lines[i][0], len(lines[i][1 : len(lines[0]) ] ) ] )
        # inserts blank element between name and word count for purposes of line count
        tally[i].insert(1,1)
        # continuing from above we are adding in the line count and word count to the associated name
    i = 0
    while True:
        try:
            if tally[i][0] == tally[i+1][0]:  # verify if the names are the same
                tally[i][1] += 1              # increment the # of spoken lines
                tally[i][2] += tally[i+1][2]  # sum the number of spoken words
                del tally[i+1]                # delete the next entry
            else:                             # i is only increased when the next entry name is unique
                i += 1
        except IndexError:                    # IndexError means all non-unique entries trimmed
            break                             # end the loop
    return(tally)


# import words from dataset to list split at ',' and make lowercase
# word_str = pos_word_str or neg_word_str
# words = pos_words or neg_words
def read_words(word_str):
    with open(word_str, 'r') as file:
        words = file.read().lower().split(',')
    file.close()
    # create a sublist of WORD, COUNT for later analysis
    for i in range( len(words) ):
        words[i] = [words[i], 0]
    return words


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


# format trimmed word list as [ [word, count], [character1, count], [character2, count], etc.]
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


# create count of word from word_list by iterating through the list_lines
def word_count(word_list):
    for i in range( len(list_lines) ):
        for j in range( len(word_list) ):
            if word_list[j][0] in list_lines[i]:        # if a match is found
                word_list[j][1] += 1                    # count is incremented by 1
                word_list[j].append(list_lines[i][0])   # append name of speaker of word
    return(word_list)


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
def name_grams(lists, subs):
    # create list of [CHARACTER1, all dialog, CHARACTER2, all dialog, etc.]
    for i in range( len( graph_name_values )-1 ):
        lists.append(graph_name_values[i])
        for j in range( len( list_lines ) ):
            if list_lines[j][0] == graph_name_values[i]:
                lists.extend( list_lines[j][1:] )
    a = 0                             # index 0 is first name in list_grams
    for i in range( 1, len(lists) ):  # ignore index 0 as it is a NAME
        if lists[i].isupper():        # when the current index is a NAME
            subs.append(lists[a:i])   # append a sublist from prior name to current name
            a = i                     # store value of new NAME
        elif i == len(lists)-1:       # captures end of iteration over list_grams
            subs.append(lists[a:i+1]) # appends next NAME to first element in next sublist
    return(lists, subs)


# takes a blank list as input and populates it with sublist of ['NAME', {dict of trigrams}]
# sorted output has dictionaries of keys where value is 1 removed
def dict_grams(grams, grams_sorted):
    for i in range( len(graph_name_values)-1 ):
        d = {}
        # adapted from https://stackoverflow.com/a/28304388
        for ngram, freq in nltk.collocations.TrigramCollocationFinder.from_words(sub_grams[i][1:]).ngram_fd.items():                                        # iterate over object
            d[ngram] = freq                # create key of trigram, value frequency
        grams.append([graph_name_values[i],d])
    for n in range( len(grams) ):
        ldg_sort = sorted(grams[n][1].items(), key = lambda kv:(kv[1], kv[0]), reverse = True)
        i = 0
        while True:
            try:
                if ldg_sort[i][1] < 2:  # check if the value of the former key was 1
                    del ldg_sort[i]     # delete said entry, we want values greater than 1 remaining
                else:
                        i += 1          # iterate i
            except IndexError:          # catch IndexError and end loop
                break
        # append character [character name, dictionary] to sorted list
        grams_sorted.append([graph_name_values[n], dict(ldg_sort)])
    return(grams, grams_sorted)


# create a list of frequencies for each word a character speaks
# words = sub_grams [character name, all text]
def frequency(words):
    a = []                              # create a list to store [name, dictionary] in sublists elements
    for i in range( len(words)):        # iterate over the list
        d = dict(Counter(words[i][1:])) # create a dictionary of key: word, value: count
        a.append( [ words[i][0], d ] )  # append [character name, dictionary] to sublist elements
        b = []                          # create empty list for sorting
        for k, v in d.items():          # iterate over key, value in dictionary
            b.append([k,v])             # append to list b sublist [key, value]
            a[i][1] = sorted(b, key = operator.itemgetter(1), reverse = True)   # reverse sort list b, replace dictionary in list a with sorted list b [word, count]
    return(a)                           # return a so that freq_list can be populated


# create a list of frequencies for each character and the positive/negative words
# to be returned for WordCloud
# words = pos_ or neg_word_tally
def hero_words(words):
    h_words = []
    for i in range( len(graph_name_values)-1 ):
        h_words.append( [ graph_name_values[i] ] )
    for n in range( len(h_words) ):
        for i in range( len(words) ):
            for j in range(1, len(words[i]) ):
                if h_words[n][0] == words[i][j][0]:
                    h_words[n].append( [words[i][0][0], words[i][j][1]] )
    return(h_words)


# send list of word count which will be changed to a dictionary with
# key [name] : value [count] that is turned into a wordcloud
# len(list) used max word size
# name is name of character
# title used for file saving
# color is optional
def make_wordcloud(words, name, title, color = None):
    if color == None:                           # handle no color specified scenario
        color = "white"
    word_dict = {}                              # create temporary empty dictionary
    if type(words) == dict:                     # if a dictionary is sent in
        temp = []                               # make a temporary list
        for k, v in words.items():              # iterate through the dictionary
            temp.append([' '.join(k), v])       # turn the tuples to string & make sublist [string of key, count]
        words = temp                            # make set the expected list to the just created one
    for i in range( len(words) ):               # iterate through pos/neg word list
        word_dict[words[i][0]] = words[i][1]    # make the key the current word & value the count
    # generation from dictionary adapted from: https://stackoverflow.com/a/51895005
    wc = WordCloud(
        background_color=color, 
        width = 1600, height = 800, 
        max_words = len(words), min_font_size = 12,
        scale = 3, normalize_plurals = False, stopwords = set(STOPWORDS)).generate_from_frequencies(word_dict)
    fig = plt.figure(1, figsize = (8, 4), dpi = 200)
    wc.to_file(film+"_WordCloud_"+name+"_"+title+".png")
#    comment line above and uncomment lines below to graph in program rather than save file
#    plt.axis('off')
#    plt.imshow(wc)
#    plt.show()
    return()

# sending in empty lists to be populated with data and returned amended to main body
def graph_values(name, line, word, pos, neg):
   # top 7 characters in line and word are the same, focus on them for individual comparison
   for i in range( 7 ):
       name.append(line_values[i][0])
       line.append(line_values[i][1])
       word.append(word_values[i][2])
       pos.append(word_values[i][3])
       neg.append(word_values[i][4])
   # all other characters occupy 8th slot as "others" to demonstrate main character share vs everyone not in top 7
   name.append("OTHERS")
   line.append(0)
   word.append(0)
   pos.append(0)
   neg.append(0)
   for i in range( 8, len(line_values) ):
       line[7] += line_values[i][1]
       word[7] += word_values[i][2]
       pos[7] += word_values[i][3]
       neg[7] += word_values[i][4]
   return(name, line, word, pos, neg)


# Double Bar
# Send list data series, strings for [xlabel, ylabel, title] and n value [7 = top 7 speakers, 8 = top 7 + "others"]
# https://scriptverse.academy/tutorials/python-matplotlib-bar-chart.html
# https://matplotlib.org/3.1.3/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
def double_bar(legend1, data1, legend2, data2, xlabel, ylabel, title, n):
    fig, ax = plt.subplots(dpi = 120)
    index = np.arange( n )
    bar_width = 0.35
    ax.bar(index, data1[0:n], bar_width, color = graph_colors[0:n], label = legend1)
    ax.bar(index+bar_width, data2[0:n], bar_width, alpha = 0.5, color = graph_colors[0:n], label = legend2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(index+bar_width/2)
    ax.set_xticklabels(graph_name_values[0:n])
    ax.legend()
    fig.set_size_inches(11, 8.5)
    plt.grid(axis = 'y')
    #plt.show()
    plt.savefig(film+"_"+title+".png")
    return


# Single Bar Graph
# Send list data series, strings for [xlabel, ylabel, title] and n value [7 = top 7 speakers, 8 = top 7 + "others"]
def single_bar(data, xlabel, ylabel, title, n):
    fig, ax = plt.subplots(dpi = 120)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel) 
    ax.set_title(title)
    ax.set_xticklabels(graph_name_values[0:n])
    fig.tight_layout()
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(11, 8.5)
    plt.bar(graph_name_values[0:n], data[0:n], color = graph_colors)
    plt.grid(axis = 'y')
    #plt.show()
    plt.savefig(film+"_"+title+".png")
    return


# Pie Chart
# Send list data series, string for title, and n value [7 = top 7 speaker,s 8 = top 7 + "others"]
# https://matplotlib.org/3.2.1/gallery/pie_and_polar_charts/pie_demo2.html#sphx-glr-gallery-pie-and-polar-charts-pie-demo2-py
# https://matplotlib.org/3.2.1/gallery/subplots_axes_and_figures/subplots_demo.html
def pie_chart(data, title, n):
    # make figure and axes
    fig, ax = plt.subplots(1, 1, dpi = 120)
    fig.suptitle(title)
    ax.pie(data[0:n], labels = graph_name_values[0:n], autopct='%1.1f%%', shadow = True, colors = graph_colors[0:n])
    fig.set_size_inches(11, 8.5)
    #plt.show()
    plt.savefig(film+"_"+title+".png")
    return


# simple function call to output all graphs as .png files in current working directory
def create_graphs():
    pie_chart(graph_line_values, film[3:]+' Percentage of Line Count Share Top 8', 8)
    pie_chart(graph_line_values, film[3:]+' Percentage of Line Count Share Top 7', 7)
    pie_chart(graph_word_values, film[3:]+' Percentage of Word Count Share Top 8', 8)
    pie_chart(graph_word_values, film[3:]+' Percentage of Word Count Share Top 7', 7)
    pie_chart(graph_pos_values, film[3:]+' Percentage of Positive Word Count Share Top 7', 7)
    pie_chart(graph_neg_values, film[3:]+' Percentage of Negative Word Count Share Top 7', 7)
    double_bar('Lines', graph_line_values, 'Words', graph_word_values, 'Character', 'Count', 'Episode V Line & Word Counts per Character Top 8', 8)
    double_bar('Lines', graph_line_values, 'Words', graph_word_values, 'Character', 'Count', 'Episode V Line & Word Counts per Character Top 7', 7)
    single_bar(graph_word_values, 'Character', 'Count', film[3:]+' Word Count per Character Top 8', 8)
    single_bar(graph_word_values, 'Character', 'Count', film[3:]+' Word Count per Character Top 7', 7)
    single_bar(graph_pos_values, 'Character', 'Count', film[3:]+' Positive Word Count per Character Top 8', 8)
    single_bar(graph_pos_values, 'Character', 'Count', film[3:]+' Positive Word Count per Character Top 7', 7)
    single_bar(graph_neg_values, 'Character', 'Count', film[3:]+' Negative Word Count per Character Top 8', 8)
    single_bar(graph_neg_values, 'Character', 'Count', film[3:]+' Negative Word Count per Character Top 7', 7)
    double_bar('Positive Words', graph_pos_values, 'Negative Words', graph_neg_values, 'Character', 'Count', film[3:]+' Positive & Negative Word Counts per Character Top 8', 8)
    double_bar('Positive Words', graph_pos_values, 'Negative Words', graph_neg_values, 'Character', 'Count', film[3:]+' Positive & Negative Word Counts per Character Top 7', 7)
    return()


# https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76
# Function to specify a SPECIFIC character to compare against the script.
# gram = sub_grams = [character name, every word they say in the script]
# lines = list_lines = [character name, line of dialog]
# n = character in top 7 from sub_grams (0 to 6)
# m = max number of words returned (None disables this)
def two_tfidf(gram, lines, n, m, csv):
    this_string = ''                    # this_string = string of all specified HERO dialog
    this_string = ' '.join(gram[n][1:]) # joins all elements of specified HERO dialog as string separated by ' '
    that_string = ''                    # that_string = string of ALL dialog
    for i in range(len(lines)):         # iterates through whole script joining all elements of dialog as string seperated by ' '
        that_string += ' '.join(lines[i][1:])
    # max_features are maximum number of words sent in by user, None instaed of int will show all words
    vectorizer = TfidfVectorizer( stop_words='english', max_features = m)
    # begin creation of table comparing specified hero vs whole script
    vectors = vectorizer.fit_transform([this_string, that_string])
    feature_names = vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=feature_names )
    if csv == True:
        df.to_csv(film+"_"+str(gram[n][0])+"_tfidf.csv", index = True, header = True)    # Saved as {NAME}_tfidf.csv
    print("\n",gram[n][0],"\n",df)                                              # print character name and datatable
    return(df)                                                                  # DataFrame can be stored for additional variable if desired

# https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76
# Function to compare all top7 characters with the whole script
# gram = sub_grams = [character name, every word they say in the script]
# lines = list_lines = [character name, line of dialog]
# m = max number of words returned (None disables this)
# hero = list of string that is all top 7 characters for each index used to create table of ALL characters vs script
def hero_tfidf(gram, lines, m, csv):
    # hero = list of string that is all top 7 characters for each index used to create table of ALL characters vs script
    hero = []
    # that_string = string of ALL dialog
    that_string = ''
    for i in range(len(gram)):
        hero.append(' '.join(gram[i][1:]))      # Iterate through all HERO entries and append elements of text to new element of string separated by ' '
    for i in range(len(lines)):
        that_string += ' '.join(lines[i][1:])   # iterates through whole script joining all elements of dialog as string seperated by ' '
    # max_features are maximum number of words sent in by user, None instaed of int will show all words
    vectorizer = TfidfVectorizer( stop_words='english', max_features = m)
    # begin creation of table comparing ALL heros with the script
    vectors = vectorizer.fit_transform([hero[0], hero[1], hero[2], hero[3], hero[4], hero[5], hero[6], that_string])
    feature_names = vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df2 = pd.DataFrame(denselist, columns=feature_names )
    if csv == True:
        df2.to_csv(film+"_hero_tfidf.csv", index = True, header = True)   # DataFrame saved to CSV, index & header true preserves row & column names
    return(df2)                                                           # DataFrame can be stored for additional variable if desired

''' Main Program '''
# Datasets to be used in analysis
film = "SW_EpisodeV"
file_str = "datasets/"+film+".txt"
pos_word_str = "datasets/positive_words.txt"
neg_word_str = "datasets/negative_words.txt"

list_lines = prepare_script(film)
list_tally = tally_lines(list_lines)

''' Positive and Negative Words '''
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
# create list sorted by index 1 of list_tally sublists in descending order
line_values = sorted(list_tally, key = operator.itemgetter(1), reverse = True)
# create list sorted by index 2 of list_tally sublists in descending order
word_values = sorted(list_tally, key = operator.itemgetter(2), reverse = True)

# initialize blank values for graphing
graph_name_values = []
graph_line_values = []
graph_word_values = []
graph_pos_values = []
graph_neg_values = []
graph_values(graph_name_values, graph_line_values, graph_word_values, graph_pos_values, graph_neg_values)


''' nGrams Section '''
# create a list with [character name, all text]
list_grams = []
sub_grams = []
name_grams(list_grams, sub_grams)

# send list above to create  a list with [character name, dictionary {trigram:count}]
list_dict_grams = []
list_dict_grams_sorted = []
dict_grams(list_dict_grams, list_dict_grams_sorted)

# create a list organized by [ [NAME1, [word1, count], [word2, count], etc], [NAME2, [word1, count], [word2, count], etc.] ]
# this word frequency list is used to create a wordcloud for top words of each character
# the list is also sorted so that when printed it is in descending order
freq_list = frequency(sub_grams)

# create list of [NAME1, [sublist of word, count]], [NAME2, [sublist of word, count]]
hero_pos_words = hero_words(pos_word_tally)
hero_neg_words = hero_words(neg_word_tally)


''' WordCloud Section '''
# name is name of character
# title used for file saving
# color is optional
# make_wordcloud(words, name, title, color = None)
'''
# send list where sublist has first two elements [word, count] to generate wordcloud
make_wordcloud(pos_words, "All Characters", "Positive Words")   # Generate WordCloud of ALL Positive Words
make_wordcloud(neg_words, "All Characters", "Negative Words")   # Generate WordCloud of ALL Negative Words

# Word Clouds for Top 7
# if a dictionary is sent the function will recognize this and adjust it to the needed
# sublist [string of key, value] setup to work properly
# #1 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[0][1], graph_name_values[0], "Trigrams", graph_colors[0])
make_wordcloud(freq_list[0][1], graph_name_values[0], "Frequent Words", graph_colors[0])
make_wordcloud(hero_pos_words[0][1:], graph_name_values[0], "Positive Words", graph_colors[0])
make_wordcloud(hero_neg_words[0][1:], graph_name_values[0], "Negative Words", graph_colors[0])

# #2 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[1][1], graph_name_values[1], "Trigrams", graph_colors[1])
make_wordcloud(freq_list[1][1], graph_name_values[1], "Frequent Words", graph_colors[1])
make_wordcloud(hero_pos_words[1][1:], graph_name_values[1], "Positive Words", graph_colors[1])
make_wordcloud(hero_neg_words[1][1:], graph_name_values[1], "Negative Words", graph_colors[1])

# #3 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[2][1], graph_name_values[2], "Trigrams", graph_colors[2])
make_wordcloud(freq_list[2][1], graph_name_values[2], "Frequent Words", graph_colors[2])
make_wordcloud(hero_pos_words[2][1:], graph_name_values[2], "Positive Words", graph_colors[2])
make_wordcloud(hero_neg_words[2][1:], graph_name_values[2], "Negative Words", graph_colors[2])

# #4 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[3][1], graph_name_values[3], "Trigrams", graph_colors[3])
make_wordcloud(freq_list[3][1], graph_name_values[3], "Frequent Words", graph_colors[3])
make_wordcloud(hero_pos_words[3][1:], graph_name_values[3], "Positive Words", graph_colors[3])
make_wordcloud(hero_neg_words[3][1:], graph_name_values[3], "Negative Words", graph_colors[3])

# #5 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[4][1], graph_name_values[4], "Trigrams", graph_colors[4])
make_wordcloud(freq_list[4][1], graph_name_values[4], "Frequent Words", graph_colors[4])
make_wordcloud(hero_pos_words[4][1:], graph_name_values[4], "Positive Words", graph_colors[4])
make_wordcloud(hero_neg_words[4][1:], graph_name_values[4], "Negative Words", graph_colors[4])

# #6 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[5][1], graph_name_values[5], "Trigrams", graph_colors[5])
make_wordcloud(freq_list[5][1], graph_name_values[5], "Frequent Words", graph_colors[5])
make_wordcloud(hero_pos_words[5][1:], graph_name_values[5], "Positive Words", graph_colors[5])
make_wordcloud(hero_neg_words[5][1:], graph_name_values[5], "Negative Words", graph_colors[5])

# #7 nGrams, All Words, Pos Words, Neg Words
make_wordcloud(list_dict_grams_sorted[6][1], graph_name_values[6], "Trigrams", graph_colors[6])
make_wordcloud(freq_list[6][1], graph_name_values[6], "Frequent Words", graph_colors[6])
make_wordcloud(hero_pos_words[6][1:], graph_name_values[6], "Positive Words", graph_colors[6])
make_wordcloud(hero_neg_words[6][1:], graph_name_values[6], "Negative Words", graph_colors[6])
'''


''' TF-IDF Section ''' '''
# Create TF-IDF table for character in index 4 limited to top 10 words, save as [char name]_tfidf.csv for example
two_tfidf(sub_grams, list_lines, 4, 10, True)

# Create TF-IDF table for top 7 limsted to top 10 words, save as hero_tfidf.csv for example
hero_tfidf(sub_grams, list_lines, 10, True)'''