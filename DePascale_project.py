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

# create count of word form word_list by iterating through the list_lines
def word_count(word_list):
    for i in range( len(list_lines) ):
        for j in range( len(word_list) ):
            if word_list[j][0] in list_lines[i]:        # if a match is found
                word_list[j][1] += 1                    # count is incremented by 1
                word_list[j].append(list_lines[i][0])   # append name of speaker of word
    return(word_list)

file_str = "datasets/datasets_25491_32521_SW_EpisodeV.txt"
#file_str = "datasets/sw_v_temp.txt"
pos_word_str = "datasets/positive_words.txt"
neg_word_str = "datasets/negative_words.txt"

# import positive and negative words to list split at ',' and made lowecase
with open(pos_word_str) as file:
    pos_words = file.read().lower().split(',')
file.close()
with open(neg_word_str) as file:
    neg_words = file.read().lower().split(',')
file.close()

# create sublist of WORD, COUNT for future analysis of positive and negative words
for i in range( len(pos_words) ):
    pos_words[i] = [pos_words[i], 0]
for i in range( len(neg_words) ):
    neg_words[i] = [neg_words[i], 0]

# read script into a list for manipulation
# split at space, text lowercase, no punctuation
# translate() adadpted from: https://stackoverflow.com/questions/34293875/how-to-remove-punctuation-marks-from-a-string-in-python-3-x-using-translate
with open(file_str) as file:
    list_lines = [line.lower().translate( str.maketrans('', '', string.punctuation) ).split() for line in file]
file.close()

# first index in list_lines after first line is a number, remove it    
for line in range(1, len(list_lines)):
    del list_lines[line][0]    

# delete first row of non-useful data in list_lines
del list_lines[0]

# sort row to begin looking at calculations
list_lines.sort()

# make character names uppercase at start of line to differentiate with when they are mentioned in script
for i in range( len(list_lines) ):
    list_lines[i][0] = list_lines[i][0].upper()

# get count of occurance of word type and append speaker
word_count(pos_words)
word_count(neg_words)

#This will insert the character name and number of words into a new list
list_tally = []
for i in range( len(list_lines) ):
    # inserts character name then the count of words by counting elements AFTER name in list
    list_tally.append( [ list_lines[i][0], len(list_lines[i][1 : len(list_lines[0]) ] ) ] )
    # inserts blank element between name and word count for purposes of character count
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
    except IndexError:                              # an IndexError means we have trimmed all non-unique entries, end the loop
        break

# trim out entries with count of zero for each list
trim_list(neg_words, 1)
trim_list(pos_words, 1)

# graph data section
# color codes sourced from
# https://matplotlib.org/3.1.0/gallery/color/named_colors.html
graph_colors = ['royalblue', 'orangered', 'green', 'gold', 'violet', 'silver', 'lightgreen', 'navajowhite']
line_values = sorted(list_tally, key = operator.itemgetter(1), reverse = True)
word_values = sorted(list_tally, key = operator.itemgetter(2), reverse = True)
graph_name_values = []
graph_line_values = []
graph_word_values = []
# top 7 characters in line and word are the same, focus on them for individual comparison
for i in range( 7 ):
    graph_name_values.append(line_values[i][0])
    graph_line_values.append(line_values[i][1])
    graph_word_values.append(word_values[i][2]) 

# all other characters occupy 8th slot as "others" to demonstrate main character share vs everyone not in top 7
graph_name_values.append("OTHERS")
graph_line_values.append(0)
graph_word_values.append(0)
for i in range( 8, len(line_values) ):
    graph_line_values[7] += line_values[i][1]
    graph_word_values[7] += word_values[i][2]

'''
# graph adapted from
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