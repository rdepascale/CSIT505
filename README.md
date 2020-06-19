# CSIT505
# Summer 2020 Project
Analysis of Star Wars Episode V script to look for insights into characters based off of
  - number of lines in script
  - total number of words spoken
  - positive / negative words used in script
  - which characters have the most "script space" (word count/line count)
  - which characters are the most positive/negative (word count/frequency of said words)
  - sentiment analysis
      - ngrams for context
      - positive/negative word choice
      
This is still a work in progress!

# Milestone 2 Report - Update from 6/12/2020

# Graph Work
The double-bar, bar, and pie charts are no longer hard coded into the program.  Each is now implemented through function calls such that a list for the data series, strings for axis label & title, and an n-value for top 7 or inclusion of rest of cast as "others" is possible.

# nGrams Work
Trigrams were decided on as they produced the most balance between number of results and having values returned greater than 1.  The code to find the Trigrams is done through a function call specifically looking for trigrams but can be altered to accomidate an n-value specifying greater/smaller than trigram.  The trigrams are stored in a list where each element is a sublist of ['NAME', dictionary of trigrams] so that using indexing on the list can provide WHO the directory is associated with to avoid confusion.

# WordCloud Work
A function was written to generate WordClouds from data passed into it using len() on the data passed in to determine the maximum number of words.  WordClouds are provided for positive & negative word count as well as the trigrams for the top 7 characters for trigrams that had counts greater than 1, sending in a different dataset of trigrams can show ALL of them if desired although the WordCloud starts looking rather cluttered.

# General Work
This was a lot of code cleanup as well making sure that functions were robust enough to handle the various data types sent to them.  A lot of time was spent looking at what nGrams were returned (bi/tri/etc) and what their counts were.  The work on nGrams was paused to transition to the WordCloud for a sanity check as well as knowing this could be a useful method of visually displaying the nGram results.  As of right now there is a funtion temp_cloud used to turn the dictionary to the data type make_cloud is expecting then call make_cloud from within, this should be merged into make_cloud for the final result as a datatype check combined with an if statement should enable a single function to handle both tasks.  At this moment the "shippable product" took priority over deep bug wrangling.

# TF-IDF
This should be the next/final step after handling initial code work next week mentioned above.  I still have the script/character lines/etc all in various datatypes available within the program so finding an implementation that works given my data arrangement will be the key.  Initial ideas right now are to take the trigrams, break them into unique words for each of the top 7 characters then compare that against the entire script, as I read deeper and conduct additional testing next week this will solidify into a more concrete/numeric piece of data to go with the visual WordCloud work from this week.

=======================================================
# Milestone 1 Report - What Has Been Accomplished So Far
The following datasets have been obtained:
  - Star Wars Episode V script: https://www.kaggle.com/xvivancos/star-wars-movie-scripts/data?select=SW_EpisodeV.txt
  - List of Positive Words: https://positivewordsresearch.com/list-of-positive-words/
  - List of Negative Words: https://positivewordsresearch.com/list-of-negative-words/

# Script Work
The Star Wars Episode V script was pre-formatted as a text file in the form of “LINE NUMBER” “CHARACTER” “DIALOG” for the duration of the script, any manner of stage directions were not present so that did not need accounting for in processing.  Processing occurred as follows:
  - Import script into list list_lines splitting at whitespace to create a sublist of [line number, character name, dialog word 1, dialog word 2, etc.] for the entire line of dialog.
  - While this is going on all characters are being made lowercase and all punctuation removed to prepare for analysis downstream.
  - The first sublist is then deleted because it just contains [‘character’, ‘dialog’] which is understood as the first two entries and would cause any loops to start from 1 rather than 0.
  - list_lines is then iterated through to delete the first element of each sublist (the line number) so now all sublists are in the form [character name, dialog word 1, etc.] then the character name is made uppercase to help differentiate it from when the character is referred to in the dialog later.
    - Ex: if we compare strings “HAN” == ‘han’ would return false so we would not get a false count of his speaking lines or instances of him being mentioned.
  - Finally list_lines is sorted through .sort() so that the list is altered to be in order sorted by speaking character, this is in preparation of creating a new list to produce a list with numerical data about what is going on in the script.
  - list_tally is created to begin the numeric summary by iterating through list_lines and creating a sublist of [character name, number of words in line] then inserting a 1 value for “number of lines” between the two entries in the sublist for the entirety of the script.  The word count is done by counting the number of elements that occur in list_lines AFTER the character name.
  - list_tally is then iterated over to look to see if the current line and the next line have the same ‘character name’ at which point the current line has the line count and word count from the next line summed to it and the next line is then deleted.  If the speakers are not the same we continue to iterate through the list.  A try-except was utilized to catch the IndexError likely to occur to end the while loop without crashing the program.
    - list_tally is now in the form of sublists [character name, number of lines in the script, number of words in the script]

# Positive & Negative Words
The Positive and Negative word lists were acquired through a webpage and had to be put into a text file by me.   To do this I did a copy-paste from the websites into a text editor, deleted the “[Positive/Negatives] words starting with [A/B/C/etc] letter” headings, then used a find/replace to make sure all words were in the form “word1,word2,word3,etc” (note no space between comma and word) since the html formatting did not produce a consistent pattern of word entry.  The positive and negative word lists were then treated as follows:
  - Passed to function read_words to import words from the dataset to a list split at ‘,’ and made all lowercase.
  - Passed to function word_count to create sublists [word, word count, speaker1, speaker2, etc.] by checking the positive or negative word list against the list_lines to look for matches of the words and append speaker of said word.
  - Passed to function trim_list to remove all words that are not in the script (drops list from 1000s of entries to ~130 each) by deleting any entry where the count is zero.  This function also utilizes a try-except of IndexError to break at out of bounds to prevent the program from crashing.
  - Passed to function word_tally to create a new list with sublists [ [word, count], [speaker1, count], [speaker 2, count], etc.] so we can look at overall usage of word as well as granularly with individual characters.
  - Passed to function tally_amend to amend list_tally to be formatted with sublists [name, # lines, #words, #pos words, #neg words].  Function extends existing list_tally sublists with a new element of 0 then adds one to the element if the positive/negative word being looked for is found.

# Graph Work
Basic graphic representation has been done through sorting the initial list_tally by word and line count and noticing the same 7 top entries.  Since these characters had a dominating presence over the script they were chosen as the focus for deeper analysis and the rest of characters in the script were categorized as “other” so as to not ignore them outright but show the overwhelming majority of representation the top 7 have.  The line/word count percentages do not really seem to differ that much according to the graphs so further analysis is going to be in the form of positive/negative words.  Graphs to date are:
  - Double bar chart of #lines/#words for the 8 categories.
  - Bar chart of # words for the 8 categories.
  - Bar chart of # lines for the 8 categories.
  - Pie charts of # lines / #words for the 8 categories.

# Next Steps
The deep analysis of the top 7 characters and positive/negative words is now the focus.  I am at a stage where all of the data is in a form I can use for whatever is most appropriate, which is the key, figuring out WHAT is the most appropriate step.  The frequency characters are using positive/negative words overall and then which (if any) word in that list is most frequent could be an avenue.  I have done some reading on implementing tf-idf (using pandas) and ngrams (using ntlk) in Python 3 and since all the textual data is “there” now I see running my data through these modules to be the crux of the work toward Milestone 2.
