import nltk

# import brown corpus
from nltk.corpus import brown

# Make sure we get the right tagset
nltk.data.path.insert(0, '/group/ltg/projects/fnlp/nltk_data')

# module for training a Hidden Markov Model and tagging sequences
from nltk.tag.hmm import HiddenMarkovModelTagger

# module for computing a Conditional Frequency Distribution
from nltk.probability import ConditionalFreqDist

# module for computing a Conditional Probability Distribution
from nltk.probability import ConditionalProbDist, LidstoneProbDist

### added:
from nltk.tag import map_tag

assert map_tag('brown', 'universal', 'NR-TL') == 'NOUN', '''
The installed Brown-to-Universal POS tag map is out of date.
Replace ~/nltk_data/taggers/universal_tagset/en-brown.map with
https://raw.githubusercontent.com/slavpetrov/universal-pos-tags/master/en-brown.map
'''
###

import operator
import random
from math import log


class HMM:
    def __init__(self, train_data, test_data):
        self.train_data = train_data
        self.test_data = test_data
        self.states = []
        self.viterbi = []
        self.backpointer = []

    # compute emission model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin and an extra bin
    def emission_model(self, train_data):
        # COMPLETED prepare data
        # don't forget to lowercase the observation otherwise it mismatches the test data
        # print("this is emission model")
        print(train_data)

        #Concats all the internal lists in train_data into one long list to be processed
        new_data = []
        for x in range(len(train_data)):
            new_data += train_data[x]

        data = [(tag, word.lower()) for (word, tag) in new_data]
        # print(data[:20])
        # COMPLETED compute the emission model
        emission_FD = ConditionalFreqDist(data)
        self.emission_PD = ConditionalProbDist(emission_FD, LidstoneProbDist, 0.01)
        self.states = emission_FD.keys()
        print "states: ", self.states, "\n\n"
        # states:  [u'.', u'ADJ', u'ADP', u'ADV', u'CONJ', u'DET', u'NOUN', u'NUM', u'PRON', u'PRT', u'VERB', u'X']

        return self.emission_PD, self.states

    # test point 1a
    def test_emission(self):
        print "test emission"
        t1 = -self.emission_PD['NOUN'].logprob('fulton')  # 10.7862311423
        t2 = -self.emission_PD['X'].logprob('fulton')  # -12.3247431105
        return t1, t2

    # compute transition model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin and an extra bin
    def transition_model(self, train_data):
        data = []
        # COMPLETED prepare the data
        # the data object should be an array of tuples of conditions and observations
        # in our case the tuples will be of the form (tag_(i),tag_(i+1))
        # DON'T FORGET TO ADD THE START SYMBOL <s> and the END SYMBOL </s>
        for s in train_data:
            data.append(("<s>", s[0][1]))          #Start Symbol
            for i in range(len(s) - 1):
                data.append((s[i][1], s[i + 1][1]))
            data.append((s[len(s) - 1][1], "</s>"))      #End Symbol

        # COMPLETED compute the transition model
        transition_FD = ConditionalFreqDist(data)
        self.transition_PD = ConditionalProbDist(transition_FD, LidstoneProbDist, 0.01)

        return self.transition_PD

    # test point 1b
    def test_transition(self):
        print "test transition"
        transition_PD = self.transition_model(self.train_data)
        start = -transition_PD['<s>'].logprob('NOUN')  # 1.78408815305
        end = -transition_PD['NOUN'].logprob('</s>')  # 7.31426080296
        return start, end

    # train the HMM model
    def train(self):
        self.emission_model(self.train_data)
        self.transition_model(self.train_data)

    def set_models(self, emission_PD, transition_PD):
        self.emission_PD = emission_PD
        self.transition_PD = transition_PD

    # initialise data structures for tagging a new sentence
    # describe the data structures with comments
    # use the models stored in the variables: self.emission_PD and self.transition_PD
    # input: first word in the sentence to tag
    def initialise(self, observation):

        self.viterbi = [{}]  # A list of dictionaries is used at each point to manage the possible states
        self.backpointer = {}  # Denotes the sequence of tags in a dictionary

        for state in self.states:

            # initialise for transition from <s> , beginning of sentence
            self.viterbi[0][state] = self.transition_PD['<s>'].prob(state) * self.emission_PD[state].prob(observation)
            # initialise backpointer
            self.backpointer[state] = [state]


    # tag a new sentence using the trained model and already initialised data structures
    # use the models stored in the variables: self.emission_PD and self.transition_PD
    # update the self.viterbi and self.backpointer datastructures
    # describe your implementation with comments
    # input: list of words
    def tag(self, observations):
        tags = []

        for t in range(1, len(observations)):

            self.viterbi.append({})  # Adds a new path for each observation
            next_backpointer = {}

            for state in self.states:

                # Loops through each state and for each possible state it finds the state with the largest probability
                # using the previous path probabilities

                (probability, possible_state) = max(
                    [(self.viterbi[t - 1][prev_state] * self.transition_PD[prev_state].prob(state)
                      * self.emission_PD[state].prob(observations[t]), prev_state) for prev_state in self.states])

                # Updates the probability for the observation having the current state
                self.viterbi[t][state] = probability
                # Updates the path with the current state
                next_backpointer[state] = self.backpointer[possible_state] + [state]

            self.backpointer = next_backpointer


        # reconstruct the tag sequence using the backpointer
        # return the tag sequence corresponding to the best path as a list (order should match that of the words in the sentence)

        # Calculates the backtrace path by following backpointers to states back in time
        (_, state) = max([(self.viterbi[len(observations) - 1][state], state) for state in self.states])
        tags = self.backpointer[state]

        return tags


