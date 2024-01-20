from django.shortcuts import render, redirect
from django.http import HttpResponse
from os import path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from urllib.parse import urlparse
import urllib, base64
from PIL import Image
import wikipedia
from wordcloud import WordCloud, STOPWORDS
import random
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from urllib.request import urlopen

currdir = path.dirname(__file__)
# Create your views here.

def homepage(request):
    if request.method == 'POST':
        if request.POST.get('name1'):
            name1 = request.POST.get('name1')
            request.session['query']=name1
            return redirect('main:typo')
    if request.method == 'POST':
        if request.POST.get('name2'):
            name2 = request.POST.get('name2')
            request.session['query2']=name2
            return redirect('main:typo')

    return render(request=request,template_name="home.html"
                #--context={"":}
                 )
def grey_color_func(word, font_size, position, orientation, random_state=None,**kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

def get_wiki(query):
	title = wikipedia.search(query)[0]
	page = wikipedia.page(title)
	return page.content

def get_url(query2):
    html = urlopen(query2).read()
    features="html.parser"
    soup = BeautifulSoup(html,"html.parser")
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    # removes punctuation and numbers
    wordsFiltered = [word.lower() for word in words if word.isalpha()]
    filtered_words = [word for word in wordsFiltered if word not in stopwords.words('english')]
    return(' '.join(filtered_words))

def create_wordcloud(text):
    # mask = np.array(Image.open(path.join(currdir, "black.jpg")))
    stopwords = set(STOPWORDS)
    wc = WordCloud(background_color="black",
                    # mask=mask,
                    max_words=1000,
                    max_font_size=170,
                    width=1100, height=1500,
                    stopwords=stopwords)
    wc.generate(text)
    wc.recolor(color_func = grey_color_func)
    #wc.to_file(path.join(currdir, "wc2.jpg"))
    plt.figure(figsize = (6, 6), facecolor = None)
    plt.imshow(wc,interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad = 0)
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    #plt.savefig(img, format='png',bbox_inches='tight')
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return(img_b64)

def typo(request):
    if(request.session['query']!=""):
        query=request.session['query']
        text = get_wiki(query)
        text=text.upper()
    if(request.session['query2']!=""):
        query2=request.session['query2']
        text= get_url(query2)
        text=text.upper()

    wordcloud = create_wordcloud(text)
    request.session['query2']=""
    request.session['query']=""
    return render(request=request,template_name="typo.html",context={'wordcloud':wordcloud})
