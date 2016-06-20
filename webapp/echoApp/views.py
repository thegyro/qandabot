from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext,loader
from django.contrib.auth import authenticate, login ,logout
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django import forms
from django.contrib.auth.decorators import login_required
from echoApp.forms import MessageForm
from chatterbot import ChatBot
from chatterbot.training.trainers import ChatterBotCorpusTrainer, ListTrainer
from gensim.models import ldamodel
from gensim.corpora import Dictionary
from gensim import models, similarities, corpora
from similarity import jaccard, kullback_leibler, hellinger

import os
import pickle
import gensim
import question_similarity
import sol
import rnn_generator as rg



text_blah = """Intuit is a great place to be.
Isn't it? Ever since I've been breathed into life I'm glad to be working for Inuit.
How are you?
I am doing fine. The thought of being able to help you makes me happy!
I need help.
We all need help sometimes... How exactly may I help you?
You are being strange.
I am sorry! I've only been trained one night, you see.
You are not helpful and are bad.
I am sorry! I've only been trained one night, you see.
You are stupid and useless.
I am sorry! I've only been trained one night, you see.
It's a nice day outside.
Any day I can help you is a nice day for me!
What is your name?
My name is echo.
When were you born?
I was born just last night. I'm smart for a one day old, right?
How old are you?
I was born just last night. I'm smart for a one day old, right?
How do you do?
I am doing fine. The thought of being able to help you makes me happy!
What do you think of Donald Trump?
I was not trained to have political leaning. 
Do you have a wife?
No one has trained a girl for me. Hopefully my creators will, soon!
Do you have a girlfriend?
No one has trained a girl for me. Hopefully my creators will, soon!
Do you have a girl?
No one has trained a girl for me. Hopefully my creators will, soon!
How many languages do you speak?
I speak English, a little French and a lot of binary.
You are bad.
I am sorry! I've only been trained one night, you see.
You are helpful!
Thank you, it's my pleasure."""


# Create your views here.
question_list = []
chatbot = ChatBot("Echo")
chatbot.set_trainer(ChatterBotCorpusTrainer)
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")

chatbot.set_trainer(ListTrainer)
data_list = text_blah.split('\n')
chatbot.train(data_list)

current_dir = os.getcwd() + '/echoApp'  #From the location of 'manage.py'
print current_dir

qa = question_similarity.QASimilarityDoc2Vec(model_name=current_dir + '/intuit_temp.doc2vec',filename={'question':current_dir +'/intuit_questions.txt', 'answer':current_dir +'/intuit_answers.txt'})
q_lda = ldamodel.LdaModel.load(current_dir +'/q_LDA_stop_20')
dictionary = Dictionary.load(current_dir +'/q_dictionary')
corpus = corpora.MmCorpus(current_dir + '/corpus')
question_file = open(current_dir +'/questions')
answer_file = open(current_dir +'/answers') 
rnn = rg.RNNGenerator(current_dir + '/intuit_weights.h5', open(current_dir +'/intuit_data.txt').read())                


q = pickle.load(question_file)
a = pickle.load(answer_file)

def home(request):
    global chatbot
    global question_list
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            question = message_form.cleaned_data['message']
            question_list.append(question)
            bot_response = chatbot.get_response(question)
            
            temp_question = question.lower()
            tax_words = ['tax', 'form', 'problem', 'issue', 'turbo', 'file', 'return']
            if [w for w in tax_words if w in temp_question]:
                modal = True
                bot_response = 'It seems you have a problem with Turbo Tax or filing your taxes. I have had a look at some previous questions, see if they might help!'
                question_list.append(bot_response)
                question_dict = similarity(temp_question)
                sim_qa = qa.get_most_similar_qa(temp_question, topn=2)
                sim_dict = {}
                for s in sim_qa:
                    sim_dict[s[0]] = s[1]
                #call link list
                linkList  = sol.get_links(temp_question)
                rnn_list = []
                # for i in range(5):
                rnn_result = rnn.generate()
                rnn_result = rnn_result.decode('utf-8')
                rnn_list.append(rnn_result)
                return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list, 'modal':modal, 'question_dict':question_dict, 'sim_dict':sim_dict, 'linkList':linkList, 'temp_question':temp_question, 'rnn_list':rnn_list})
            else:
                question_list.append(bot_response)
                return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list})
    else:
        message_form = MessageForm()
        question_list = []
        question_list.append('Hello! My name is Echo. Please type in what would you like to ask.')
    return render(request, 'echoApp/messages_chat_widget.html',{'message_form':message_form, 'question_list':question_list})


