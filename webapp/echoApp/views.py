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