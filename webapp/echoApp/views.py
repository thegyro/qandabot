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
import gensim
import question_similarity
import sol



# Create your views here.
question_list = []
chatbot = ChatBot("Echo")
chatbot.set_trainer(ChatterBotCorpusTrainer)
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")
qa = question_similarity.QASimilarityDoc2Vec(model_name='/Users/prane1/Hackathon/qandabot/webapp/echoApp/intuit_temp.doc2vec',filename={'question':'/Users/prane1/Hackathon/qandabot/webapp/echoApp/intuit_questions.txt', 'answer':'/Users/prane1/Hackathon/qandabot/webapp/echoApp/intuit_answers.txt'})
                


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
                return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list, 'modal':modal, 'question_dict':question_dict, 'sim_dict':sim_dict, 'linkList':linkList})
            else:
                question_list.append(bot_response)
                return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list})
    else:
        message_form = MessageForm()
        question_list = []
        question_list.append('Hello! My name is Echo. Please type in what would you like to ask.')
    return render(request, 'echoApp/messages_chat_widget.html',{'message_form':message_form, 'question_list':question_list})

def superbot(request):
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
                return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list, 'modal':modal, 'question_dict':question_dict})
            else:
                question_list.append(bot_response)
                return render(request, 'echoApp/messages_chat_widget.html', {'message_form':message_form, 'question':question, 'bot_response':bot_response, 'question_list':question_list})
    else:
        message_form = MessageForm()
        question_list = []
        question_list.append('Hello! I am superbot.')
    return render(request, 'echoApp/messages_chat_widget.html',{'message_form':message_form, 'question_list':question_list})

def similarity(query):

    # GDRAT_abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media/documents/GDRAT.xls')
    # loading starts
    q_lda = ldamodel.LdaModel.load('/Users/prane1/Hackathon/qandabot/webapp/echoApp/q_LDA_stop_20')
    dictionary = Dictionary.load('/Users/prane1/Hackathon/qandabot/webapp/echoApp/q_dictionary')
    corpus = corpora.MmCorpus('/Users/prane1/Hackathon/qandabot/webapp/echoApp/corpus')
    question_file = open("/Users/prane1/Hackathon/qandabot/webapp/echoApp/questions")
    answer_file = open("/Users/prane1/Hackathon/qandabot/webapp/echoApp/answers") 
    q = pickle.load(question_file)
    a = pickle.load(answer_file)
    q_lsi = models.LsiModel.load('/Users/prane1/Hackathon/qandabot/webapp/echoApp/q_LSI_stop_20')
    index = similarities.MatrixSimilarity.load('/Users/prane1/Hackathon/qandabot/webapp/echoApp/lsi_index')
    lsi_tf = models.LsiModel.load('/Users/prane1/Hackathon/qandabot/webapp/echoApp/lsi_tf')
    index_tf = similarities.MatrixSimilarity.load('/Users/prane1/Hackathon/qandabot/webapp/echoApp/lsi_tf_index')

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
    corpus = list(read_corpus("/Users/prane1/Hackathon/qandabot/webapp/echoApp/intuit_questions.txt"))

    model =  gensim.models.doc2vec.Doc2Vec.load("/Users/prane1/Hackathon/qandabot/webapp/echoApp/Intuit_Model.doc2vec")
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

