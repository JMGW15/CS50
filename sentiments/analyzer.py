import nltk
import os
import cs50

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        self.positives_list = [] #create empty list
        file = open(positives, "r") #open positive file
        for line in file:
            if line.startswith(';') == False:
                self.positives_list.append(line.rstrip("\n"))#add word to the end of the list and strip out the whitespace
        #count = self.positives_list.count('i')
        #print('The count of i is:', count)
        file.close() # close the file
        
        self.negatives_list = [] #create empty list
        file = open(negatives, "r") #open positive file
        for line in file:
            if line.startswith(';') == False: #if line does not start with ; then...
                self.negatives_list.append(line.rstrip("\n"))#add word to the end of the list and strip out the whitespace
        #count = self.negatives_list.count('i')
        #print('The count of i is:', count)
        file.close() # close the file
        
    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        tokenizer = nltk.tokenize.TweetTokenizer(preserve_case=False) #initiate tokenizer and change case of words in output tokens to lowercase
        tokens = tokenizer.tokenize(text) #create tokens of the text
        value = 0 #initialize value to capture sum of words and their corresponding sentiment score
        for word in tokens: 
            if word.lower() in self.positives_list:
                value += 1 # add 1 to value - https://www.tutorialspoint.com/python/python_basic_operators.htm
            elif word.lower() in self.negatives_list: #https://cs50.stackexchange.com/questions/25674/a-simple-question-in-application-py-sentiments
                value -= 1 # subtract 1 from value - https://www.tutorialspoint.com/python/python_basic_operators.htm
            else:
                value += 0 #value += 0 # add nothing to the value - https://www.tutorialspoint.com/python/python_basic_operators.htm
        
        return value
        
        
