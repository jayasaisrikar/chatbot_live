from django.shortcuts import render, redirect
from django import forms
from .utils import fetch_and_process_article, create_vector_store, build_query_agent

class ChatSessionForm(forms.Form):
    product_name = forms.CharField(max_length=100)
    num_articles = forms.IntegerField(min_value=1)

class ArticleForm(forms.Form):
    url = forms.URLField()

class ChatMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)

def home(request):
    if request.method == 'POST':
        form = ChatSessionForm(request.POST)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            num_articles = form.cleaned_data['num_articles']
            request.session['product_name'] = product_name
            request.session['num_articles'] = num_articles
            request.session['articles'] = []
            return redirect('add_articles', num_articles=num_articles)
    else:
        form = ChatSessionForm()
    return render(request, 'home.html', {'form': form})

def add_articles(request, num_articles):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            content = fetch_and_process_article(url)
            articles = request.session.get('articles', [])
            articles.append({'url': url, 'content': content})
            request.session['articles'] = articles
            num_articles -= 1
            if num_articles > 0:
                return redirect('add_articles', num_articles=num_articles)
            else:
                return redirect('chatbot')
    else:
        form = ArticleForm()
    return render(request, 'add_articles.html', {'form': form, 'num_articles': num_articles})

def chatbot(request):
    articles = request.session.get('articles', [])
    vector_store = create_vector_store([article['content'] for article in articles])
    query_agent = build_query_agent(vector_store)

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            bot_response = query_agent(user_message)
            chat_messages = request.session.get('chat_messages', [])
            chat_messages.append({'user_message': user_message, 'bot_response': bot_response})
            request.session['chat_messages'] = chat_messages
            return redirect('chatbot')
    else:
        form = ChatMessageForm()

    chat_messages = request.session.get('chat_messages', [])
    return render(request, 'chatbot.html', {
        'form': form,
        'chat_messages': chat_messages
    })
