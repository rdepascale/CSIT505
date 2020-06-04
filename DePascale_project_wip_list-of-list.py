#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 16:30:42 2020

@author: ryanrien

Star Wars Episode V script progject proof of concept
WIP - take snippet of text, scan and put unique character names into list
"""


file_name = "datasets_25491_32521_SW_EpisodeV.txt"
#file_name = "sw_v_temp.txt"
input_file = open(file_name, 'r')
file_text = input_file.read()
input_file.close()
#print(file_text)

# go through the text file to determine WHERE the characters are.
# the quote1 & quote2 boolean set up a slice of file_text[a:i]
# that we will look at when both quote1 & quote2 are True
# logic as of 6/2/2020 can/needs to be tweaked but works for proof of concept
character_list = []
quote1 = False
i = a = b = 0
while i < len(file_text):
    tempt_ft = file_text[i:i+1]                     # debug value
    temp_a = file_text[a:i]                         # debug value
    if quote1 == True and file_text[i:i+1] == '\"':
        quote2 = True
        if file_text[a:i].isupper():
            #print(file_text[a:i],"is a character!")     # terminal confirmation
            character_list.append(file_text[a+1:i])      # append character names to list sans quotes
            b = i
        else:
            quote1 = quote2 = False
    if file_text[i:i+1] == '\"':
        quote1 = True
        a = i
    if file_text[i:i+1] == '\"' and file_text[i-b:i].isnumeric():
       # FINISH
       character_list.append(file_text[a+1])
    i += 1

#print(character_list)                                   # verify names are in and we have dupes

# turning the list to a dictionary to a list removes duplicates
character_list = list( dict.fromkeys( character_list ) )
character_list.sort()
#print(character_list)                                   # verify no dupes



'''i = 0
while i < len(character_list):
    character_list.append(i,file_text.count(character_list[i]))
    i += 1
print(character_list)'''

# with a list of characters without duplicates we are going to now put them into a dictionary
# key is the character name
# 1st value # of times the character speaks
character_tally = {}
i = 0
while i < len(character_list):
    character_tally[character_list[i]] = file_text.count(character_list[i])
    i += 1
print(character_tally)
print()

# sw_stats is our final list since we may want to change what is "linked" for character name
# TO BE PUT IN:
    # words spoken
    # words per line?
    # total characters in words spoken?
sw_stats = []
for key, value in character_tally.items():
    sw_stats.append([key, value])
print(sw_stats)