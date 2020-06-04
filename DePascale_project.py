#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 15:31:36 2020

@author: ryanrien
"""


file_str = "datasets_25491_32521_SW_EpisodeV.txt"
#file_str = "sw_v_temp.txt"

# read script into a list for manipulation
with open(file_str) as file:
    list_lines = [line.split() for line in file]

# first index in linked list after first line is a number, remove it    
for line in range(1, len(list_lines)):
    del list_lines[line][0]    

# delete first row of non-useful data
del list_lines[0]

# sort row to begin looking at calculations
list_lines.sort()

# remove extraneous quotes from text
# due to importing or set-up of data we may have some non-essential characters, this eliminates the " in specific
for i in range( len(list_lines) ):
    for j in range( len(list_lines[i]) ):
        if list_lines[i][j][0 : 1] == '"' and list_lines[i][j][-1:] == '"':     # catches " at beginning & end of text
            list_lines[i][j] = list_lines[i][j][ 1 : len(list_lines[i][j])-1 ]  # trims via slice
        elif list_lines[i][j][0 : 1] == '"':                                    # catches " at beginning of text
            list_lines[i][j] = list_lines[i][j][ 1 : ]                          # trims via slice
        elif list_lines[i][j][-1:] == '"':                                      # catches " at end of text
            list_lines[i][j] = list_lines[i][j][ : -1 ]                         # trims via slice
# putting in additional check codes for punctuation can fail if one of the above catches this
# think of a solution later!
    
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
'''    
# graph adapted from
# https://matplotlib.org/3.1.3/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

name_values = []
line_values = []
word_values = []
for i in range( len(list_tally) ):
    name_values.append(list_tally[i][0])
    line_values.append(list_tally[i][1])
    word_values.append(list_tally[i][2])'''
'''
x = np.arange(len(name_values))
width = 0.35

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, line_values, width, label = '# of lines')
rects2 = ax.bar(x + width/2, word_values, width, label = '# of words')

ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Lines and Words per Character')
ax.set_xticks(x)
ax.set_xticklabels(name_values)
ax.legend()
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.xticks(rotation=90)
plt.show()'''
'''
# set our x-axis as keys (letters) and y-axis as values (count)
fig, ax = plt.subplots()
ax.set_xlabel('Character Name')
ax.set_title('Star Wars Episode V Lines and Words per Character')
ax.set_xticklabels(name_values)
ax.legend()
fig.tight_layout()
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(11, 8.5)
plt.xticks(rotation=90)
plt.bar(name_values, word_values, color='g')
plt.show() # displays the histogram'''