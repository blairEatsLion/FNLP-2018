from nltk.model import NgramModel
from itertools import chain
from nltk.probability import (ConditionalProbDist, ConditionalFreqDist,
                              SimpleGoodTuringProbDist)
from math import log

def prob(self, word, context,verbose=False):
  """
  Evaluate the probability of this word in this context using Katz Backoff.

  :param word: the word to get the probability of
  :type word: str
  :param context: the context the word is in
  :type context: list(str)
  """

  context = tuple(context)
  if (context + (word,) in self._ngrams) or (self._n == 1):
      return self[context].prob(word)
  else:
    if verbose:
      print "backing off for %s"%(context+(word,),)
    return self._alpha(context) * self._backoff.prob(word, context[1:], verbose)


NgramModel.prob = prob

def logprob(self, word, context, verbose=False):
  """
  Evaluate the (negative) log probability of this word in this context.

  :param word: the word to get the probability of
  :type word: str
  :param context: the context the word is in
  :type context: list(str)
  """

  try:
    return -log(self.prob(word, context, verbose), 2)
  except ValueError:
    print self._n,context,word,self[context].prob(word)

NgramModel.logprob = logprob

def entropy(self, text, verbose=False):
  """
  Calculate the approximate cross-entropy of the n-gram model for a
  given evaluation text.
  This is the average log probability of each word in the text.

  :param text: words to use for evaluation
  :type text: list(str)
  """

  e = 0.0
  m = len(text)
  cl = self._n - 1
  for i in range(cl, m):
    context = tuple(text[i - cl : i ])
    token = text[i]
    e += self.logprob(token, context, verbose)
  return e/(float(m)-cl)

NgramModel.entropy = entropy
