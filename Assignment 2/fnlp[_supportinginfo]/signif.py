from nltk import FreqDist
from random import randint
import pylab
from math import sqrt

def mean(self):
  # Assumes the keys of this distribution are numbers!
  return float(sum(v*self[v] for v in self.keys()))/self.N()

FreqDist.mean=mean

def bell(self):
  # Assumes the keys of this distribution are numbers!
  sk = sorted(self.keys()) # range(max(self.keys())+1)
  #sk.append(sk[-1]+1)
  #sk[0:0]=[(sk[0]-1)]
  mm=0 # sk[0]
  mean = self.mean()
  tot = 0
  ssd = 0
  for v in self.keys():
    d = v-mean
    ssd+=d*d*self[v]
  sd=sqrt(ssd/float(self.N()))
  #print (mean,sd)
  kv=[self[k] for k in sk]
  pylab.figure().subplots_adjust(bottom=0.15)
  pylab.plot(sk,kv,color='blue')
  pylab.bar([s-mm for s in sk],kv,
            align='center',color='white',edgecolor='pink')
  pylab.xticks(sk,rotation=90)
  mv=self[self.max()]
  bb=(-mv/10,mv+(mv/10))
  pylab.plot((mean-mm,mean-mm),bb,
             (mean-mm-sd,mean-mm-sd),bb,
             (mean-mm-(2*sd),mean-mm-(2*sd)),bb,
             (mean-mm+sd,mean-mm+sd),bb,
             (mean-mm+(2*sd),mean-mm+(2*sd)),bb,
              color='green')
  pylab.xlabel("N %s, max %s\nmean %5.2f, s.d. %5.2f"%(self.N(),mv,mean, sd))
  pylab.show()

FreqDist.bell=bell

def ranks(l,**kvargs):
  # compute the rank of every element in a list
  # uses sort, passing on all kv args
  # uses key kv arg itself
  # _Very_ inefficient, in several ways!
  # Result is a pair:
  #  list of ranks
  #  list of tie information, each elt the magnitude of a tie group
  s=sorted(l,**kvargs)
  i=0
  res=[]
  td=[]
  if kvargs.has_key('key'):
    kf=kvargs['key']
  else:
    kf=lambda x:x
  while i<len(l):
    ties=[x for x in s if kf(s[i])==kf(x)]
    if len(ties)>1:
      td.append(len(ties))
    r=float(i+1+(i+len(ties)))/2.0
    for e in ties:
      res.append((r,e))
      i+=1
  return (res,td)

def mannWhitneyU(fd1,fd2,forceZ=False):
  # Compute Mann Whitney U test for two frequency distributions
  # For n1 and n2 <= 20, see http://www.soc.univ.keiv.ua/LIB/PUB/T/textual.pdf
  #  to look up significance levels on the result: see Part 3 section 10,
  #  actual page 150 (printed page 144)
  # Or use http://faculty.vassar.edu/lowry/utest.html to do it for you
  # For n1 and n2 > 20, U itself is normally distributed, we
  #  return a tuple with a z-test value
  # HST DOES NOT BELIEVE THIS IS CORRECT -- DOES NOT APPEAR TO GIVE CORRECT ANSWERS!!
  r1=[(lambda x:x.append(1) or x)(list(x)) for x in fd1.items()]
  r2=[(lambda x:x.append(2) or x)(list(x)) for x in fd2.items()]
  n1=len(r1)
  n2=len(r2)
  (ar,ties)=ranks(r1+r2,key=lambda e:e[1])
  s1=sum(r[0] for r in ar if r[1][2] is 1)
  s2=sum(r[0] for r in ar if r[1][2] is 2)
  u1=float(n1*n2)+(float(n1*(n1+1))/2.0)-float(s1)
  u2=float(n1*n2)+(float(n2*(n2+1))/2.0)-float(s2)
  u=min(u1,u2)
  if forceZ or n1>20 or n2>20:
    # we can treat U as sample from a normal distribution, and compute
    # a z-score
    # See e.g. http://mlsc.lboro.ac.uk/resources/statistics/Mannwhitney.pdf
    mu=float(n1*n2)/2.0
    if len(ties)>0:
      n=float(n1+n2)
      ts=sum((float((t*t*t)-t)/12.0) for t in ties)
      su=sqrt((float(n1*n2)/(n*n-1))*((float((n*n*n)-n)/12.0)-ts))
    else:
      su=sqrt(float(n1*n2*(n1+n2+1))/12.0)
    z=(u-mu)/su
    return (n1,n2,u,z)
  else:
    return (n1,n2,u)

# This started from http://dr-adorio-adventures.blogspot.com/2010/05/draft-untested.html
#  but has a number of bug fixes
def Rank(l,**kvargs):
  # compute the rank of every element in a list
  # uses sort, passing on all kv args
  # uses key kv arg itself
  # _Very_ inefficient, in several ways!
  # Result is a list of pairs ( r, v) where r is a rank and v is an input value
  s=sorted(l,**kvargs)
  i=0
  res=[]
  if kvargs.has_key('key'):
    kf=kvargs['key']
  else:
    kf=lambda x:x
  while i<len(l):
    ties=[x for x in s if kf(s[i])==kf(x)]
    r=float(i+1+(i+len(ties)))/2.0
    #print (i,r,ties)
    for e in ties:
      res.append((r,e))
      i+=1
  return (res)

def mannWhitney(S1, S2):
    """
    Returns the Mann-Whitney U statistic of two samples S1 and S2.
    """
    # Form a single array with a categorical variable indicate the sample
    X = [(s, 0) for s in S1]
    X.extend([(s,1) for s in S2])
    R = Rank(X,key=lambda x:x[0])
 
    # Compute needed parameters.
    n1 = float(len(S1))
    n2 = float(len(S2))
 
    # Compute total ranks for sample 1.          
    R1 = sum([i for i, (x,j) in R if j == 0])
    R2 = sum([i for i, (x,j) in R if j == 1])
    u1 = (n1*n2)+((n1*(n1+1))/2.0)-R1
    u2 = n1 * n2 - u1
    U = min(u1, u2)
    #print u1,R1/n1,R2/n2
 
    mU     = n1 * n2 / 2.0
    sigmaU = sqrt((n1 * n2 * (n1 + n2 + 1))/12.0)
    return u1, R1/n1,R2/n2, (U-mU)/sigmaU