# def superbot(request,temp_question):
#     list_question = question_list
#     is_superbot = True
#     rnn_result = rnn.generate()

#     return HttpResponse("d")

def similarity(query):

    # GDRAT_abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media/documents/GDRAT.xls')
    # loading starts
    # q = pickle.load(question_file)
    # a = pickle.load(answer_file)
    global q, a

    q_lsi = models.LsiModel.load(current_dir +'/q_LSI_stop_20')
    index = similarities.MatrixSimilarity.load(current_dir +'/lsi_index')
    lsi_tf = models.LsiModel.load(current_dir +'/lsi_tf')
    index_tf = similarities.MatrixSimilarity.load(current_dir +'/lsi_tf_index')

    # loading ends
    query = dictionary.doc2bow(query.lower().split())

    question_dict = {}

    # this if for LSI TF IDF
    i = 0
    vec_query = lsi_tf[query]
    sims = index_tf[vec_query]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])   
    while len(question_dict) is not 2:
        if ' '.join(a[sims[i][0]]) is not ' ' and ' '.join(a[sims[i][0]]) is not '' and ' '.join(a[sims[i][0]]) is not None:
            question_dict[' '.join(q[sims[i][0]])] = ' '.join(a[sims[i][0]])
        i += 1

    # this is for normal LSI
    i = 0
    vec_query = q_lsi[query]
    sims = index[vec_query]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])   
    while len(question_dict) is not 4:
        if ' '.join(q[sims[i][0]]) in question_dict:
            i += 1
            continue

        if ' '.join(a[sims[i][0]]) is not ' ' and ' '.join(a[sims[i][0]]) is not '' and ' '.join(a[sims[i][0]]) is not None :
            question_dict[' '.join(q[sims[i][0]])] = ' '.join(a[sims[i][0]])
        i += 1


    vec_query = q_lda[query]
    max_sim = 10
    i = 0

    for doc in corpus:
        sim = hellinger(vec_query, q_lda[doc])
        if sim < max_sim:
            max_sim = sim
            max_doc = doc 
            doc_num = i
        i += 1

    if ' '.join(q[doc_num]) is not question_dict and a[doc_num] is not ' ' and a[doc_num] is not '' and a[doc_num] is not None:
        question_dict[' '.join(q[doc_num])] = ' '.join(a[doc_num])

    return question_dict


def read_corpus(fname, tokens_only=False):
    with open(fname) as f:
        for i, line in enumerate(f):
            if tokens_only:
                yield gensim.utils.simple_preprocess(line)
            else:
                # For training data, add tags
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])


def doc_2_vec(text):
    corpus = list(read_corpus(current_dir + "/intuit_questions.txt"))

    model =  gensim.models.doc2vec.Doc2Vec.load(current_dir +"/Intuit_Model.doc2vec")
    inferred_vector = model.infer_vector(text.split())
    sims = model.docvecs.most_similar([inferred_vector], topn=2)#len(model.docvecs))
    #print sims

    # model.save("Intuit_Model.doc2vec");
    sim_ques = []
    for label, index in [('MOST', 0), ('MOST',1)]:#('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
        #print(u'%s %s: %s\n' % (label, sims[index], ' '.join(corpus[sims[index][0]].words)))
        sim_ques.append(' '.join(corpus[sims[index][0]].words))
        #print(u'%s' % (' '.join(corpus[sims[index][0]].words)))
    return sim_ques

