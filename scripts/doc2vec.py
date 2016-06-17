import gensim

def read_corpus(fname, tokens_only=False):
    with open(fname) as f:
        for i, line in enumerate(f):
            if tokens_only:
                yield gensim.utils.simple_preprocess(line)
            else:
                # For training data, add tags
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

 
corpus = list(read_corpus("intuit_questions.txt"))
# model = gensim.models.doc2vec.Doc2Vec(size=50, min_count=2, alpha=0.025, min_alpha=0.025)
model =  gensim.models.doc2vec.Doc2Vec.load("Intuit_Model.doc2vec")
# model.build_vocab(corpus)
# #model.sort_vocab()

# for epoch in range(10):
#     model.train(corpus)
#     model.alpha -= 0.002  # decrease the learning rate
#     model.min_alpha = model.alpha  # fix the learning rate, no decay

inferred_vector = model.infer_vector("I have problem filing taxes".split())
sims = model.docvecs.most_similar([inferred_vector], topn=2)#len(model.docvecs))
#print sims

# model.save("Intuit_Model.doc2vec");

for label, index in [('MOST', 0), ('MOST',1)]:#('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
    #print(u'%s %s: %s\n' % (label, sims[index], ' '.join(corpus[sims[index][0]].words)))
    print(u'%s' % (' '.join(corpus[sims[index][0]].words)))
