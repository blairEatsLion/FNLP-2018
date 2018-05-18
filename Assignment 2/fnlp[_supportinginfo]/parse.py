from nltk.app import rdparser_app as rd
from nltk import parse_cfg
from pprint import pprint as pp
from nltk import grammar
import nltk
import re
from nltk.grammar import _ARROW_RE, _PROBABILITY_RE, _DISJUNCTION_RE, Production, WeightedProduction

# fix buggy NLTK 3 :-(
from nltk.draw import CFGEditor
from nltk.draw.util import SymbolWidget
ARROW = SymbolWidget.SYMBOLS['rightarrow']
CFGEditor._TOKEN_RE=re.compile("->|u?'[\\w ]+'|u?\"[\\w ]+\"|\\w+|("+ARROW+")")
CFGEditor._PRODUCTION_RE=re.compile(r"(^\s*\w+\s*)" +
                  r"(->|("+ARROW+"))\s*" +
                  r"((u?'[\w ]*'|u?\"[\w ]*\"|\w+|\|)\s*)*$")
nltk.grammar._TERMINAL_RE = re.compile(r'( u?"[^"]+" | u?\'[^\']+\' ) \s*', re.VERBOSE)
from nltk.grammar import _TERMINAL_RE

def parse_production(line, nonterm_parser, probabilistic=False):
    """
    Parse a grammar rule, given as a string, and return
    a list of productions.
    """
    pos = 0

    # Parse the left-hand side.
    lhs, pos = nonterm_parser(line, pos)

    # Skip over the arrow.
    m = _ARROW_RE.match(line, pos)
    if not m: raise ValueError('Expected an arrow')
    pos = m.end()

    # Parse the right hand side.
    probabilities = [0.0]
    rhsides = [[]]
    while pos < len(line):
        # Probability.
        m = _PROBABILITY_RE.match(line, pos)
        if probabilistic and m:
            pos = m.end()
            probabilities[-1] = float(m.group(1)[1:-1])
            if probabilities[-1] > 1.0:
                raise ValueError('Production probability %f, '
                                 'should not be greater than 1.0' %
                                 (probabilities[-1],))

        # String -- add terminal.
        elif (line[pos] in "\'\"" or line[pos:pos+2] in ('u"',"u'")):
            m = _TERMINAL_RE.match(line, pos)
            if not m: raise ValueError('Unterminated string')
            rhsides[-1].append(eval(m.group(1)))
            pos = m.end()

        # Vertical bar -- start new rhside.
        elif line[pos] == '|':
            m = _DISJUNCTION_RE.match(line, pos)
            probabilities.append(0.0)
            rhsides.append([])
            pos = m.end()

        # Anything else -- nonterminal.
        else:
            nonterm, pos = nonterm_parser(line, pos)
            rhsides[-1].append(nonterm)

    if probabilistic:
        return [WeightedProduction(lhs, rhs, prob=probability)
                for (rhs, probability) in zip(rhsides, probabilities)]
    else:
        return [Production(lhs, rhs) for rhs in rhsides]


g1=parse_cfg("""
    # Grammatical productions.
     S -> NP VP
     NP -> D N | Pro | PropN
     D -> PosPro | Art | NP s
     VP -> Vi | Vt NP | Vp NP VP
    # Lexical productions.
     Pro -> "i" | "we" | "you" | "he" | "she" | "him" | "her"
     PosPro -> "my" | "our" | "your" | "his" | "her"
     PropN -> "Robin" | "Jo"
     Art -> "a" | "an" | "the"
     N -> "cat" | "dog" | "duck" | "park" | "telescope" | "bench"
     Vi -> "sleep" | "run" | "duck"
     Vt -> "eat" | "break" | "see" | "saw"
     Vp -> "see" | "saw" | "heard"
     s -> "'s"
    """)

g2=parse_cfg("""
    # Grammatical productions.
     S -> NP VP
     NP -> D N | N | Pro | PropN
     D -> PosPro | Art
     VP -> Vi | Vt NP | Vp NP VP
    # Lexical productions.
     Pro -> "i" | "we" | "you" | "he" | "she" | "him" | "her"
     PosPro -> "my" | "our" | "your" | "his" | "her"
     PropN -> "Robin" | "Jo"
     Art -> "a" | "an" | "the"
     N -> "cat" | "dog" | "duck" | "park" | "telescope" | "bench"
     N -> "dogs" | "cats" | "ducks"
     Vi -> "sleep" | "run" | "duck"
     Vt -> "eat" | "break" | "see" | "saw"
     Vp -> "see" | "saw" | "heard"
     s -> "'s"
    """)

g3=parse_cfg("""
    # Grammatical productions
     S -> NPsg VPsg | NPpl VPpl
     NPpl -> Npl | Dpl Npl | ProPl | PropNPpl
     NPsg -> Dsg Nsg | ProSg | PropNPsg
     Dpl -> PosPro | Art
     Dsg -> PosPro | ArtSg | Art
     VPsg -> Visg | Vtsg NP | Vpsg NP VP
     VPpl -> Vipl | Vtpl NP | Vppl NP VP
     NP -> NPsg | NPpl
    # Lexical productions.
     ProSg -> "he" | "she" | "it" | "him" | "her" | "i" | "you"
     ProPl -> "they" | "them" | "we" | "you"
     PosPro -> "my" | "our" | "your" | "his" | "her" | "their"
     PropNsg -> "Robin" | "Jo" | "IBM"
     PropNpl -> "IBM"
     ArtSg -> "a" | "an"
     Art -> "the"
     Nsg -> "cat" | "sheep" | "dog" | "duck" | "park" | "telescope" | "bench"
     Npl -> "cats" | "dogs" | "men" | "sheep"
     Visg -> "sleeps" | "runs" | "ducks"
     Vipl -> "sleep" | "run" | "duck"
     Vtsg -> "eats" | "breaks" | "sees" | "saw"
     Vtpl -> "eat" | "break" | "see" | "saw"
     Vpsg -> "sees" | "saw" | "hears" | "heard"
     Vppl -> "see" | "saw" | "hear" | "heard"
""")

grammar.parse_production=parse_production

def app(grammar,sent="we sleep"):
    """
    Create a recursive descent parser demo, using a simple grammar and
    text.
    """    
    rd.RecursiveDescentApp(grammar, sent.split()).mainloop()




