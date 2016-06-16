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
from chatterbot.training.trainers import ChatterBotCorpusTrainer
from gensim.models import ldamodel
from gensim.corpora import Dictionary
from gensim import models, similarities, corpora
from similarity import jaccard, kullback_leibler, hellinger
import pickle



# Create your views here.
question_list = []
chatbot = ChatBot("Echo")
chatbot.set_trainer(ChatterBotCorpusTrainer)
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")



def home(request):
	global chatbot
	global question_list
	if request.method == 'POST':
		message_form = MessageForm(request.POST)
		if message_form.is_valid():
			question = message_form.cleaned_data['message']
			if 'tax' in question or 'form' in question:
				similarity()

			question_list.append(question)
			bot_response = chatbot.get_response(question)
			question_list.append(bot_response)
			modal = True
			if modal:
				return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list, 'modal':modal})
			else:
				return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list})
	else:
		message_form = MessageForm()
		question_list = []
		question_list.append('Hello! My name is Echo. Please type in what would you like to ask.')
	return render(request, 'echoApp/messages_chat_widget.html',{'message_form':message_form, 'question_list':question_list})

def similarity(query):

	# loading starts
	q_lda = ldamodel.LdaModel.load('q_LDA_stop_20')
	dictionary = Dictionary.load('q_dictionary')
	corpus = corpora.MmCorpus('corpus')
	question_file = open("questions")
	answer_file = open("answers") 
	q = pickle.load(question_file)
	a = pickle.load(answer_file)
	q_lsi = models.LsiModel.load('q_LSI_stop_20')
	index = similarities.MatrixSimilarity.load('lsi_index')
	lsi_tf = models.LsiModel.load('lsi_tf')
	index_tf = similarities.MatrixSimilarity.load('lsi_tf_index')

	# loading ends
	query = dictionary.doc2bow(query.lower().split())
	# vec_query = q_lda[query]

	# max_sim = 10
	# i = 0
	# for doc in corpus:
	# 	sim = hellinger(vec_query, q_lda[doc])
	# 	if sim < max_sim:
	# 		max_sim = sim
	# 		max_doc = doc 
	# 		doc_num = i
	# 	i += 1

	# print(q[doc_num])
	# print "\n"


	vec_query = lsi_tf[query]
	sims = index[vec_query]
	sims = sorted(enumerate(sims), key=lambda item: -item[1])

	print(q[sims[0][0]], q[sims[1][0]])
	print "\n"

	vec_query = q_lsi[query]
	sims = index[vec_query]
	sims = sorted(enumerate(sims), key=lambda item: -item[1])

	print(q[sims[0][0]], q[sims[1][0]])
