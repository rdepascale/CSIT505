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
i = a = 0
while i < len(file_text):
    tempt_ft = file_text[i:i+1]                     # debug value
    temp_a = file_text[a:i]                         # debug value
    if quote1 == True and file_text[i:i+1] == '\"':
        quote2 = True
        if file_text[a:i].isupper():
            #print(file_text[a:i],"is a character!")     # terminal confirmation
            character_list.append(file_text[a+1:i])      # append character names to list sans quotes
        else:
            quote1 = quote2 = False
    if file_text[i:i+1] == '\"':
        quote1 = True
        a = i
    i += 1

#print(character_list)                                   # verify names are in and we have dupes

# turning the list to a dictionary to a list removes duplicates
character_list = list( dict.fromkeys( character_list ) )
character_list.sort()
#print(character_list)                                   # verify no dupes

# with a list of characters without duplicates we are going to now put them into a dictionary
# the key is the character name and the values are:
# 1- # of times the character speaks
# TO BE PUT IN:
    # words spoken
    # words per line?
    # total characters?
character_tally = {}
i = 0
while i < len(character_list):
    character_tally[character_list[i]] = file_text.count(character_list[i])
    i += 1
    
print(character_tally)