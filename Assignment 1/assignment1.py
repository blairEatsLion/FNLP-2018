#!/usr/bin/python
# coding: utf-8


import nltk
import sys

# extend python path to allow us to import twitter
sys.path.extend(['/group/ltg/projects/fnlp',
'/group/ltg/projects/fnlp/packages_2.6'])

# Import numpy as we will need it to calculate mean and standard deviation
import numpy as np

# Import the Presidential inaugural speeches, Brown and CONLL corpora
from nltk.corpus import inaugural, brown, conll2007

# Import the Twitter corpus and LgramModel
from twitter import xtwc, LgramModel

# Stopword list
from nltk.corpus import stopwords

twitter_file_ids = xtwc.fileids()[11:13]





#################### SECTION A: DATA IN THE REAL WORLD ####################

##### Solution for question 1 #####

# Input: corpus (string), list_of_files (list of strings)
# Output: corpus_tokens (list of strings)
def get_corpus_tokens(corpus, list_of_files):
    corpus_tokens = []

    # Construct "corpus_tokens" (a list of all tokens in the corpus)
    # ...
    for file_name in list_of_files:                     # Loops through all the file names
        for word in corpus.words(file_name):            # Loops through all the words for the file in the corpus
            corpus_tokens.append(word.lower())          # Adds all the words to the corpus_token list

    # Return the list of corpus tokens
    return corpus_tokens

# Input: corpus (string), list_of_files (list of strings), x (int)
# Output: top_tokens (list)
def q1(corpus, list_of_files, x):
    corpus_tokens = []

    # Get a list of all tokens in the corpus
    corpus_tokens = get_corpus_tokens(corpus, list_of_files)

    # Construct a frequency distribution over the lower-cased tokens in the document
    fd_doc_tokens = nltk.FreqDist(corpus_tokens)  # previously: w.lower() for w in

    # Find the top x most frequently used tokens in the document
    top_tokens = fd_doc_tokens.most_common(x)

    # Produce a plot showing the top x tokens and their frequencies
    fd_doc_tokens.plot(x)

    # Return the top x most frequently used tokens
    return top_tokens



##### Solution for question 2 #####

# Input: corpus_tokens (list of strings)
# Output: cleaned_corpus_tokens (list of strings)
def clean_tokens(corpus_tokens):
    stops = [x for x in stopwords.words("english")]
    cleaned_corpus_tokens = []

    # If token is alpha-numeric and NOT in the list of stopwords, add it to cleaned_tokens
    cleaned_corpus_tokens = []

    for word in corpus_tokens:
        if (word in corpus_tokens) and (word not in stops) and (word.isalnum()):
            cleaned_corpus_tokens.append(word)

    # Return the cleaned list of corpus tokens    
    return cleaned_corpus_tokens


# Input: cleaned_corpus_tokens (list of strings), x (int)
# Output: top_tokens (list)
def q2(cleaned_corpus_tokens, x):
    top_tokens = []  # added just for testing

    # Construct a frequency distribution over the lowercased tokens in the document
    fd_doc_tokens = nltk.FreqDist([token.lower() for token in cleaned_corpus_tokens])

    # Find the top x most frequently used tokens in the document
    top_tokens = fd_doc_tokens.most_common(x)

    # Produce a plot showing the top x tokens and their frequencies
    fd_doc_tokens.plot(x)

    # Return the top x most frequently used tokens
    return top_tokens


##### Solution for question 3 #####

# Input: n/a
# Output: answer (string)
def q3():
    answer = "The data is noisy with a high frequency of uncommon english words that display as spikes on the graph are " \
             "more relevant to the twitter corpus. Smoothing techniques such as Laplace smoothing could be used to add " \
             "more weight to unseen words and reduce the spikes in the data."
    assert(len(answer) <= 280)
    return answer



#################### SECTION B: LANGUAGE IDENTIFICATION ####################


##### Solution for question 4 #####

# Input: corpus (string)
# Output: bigram_model (bigram letter LM)
def q4(corpus):
    corpus_tokens = []

    # Build a bigram letter language model using "LgramModel"

    # Creates a list of all alpha-only tokens in the Brown corpus.
    for word in corpus.words():
        if word.isalpha():
            corpus_tokens.append(word)

    # Trains a bigram letter language model using the “cleaned” Brown data
    bigram_model = LgramModel(2, corpus_tokens)

    # Return the letter bigram LM: bigram_model
    return bigram_model



##### Solution for question 5 #####

