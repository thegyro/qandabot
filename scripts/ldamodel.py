"""

This is a file which creates the 'domains' after the questions and answers have been pre-processed.
It also has top answers in a domain.

"""

from gensim.models import ldamodel
from gensim.corpora import Dictionary


q_corpus = []
a_corpus = []
for line in open("csvfile.txt"):
	q_corpus.append(line.split[1].split())
	a_corpus.append(line.split[2].split())

q_dictionary = Dictionary(q_corpus)
q_corpus = [q_dictionary.doc2bow(text) for text in q_corpus]

a_dictionary = Dictionary(a_corpus)
a_corpus = [a_dictionary.doc2bow(text) for text in a_corpus]


q_model = ldamodel.LdaModel(corpus, num_topics=5)
a_model = ldamodel.LdaModel(corpus, num_topics=5)


# random comment