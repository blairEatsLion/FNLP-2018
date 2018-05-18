#!/c/Python26/python
# Based on Zhang, Vogel and Waibel 20??, "Integrated Phrase Segmentation and Alignment Algorithm
#   for Statistical Machine Translation"
import sys

class ISA:
  def __init__(self,ep,fp,bp,als=None):
    self.ep=ep
    self.fp=fp
    self.bp=bp
    if als is not None:
      self.load(als)

  def load(self,als):
    self.als=als
    self.max=-1000.0
    self.blocks=[]
    self.status={}
    self.e=[w.lower() for w in als.words if w[0].isalpha()]
    self.Ne=len(self.e)
    self.f=[w.lower() for w in als.mots if w[0].isalpha()]
    self.Nf=len(self.f)
    self.m=[0]*self.Ne
    # so m is an array of columns, and m[x][y] should be
    # pmi(e[x],f[y])
    for x in range(self.Ne):
      self.m[x]=[0]*self.Nf
      for y in range(self.Nf):
        pmi=self.pmi(self.e[x],self.f[y])
	self.m[x][y]=pmi
        if pmi>self.max:
          self.max=pmi
          self.maxX=x
          self.maxY=y

  def show(self,pmi=True,fromE=0,toE=-1,fromF=0,toF=-1,
           verbose=False):
    if toE==-1:
      toE=len(self.e)
    if toF==-1:
      toF=len(self.f)
    fwl=max(len(self.f[i]) for i in range(fromF,toF))
    fwFormat="%%%ss"%fwl
    if pmi:
      valFormat=[("%%%s.2f"%max(5,len(self.e[i]))) for i in range(fromE,toE)]
      ewFormat=[("%%%ss"%max(5,len(self.e[i]))) for i in range(fromE,toE)]
      cellFn=lambda x,y,s=self:s.m[x][y]
    else:
      valFormat=[("%%%ss"%max(2,len(self.e[i]))) for i in range(fromE,toE)]
      ewFormat=[("%%%ss"%max(2,len(self.e[i]))) for i in range(fromE,toE)]
      cellFn=lambda x,y,s=self:s.status.get((x,y)," ")
    print "(%s,%s)"%(self.maxX,self.maxY)
    for y in range(self.Nf-1,-1,-1):
      if y in range(fromF,toF):
        print ' '.join([fwFormat%self.f[y],"%2s"%y]+
                        [valFormat[x-fromE]%cellFn(x,y) for x in range(fromE,toE)])
    print ' '.join([" "*(fwl+3)]+[ewFormat[x-fromE]%x for x in range(fromE,toE)])
    ll=' '.join([" "*(fwl+3)]+[ewFormat[x-fromE]%self.e[x] for x in range(fromE,toE)])
    print ll
    if verbose:
      return len(ll)

  def pmi(self,e,f):
    return self.bp.logprob((e,f))-(self.ep.logprob(e)+self.fp.logprob(f))
   
  def nextBlock(self):
    if self.blocks!=[]:
      # Need a new max
      self.max=-1000
      for x in range(self.Ne):
        for y in range(self.Nf):
          p=(x,y)
          if not (x,y) in self.status:
            pmi=self.m[x][y]
            if pmi>self.max:
              self.max=pmi
              self.maxX=x
              self.maxY=y
    if self.max==-1000:
      return
    p=(self.maxX,self.maxY)
    blocks=self.growBlock(p,p,self.max)
    if blocks:
      # should check for ties. . .
      return blocks[0]

  def growBlock(self,ll,ur,seedPMI):
    global newCandidates
    # Grow a block all possible directions
    # Brute force for now -- just enumerate all possible rectangles, keeping
    #  keeping track of everything we find
    candidates=[(ll,ur)]
    res=[]
    while candidates:
      res=res+candidates # should do area-sorted insertion. . .
      newCandidates=[]
      for (ll,ur) in candidates:
        for (dx,dy) in ((1,0),(0,-1),(-1,0),(0,1)):
          bigger=self.growBlock1(ll,ur,seedPMI,dx,dy)
          if bigger is not None:
            newCandidates.append(bigger)
      candidates=newCandidates
    sortedRes=sorted(res,key=self.blockSize,reverse=True)
    if self.debug>0:
      for r in sortedRes:
        print "%5.2f %5s %s"%(self.blockSize(r), self.req2OK(r), r)
    return [b for b in sortedRes if self.req2OK(b)]

  def growBlock1(self,ll,ur,seedPMI,dx,dy):
    # grow a block with lower-left at ll and upper-right at ur of width w and height h
    # by dx,dy clockwise (from (1,0),(0,-1),(-1,0),(0,1),
    #                     bearing in mind that m[x] is a column going _up_)
    # respecting the requirements that:
    #  0) the cell is a) still in the matrix and b) alive
    #  1) ratio of each added cell's PMI to seedPMI >= self.thresh
    #  2) no free cell in added cell's row or column has > PMI
    #         > than _what_ PMI?  See req2OK below
    if self.debug>1:
      print "growing %s, %s by %s, %s"%(ll,ur,dx,dy)
    # First requirement 0a:
    if dx is not 0:
      if dx is -1:
        if ll[0] is 0:
          return
        else:
          # extending left
          ll=(ll[0]-1,ll[1])
          x=ll[0]
      elif ur[0] is (self.Ne-1):
        return
      else:
        ur=(ur[0]+1,ur[1])
        x=ur[0]
      for y in range(ll[1],ur[1]+1):
        # req. 0b
        if (x,y) in self.status:
          return
        # req. 1
        if self.m[x][y]/seedPMI<self.thresh:
          return
    elif dy is -1:
      if ll[1] is 0:
        return
      else:
        ll=(ll[0],ll[1]-1)
        y=ll[1]
    elif ur[1] is (self.Nf-1):
      return
    else:
      ur=(ur[0],ur[1]+1)
      y=ur[1]
    for x in range(ll[0],ur[0]+1):
      # req. 0b
      if (x,y) in self.status:
        return
      # req. 1
      if self.m[x][y]/seedPMI<self.thresh:
        return
    if self.debug>1:
      print "got one: %s, %s"%(ll,ur)
    res=(ll,ur)
    # how could we check this sooner w/o obscurity?
    if res in newCandidates:
      if self.debug>1:
        print " duplicate|"
      return
    if self.debug>2:
      sys.stdin.readline()
    return res

  def req2OK(self,block):
    (ll,ur)=block
    # Guessing what the right thing to do is
    # All the paper says is "Do not expand the region if it will
    #                        block the free cells with higher MI value"
    # a) The row and column containing the seed can't be included, since
    #     they will _all_ be blocked by the seed no matter what
    # b) None-the-less I think we want to check against the _highest_ cell
    #     in each row/column, which may lead to non-monotonic results, i.e.
    #           [4 2 3] .... 2.5 is OK, even though [4 2] . . . 2.5 is not
    #
    # First, columns
    for x in range(ll[0],ur[0]+1):
      if x is self.maxX:
        # skip this
        continue
      cMax=-1000
      for y in range(ll[1],ur[1]+1):
        cMax=max(cMax,self.m[x][y])
      if cMax>-1000:                    # I.e. we're not just the seed
        # below
        for y in range(ll[1]):
          if (x,y) not in self.status and self.m[x][y]-cMax>self.delta:
            if self.debug>0:
              print "losing column-wise wrt %s: %s %s %s %s"%(block,x,y,self.m[x][y],cMax)
            return False
        # above
        for y in range(ur[1]+1,self.Nf):
          if (x,y) not in self.status and self.m[x][y]-cMax>self.delta:
            if self.debug>0:
              print "losing column-wise wrt %s: %s %s %s %s"%(block,x,y,self.m[x][y],cMax)
            return False
    # Then, rows
    for y in range(ll[1],ur[1]+1):
      if y is self.maxY:
        # skip this
        continue
      rMax=-1000
      for x in range(ll[0],ur[0]+1):
        rMax=max(rMax,self.m[x][y])
      if rMax>-1000:                    # I.e. we're not just the seed
        # below
        for x in range(ll[0]):
          if (x,y) not in self.status and self.m[x][y]-rMax>self.delta:
            if self.debug>0:
              print "losing row-wise wrt %s: %s %s %s %s"%(block,x,y,self.m[x][y],rMax)
            return False
        # above
        for x in range(ur[0]+1,self.Ne):
          if (x,y) not in self.status and self.m[x][y]-rMax>self.delta:
            if self.debug>0:
              print "losing row-wise wrt %s: %s %s %s %s"%(block,x,y,self.m[x][y],rMax)
            return False
    return True

  def tile(self,thresh=0.0,delta=0.1,penalty=10.0,debug=False):
    self.thresh=thresh
    self.delta=delta
    self.penalty=penalty
    self.debug=debug
    if self.blocks!=[]:
      # reset
      self.max=-1000.0
      self.blocks=[]
      self.status={}
      for x in range(self.Ne):
        for y in range(self.Nf):
          pmi=self.m[x][y]
          if pmi>self.max:
            self.max=pmi
            self.maxX=x
            self.maxY=y

    nextBlock=self.nextBlock()
    bc=0
    while nextBlock:
      self.blocks.append(nextBlock)
      # mark the block and the cells it kills
      # first columns
      (ll,ur)=nextBlock
      for x in range(ll[0],ur[0]+1):
        for y in range(self.Nf):
          if y<ll[1] or y>ur[1]:
            self.status[(x,y)]='d'
          else:
            self.status[(x,y)]=bc
      # then rows (only need to mark dead)
      for y in range(ll[1],ur[1]+1):
        for x in range(self.Ne):
          if x<ll[0] or x>ur[0]:
            self.status[(x,y)]='d'
      ll=self.show(pmi=False,verbose=True)
      print nextBlock
      bc=bc+1
      nextBlock=self.nextBlock()
      if nextBlock is not None:
        print "-"*ll

  def blockSize(self,(ll,ur)):
    ww=(ur[0]-ll[0])+1
    hh=(ur[1]-ll[1])+1
    size=ww*hh
    # ad-hoc penalty for rectangularity
    if self.penalty>0:
      return size*(self.penalty/(self.penalty+(abs(ww-hh))))
    else:
      return size
  
