def norm(g):
  white=False
  while True:
    try:
      l=g.next()
    except StopIteration:
      if white:
        yield ' '
      raise StopIteration
    if l in '\n\r \t':
      white=True
      continue
    else:
      if white:
        yield ' '
        white=False
      yield l

def nextByBigram(bpd,l):
  while True:
    g=bpd.generate()
    if g[0]==l:
      return g[1]

def bfgen(bpd,n):
  f=bpd.generate()
  r=[f[0],f[1]]
  s=r[1]
  for i in range(0,n-3):
    s=nextByBigram(bpd,s)
    r.append(s)
  return ''.join(r)
