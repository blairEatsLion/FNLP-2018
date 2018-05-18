from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.corpus.reader import RegexpTokenizer
from nltk.tokenize import LineTokenizer
from nltk.corpus.reader.util import read_line_block

from nltk import FreqDist

twc=PlaintextCorpusReader("/group/ltg/projects/fnlp/",
                          r'2.*\.txt',
                          word_tokenizer=RegexpTokenizer(r'[\w#@]+|[^\w\s]+'),
                          sent_tokenizer=LineTokenizer(),
                          para_block_reader=read_line_block)

try:
	from nltk import compat
except:
	pass

from nltk.probability import _get_kwarg,islice

def plotSorted(self, *args, **kwargs):
        """
        Plot samples from the frequency distribution,
        sorted using a supplied key function.  If an integer
        parameter is supplied, stop after this many samples have been
        plotted.  If two integer parameters m, n are supplied, plot a
        subset of the samples, beginning with m and stopping at n-1.
        For a cumulative plot, specify cumulative=True.
        (Requires Matplotlib to be installed.)

        :param title: The title for the graph
        :type title: str
        :param key: a function to pass to sort to extract the sort key
          given an FD and a sample id.
          Defaults to the value of that sample's entry,
          lambda fd,s:fd[s]
        :type key: function
        :param reverse: True to sort high to low
        :type reverse: bool
        """
        try:
            import pylab
        except ImportError:
            raise ValueError('The plot function requires the matplotlib package (aka pylab). '
                         'See http://matplotlib.sourceforge.net/')

        if len(args) == 0:
            args = [len(self)]

        keyFn = _get_kwarg(kwargs, 'key', lambda fd,s:fd[s])
        reverse = _get_kwarg(kwargs, 'reverse', False)

        samples = list(islice(self, *args))
        samples.sort(key=lambda x:keyFn(self,x),reverse=reverse)

        freqs = [self[sample] for sample in samples]
        ylabel = "Counts"
        # percents = [f * 100 for f in freqs]  only in ProbDist?

        pylab.grid(True, color="silver")
        if not "linewidth" in kwargs:
            kwargs["linewidth"] = 2
        if "title" in kwargs:
            pylab.title(kwargs["title"])
            del kwargs["title"]
        pylab.plot(freqs, **kwargs)
        pylab.xticks(range(len(samples)), [compat.text_type(s) for s in samples], rotation=90)
        pylab.xlabel("Samples")
        pylab.ylabel(ylabel)
        pylab.show()

FreqDist.plotSorted=plotSorted
