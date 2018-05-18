import nltk

#import brown corpus
from nltk.corpus import brown

#Make sure we get the right tagset
nltk.data.path.insert(0,'/group/ltg/projects/fnlp/nltk_data')

# module for training a Hidden Markov Model and tagging sequences
from nltk.tag.hmm import HiddenMarkovModelTagger

# module for computing a Conditional Frequency Distribution
from nltk.probability import ConditionalFreqDist

# module for computing a Conditional Probability Distribution
from nltk.probability import ConditionalProbDist, LidstoneProbDist

### added:
from nltk.tag import map_tag
assert map_tag('brown','universal','NR-TL')=='NOUN','''
The installed Brown-to-Universal POS tag map is out of date. 
Replace ~/nltk_data/taggers/universal_tagset/en-brown.map with 
https://raw.githubusercontent.com/slavpetrov/universal-pos-tags/master/en-brown.map
'''
###

import operator
import random
from math import log

class HMM:
  def __init__(self,train_data,test_data):
    self.train_data = train_data
    self.test_data = test_data
    self.states = []
    self.viterbi = []
    self.backpointer = []

  #TODO
  #compute emission model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin and an extra bin
  def emission_model(self,train_data):
    #TODO prepare data
    #don't forget to lowercase the observation otherwise it mismatches the test data
    data = 'fixme'

    #TODO compute the emission model
    emission_FD = 'fixme'
    self.emission_PD = 'fixme'
    self.states = 'fixme'
    print "states: ",self.states,"\n\n"
    #states:  [u'.', u'ADJ', u'ADP', u'ADV', u'CONJ', u'DET', u'NOUN', u'NUM', u'PRON', u'PRT', u'VERB', u'X']

    return self.emission_PD, self.states

  #test point 1a
  def test_emission(self):
    print "test emission"
    t1 = -self.emission_PD['NOUN'].logprob('fulton') #10.7862311423
    t2 = -self.emission_PD['X'].logprob('fulton') #-12.3247431105
    return t1,t2

  #compute transition model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin and an extra bin
  def transition_model(self,train_data):
    data = []
    # TODO: prepare the data
    # the data object should be an array of tuples of conditions and observations
    # in our case the tuples will be of the form (tag_(i),tag_(i+1))
    # DON'T FORGET TO ADD THE START SYMBOL </s> and the END SYMBOL </s>
    for s in train_data:
      pass #TODO
    
    #TODO compute the transition model
    transition_FD = 'fixme'
    self.transition_PD = 'fixme'
 
    return self.transition_PD
  
  #test point 1b
  def test_transition(self):
    print "test transition"
    transition_PD = self.transition_model(self.train_data)
    start = -transition_PD['<s>'].logprob('NOUN') #1.78408815305
    end = -transition_PD['NOUN'].logprob('</s>') #7.31426080296
    return start,end

  #train the HMM model
  def train(self):
    self.emission_model(self.train_data)
    self.transition_model(self.train_data)
  
  def set_models(self,emission_PD,transition_PD):
    self.emission_PD = emission_PD
    self.transition_PD = transition_PD
  
  #initialise data structures for tagging a new sentence
  #describe the data structures with comments
  #use the models stored in the variables: self.emission_PD and self.transition_PD
  #input: first word in the sentence to tag
  def initialise(self,observation):
    del self.viterbi[:]
    del self.backpointer[:]
    #initialise for transition from <s> , begining of sentence
    # use costs (-log-base-2 probabilities)
    #TODO
    
    #initialise backpointer
    #TODO
  
  #tag a new sentence using the trained model and already initialised data structures
  #use the models stored in the variables: self.emission_PD and self.transition_PD
  #update the self.viterbi and self.backpointer datastructures
  #describe your implementation with comments
  #input: list of words
  def tag(self,observations):
    tags = []
    index = 0
    current_decision = []
    
    for t in range(1,len(observations)):
      for state in self.states:
        pass #TODO update the viterbi and backpointer data structures
        
    #TODO
    #add termination step (for transition to </s> , end of sentence)
  
    #TODO
    #reconstruct the tag sequence using the backpointer
    #return the tag sequence corresponding to the best path as a list (order should match that of the words in the sentence)
    tags = 'fixme'
    
    return tags

def answer_question4b():
    # Find a tagged sequence that is incorrect
    tagged_sequence = 'fixme'
    correct_sequence = 'fixme'
    # Why do you think the tagger tagged this example incorrectly?
    answer = 'fixme'
    return tagged_sequence, correct_sequence, answer

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    # http://stackoverflow.com/a/33024979
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def main():
  #devide corpus in train and test data
  tagged_sentences_Brown = brown.tagged_sents(categories= 'news')
  exit() # move me down as you fill in implementations

  test_size = 1000
  train_size = len(tagged_sentences_Brown)-1000

  train_data_Brown = tagged_sentences_Brown[:train_size]
  test_data_Brown = tagged_sentences_Brown[-test_size:]

  tagged_sentences_Universal = brown.tagged_sents(categories= 'news', tagset='universal')
  train_data_Universal = tagged_sentences_Universal[:train_size]
  test_data_Universal = tagged_sentences_Universal[-test_size:]


  #create instance of HMM class and initialise the training and test sets
  obj = HMM(train_data_Universal,test_data_Universal)
  
  #train HMM
  obj.train()
  
  #part A: test emission model
  t1,t2 = obj.test_emission()
  print t1,t2
  if isclose(t1,10.7862311423) and isclose(t2,12.3247431105): ### updated again
    print "PASSED test emission\n"
  else:
    print "FAILED test emission\n"
  
  #part A: test transition model
  start,end = obj.test_transition()
  print start,end
  if isclose(start,1.78408815305) and isclose(end,7.31426080296):
    print "PASSED test transition\n"
  else:
    print "FAILED test transition\n"

  #part B: test accuracy on test set
  result = []
  correct = 0
  incorrect = 0
  accuracy = 0
  for sentence in test_data_Universal:
    s = [word.lower() for (word,tag) in sentence]
    obj.initialise(s[0])
    tags = obj.tag(s)
    for i in range(0,len(sentence)):
      if sentence[i][1] == tags[i]:
        correct+=1
      else:
        incorrect+=1
  accuracy = 1.0*correct/(correct+incorrect)
  print "accuracy: ",accuracy #accuracy:  0.857186331623
  if isclose(accuracy,0.857186331623): ### updated
    print "PASSED test viterbi\n"
  else:
    print "FAILED test viterbi\n"

  # print answer for 4b
  tags, correct_tags, answer = answer_question4b()
  print("The incorrect tagged sequence is:")
  print(tags)
  print("The correct tagging of this sentence would be:")
  print(correct_tags)
  print("A possible reason why this error may have occured is:")
  print(answer[:280])

if __name__ == '__main__':
	
	main()









