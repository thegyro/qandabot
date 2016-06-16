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

# Create your views here.

def home(request):
	print request.method
	if request.method == 'POST':
		message_form = MessageForm(request.POST)
		if message_form.is_valid():
			print "here"
			question = message_form.cleaned_data['message']
			bot_response = 'random bot_response'
			print question
			return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response})
	else:
		message_form = MessageForm()
	return render(request, 'echoApp/messages_chat_widget.html',{'message_form':message_form})