def answer_question4b():
    # Find a tagged sequence that is incorrect

    tagged_sequence = "Sentence: [u'most', u'library', u'budgets', u'are', u'hopelessly', u'inadequate', u'.'] " \
                      "\nand Tag: [u'ADJ', u'NOUN', u'X', u'X', u'X', u'X', u'.']"
    correct_sequence = "Tag: [u'ADJ', u'NOUN', u'NOUN', u'VERB', u'ADJ', u'ADJ', u'.']"
    # Why do you think the tagger tagged this example incorrectly?
    answer = "The tagger has filled certain tags with X\'s instead of actual tags. This might be due to having an " \
             "equal probability \nbetween which path to take for a certain observation. The tagger might then choose " \
             "the first path with that probability \nand avoid taking the correct one."
    return tagged_sequence, correct_sequence, answer


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    # http://stackoverflow.com/a/33024979
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def main():
    # devide corpus in train and test data
    tagged_sentences_Brown = brown.tagged_sents(categories='news')
    #COMPLETED initial location of the exit function

    test_size = 1000
    train_size = len(tagged_sentences_Brown) - 1000

    train_data_Brown = tagged_sentences_Brown[:train_size]
    test_data_Brown = tagged_sentences_Brown[-test_size:]

    tagged_sentences_Universal = brown.tagged_sents(categories='news', tagset='universal')
    train_data_Universal = tagged_sentences_Universal[:train_size]
    test_data_Universal = tagged_sentences_Universal[-test_size:]

    # create instance of HMM class and initialise the training and test sets
    obj = HMM(train_data_Universal, test_data_Universal)

    # train HMM
    obj.train()

    # part A: test emission model
    t1, t2 = obj.test_emission()
    print t1, t2
    if isclose(t1, 10.7862311423) and isclose(t2, 12.3247431105):  ### updated again
        print "PASSED test emission\n"
    else:
        print "FAILED test emission\n"

    # part A: test transition model
    start, end = obj.test_transition()
    print start, end
    if isclose(start, 1.78408815305) and isclose(end, 7.31426080296):
        print "PASSED test transition\n"
    else:
        print "FAILED test transition\n"
    # exit()  # move me down as you fill in implementations

    # part B: test accuracy on test set
    result = []
    correct = 0
    incorrect = 0
    accuracy = 0
    for sentence in test_data_Universal:
        s = [word.lower() for (word, tag) in sentence]
        # print(s)  # Added for question4_b testing
        obj.initialise(s[0])
        tags = obj.tag(s)
        # print(tags)  # Added for question4_b testing
        for i in range(0, len(sentence)):
            if sentence[i][1] == tags[i]:
                correct += 1
            else:
                incorrect += 1
    accuracy = 1.0 * correct / (correct + incorrect)
    print "accuracy: ", accuracy  # accuracy:  0.857186331623
    if isclose(accuracy, 0.857186331623):  ### updated
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

    exit()  # move me down as you fill in implementations


if __name__ == '__main__':
    main()