# Input: file_name (string), bigram_model (bigram letter LM)
# Output: list_of_tweet_entropies (list of tuples: (float,list of strings))
def q5(file_name,bigram_model):
    list_of_tweet_entropies = []
    cleaned_list_of_tweets = []

    # Clean up the tweet corpus to remove all non-alpha tokens and tweets with less than 5 (remaining) tokens
    list_of_tweets = xtwc.sents(file_name)

    # Selects each tweet from a list of tweets and if it is all alpha it checks that num_tokens is greater than 5 and if
    # it is not does not add it to the list of cleaned_tweets
    for tweet in list_of_tweets:
        if tweet.isalpha():

            num_tokens = 0
            for token in tweet:
                num_tokens += 1
                if num_tokens > 5:
                    break
            if num_tokens > 5:
                cleaned_list_of_tweets.append(tweet)

    # For each tweet in the cleaned corpus, compute the average word entropy, and store in a list of tuples of the form: tweet, entropy

            for tweet in cleaned_list_of_tweets:
               no_tokens = 0
               total_entropy = 0.0
               for token in tweet:
                   no_tokens +=1
               total_entropy += bigram_model.entropy(tweet, perItem=True)
               average_entropy = total_entropy/no_tokens
               list_of_tweet_entropies.append((average_entropy, tweet))

    # Sort the list of (entropy,tweet) tuples
    list_of_tweet_entropies.sort()

    # Return the sorted list of tuples
    return list_of_tweet_entropies



##### Solution for question 6 #####

# Input: list_of_tweet_entropies (list of tuples (float,list of strings))
# Output: mean (float), standard deviation (float), list_of_ascii_tweet_entropies (list of tuples (float,list of strings)), list_of_not_English_tweet_entropies (list of tuples (float,list of strings))
def q6(list_of_tweet_entropies):
    mean = 0.0
    standard_deviation = 0.0
    list_of_not_English_tweet_entropies = []
    list_of_ascii_tweet_entropies = []  # added just for testing


    # Find the "ascii" tweets - those in the top 90% of list_of_tweet_entropies
    #threshold = ...
    #list_of_ascii_tweet_entropies = list_of_tweet_entropies[:threshold]
    
    # Extract a list of just the entropy values
    #list_of_entropies = ...

    # Compute the mean of entropy values for top 90% of list_of_tweet_entropies
    #mean = ...

    # Compute the standard deviation of entropy values for top 90% of list_of_tweet_entropies
    #standard_deviation = ...
    
    # Get a list of "probably not English" tweets {"ascii" tweets with an entropy greater than (mean + (0.674 * std_dev)){
    #threshold = mean + (0.674 * standard_deviation)
    #...
    #list_of_not_English_tweet_entropies.sort()
    
    # Return the mean and standard_deviation values
    return (mean, standard_deviation, list_of_ascii_tweet_entropies, list_of_not_English_tweet_entropies)





##### Answers #####
def answers():
    ### Question 1
    print "*** Question 1 ***"
    print "Top 50 tokens for the inaugural corpus:"
    answer1a = q1(inaugural,inaugural.fileids(),50)
    print answer1a
    print "Top 50 tokens for the twitter corpus:"
    answer1b = q1(xtwc,twitter_file_ids,50)
    print answer1b
    ### Question 2
    print "*** Question 2 ***"
    corpus_tokens = get_corpus_tokens(inaugural,inaugural.fileids())
    answer2a = clean_tokens(corpus_tokens)
    print "Inaugural Speeches:"
    print "Number of tokens in original corpus: " + str(len(corpus_tokens))
    print "Number of tokens in cleaned corpus: " + str(len(answer2a))
    print "First 100 tokens in cleaned corpus:"
    print answer2a[:100]
    print "-----"
    corpus_tokens = get_corpus_tokens(xtwc,twitter_file_ids)
    answer2b = clean_tokens(corpus_tokens)
    print "Twitter:"
    print "Number of tokens in original corpus: " + str(len(corpus_tokens))
    print "Number of tokens in cleaned corpus: " + str(len(answer2b))
    print "First 100 tokens in cleaned corpus:"
    print answer2b[:100]

    print "Top 50 tokens for the cleaned inaugural corpus:"
    answer2c = q2(answer2a, 50)
    print answer2c
    print "Top 50 tokens for the cleaned twitter corpus:"
    answer2d = q2(answer2b, 50)
    print answer2d
    ### Question 3
    print "*** Question 3 ***"
    answer3 = q3()
    print answer3[:280]
    ### Question 4
    print "*** Question 4: building brown bigram letter model ***"
    brown_bigram_model = q4(brown)
    ### Question 5
    print "*** Question 5 ***"
    answer5 = q5("20100128.txt",brown_bigram_model)
    print "Top 10 entropies:"
    print answer5[:10]
    print "Bottom 10 entropies:"
    print answer5[-10:]
    ### Question 6
    print "*** Question 6 ***"
    answer6 = q6(answer5)
    print "Mean: " + str(answer6[0])
    print "Standard Deviation: " + str(answer6[1])
    print "ASCII tweets: Top 10 entropies:"
    print answer6[2][:10]
    print "ASCII tweets: Bottom 10 entropies:"
    print answer6[2][-10:]
    print "Probably not English tweets: Top 10 entropies:"
    print answer6[3][:10]
    print "Probably not English tweets: Bottom 10 entropies:"
    print answer6[3][-10:]


if __name__ == '__main__':
    answers()
