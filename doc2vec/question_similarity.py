from gensim.models.doc2vec import Doc2Vec
from gensim import utils
from gensim.models.doc2vec import TaggedDocument

class QASimilarityDoc2Vec:
	def __init__(self, model_name=None, corpus=None, stop_words=False, filename=None, **kwargs):
		"""
		model_name: name of the model which has been trained and saved
		corpus: dictionary with 'question' and 'answer', where corpus['question'] is a list of TaggedDocuments
		filename: name of file containing the questions dataset
		"""
		if corpus:
			self.corpus = corpus
		else:
			self.corpus = {}
			self.corpus['question'] = list(self.read_corpus(filename['question'], stop_words=stop_words))
			self.corpus['answer'] = list(self.read_corpus(filename['answer'], stop_words=stop_words))

		if model_name:
			self.model = Doc2Vec.load(model_name)

		else:
			size = kwargs.get('size', 50)
			min_count  = kwargs.get('min_count', 5)
			alpha = kwargs.get('alpha', 0.025)
			min_alpha = kwargs.get('min_alpha', 0.025)
			iters = kwargs.get('iters', 10)

			self.train(size=size, min_count=min_count, alpha=alpha, min_alpha=min_alpha, iters=iters)

	def train(self, size, min_count, alpha, min_alpha, iters):
		self.model = Doc2Vec(size=size, min_count=min_count, alpha=alpha, min_alpha=min_alpha)
		self.model.build_vocab(self.corpus['question'])
		for epoch in range(iters):
			self.model.train(self.corpus['question'])
			self.model.alpha -= 0.002  # decrease the learning rate
			self.model.min_alpha = self.model.alpha  # fix the learning rate, no decay

	def read_corpus(self, fname, stop_words=False):
		with open(fname) as f:
			for i, line in enumerate(f):
				if stop_words:
					yield TaggedDocument(utils.simple_preprocess(line), [i])
				else:
					 # For training data, add tags
					 yield TaggedDocument(line.split(), [i])

	def save_model(self, fname):
		self.model.save(fname)

	def load_model(self, fname):
		self.model = Doc2Vec.load(fname)

	def get_most_similar_qa(self, query, topn=1):
		doc_vector = self.model.infer_vector(query.split())
		sims = self.model.docvecs.most_similar([doc_vector], topn=topn)
		sim_qanda = [(' '.join(self.corpus['question'][sims[index][0]].words), ' '.join(self.corpus['answer'][sims[index][0]].words)) for index in range(topn)]
		return sim_qanda

if __name__ == "__main__":
	qa = QASimilarityDoc2Vec(filename={'question':'intuit_questions.txt', 'answer':'intuit_answers.txt'})
	qa.save_model('Bhargav_cunt.doc2vec')
	sim_qa = qa.get_most_similar_qa("How to file my taxes", topn=2)

	for s in sim_qa:
		print 'Question: '
		print s[0]
		print
		print 'Answer: '
		print s[1]

