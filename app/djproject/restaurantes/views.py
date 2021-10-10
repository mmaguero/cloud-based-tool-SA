# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .forms import ComputeForm
from .models import restaurant as restaurant_, addr, likes, stats
from django.contrib.auth.decorators import login_required
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize, corpus
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.gridspec import GridSpec

import requests
import json
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 8.0
import logging
import random
import datetime

log = logging.getLogger(__name__)

# Create your views here.

def index(request):
    log.info("INDEX -")
    context = {
        'menu': 'index'
    }
    #return HttpResponse('My restaurant Manager')
    return render(request,'index.html',context)

def test(request):
    valor = 3
    context = {
        'variable': valor,
        'resta': restaurant_.objects[:5],
    }   # Aqui van la las variables para la plantilla
    return render(request,'test.html', context)

@login_required
def listar(request):
    log.info("LIST -")
    #resta = restaurant_.objects(reviews__1__exists=True).order_by('-avg_stars', 'address.locality', 'name')[:10],
    lista = restaurant_._get_collection().aggregate([
    { "$match": { "reviews": { "$exists": True } }},
    { "$unwind": "$reviews" },
    { "$group": {
        "_id": "$_id",
        "id": { "$first": "$_id" },
        "name": { "$first": "$name" },
        "datetime": { "$first": "$datetime" },
        "avg_stars": { "$first": "$avg_stars" },
        "locality": { "$first": "$address.locality" },
        "reviews": { "$push": "$reviews" },
        "reviewsLength": { "$sum": 1 }
    }},
    { "$sort": { "avg_stars": -1, "reviewsLength": -1 } }
    ])

    context = {
        'resta': lista,
        'menu': 'list'
    }   # Aqui van la las variables para la plantilla
    return render(request,'listar.html', context)

@login_required
def users(request):
    log.info("LIST -")
    lista = restaurant_._get_collection().aggregate([
    { "$unwind": '$reviews'},
    { "$group": {"_id": '$reviews.user',
      "name": { "$first": '$reviews.user' }, "date": { "$first": '$reviews.date' }, "avg_stars": { "$avg": '$reviews.stars'},
      "reviewsLength": { "$sum": 1 }}},
    { "$sort": { "avg_stars": -1, "reviewsLength": -1 } },
    { '$match': { 'reviewsLength': {'$gt': 1}} } ])

    context = {
        'resta': lista,
        'menu': 'users'
    }   # Aqui van la las variables para la plantilla
    return render(request,'users.html', context)

@login_required
def buscar(request):
    log.info("SEARCH -")
    search = request.GET.get('searching')
    #lista=restaurant_.objects(name__icontains=search)
    lista=restaurant_._get_collection().aggregate([
    { "$match": { "reviews": { "$exists": True }, "name" : { "$regex" : ".*"+search+".*", '$options' : 'i' } }},
    { "$unwind": "$reviews" },
    { "$group": {
        "_id": "$_id",
        "id": { "$first": "$_id" },
        "name": { "$first": "$name" },
        "datetime": { "$first": "$datetime" },
        "avg_stars": { "$first": "$avg_stars" },
        "locality": { "$first": "$address.locality" },
        "reviews": { "$push": "$reviews" },
        "reviewsLength": { "$sum": 1 }
    }},
    { "$sort": { "reviewsLength": -1, "avg_stars": -1 } }
    ])
    context = {
        'resta': lista,
    }
    return render(request,'listar.html', context)

@login_required
def compute(request):
    log.info("COMPUTE -")
    formu = ComputeForm()
    sentd = []
    sentt = []
    sent = []

    if request.method == "POST":

      formu = ComputeForm(request.POST, request.FILES)
      if formu.is_valid():                    # valida o anhade errores

	      # datos sueltos
          title = formu.cleaned_data['title']
          description = formu.cleaned_data['description']

          sid = SentimentIntensityAnalyzer()

          sentences = []
          paragraphSentimentsTitle= 0.0
          negTitle= 0.0
          neuTitle= 0.0
          posTitle= 0.0
          lines_listt = tokenize.sent_tokenize(title)
          sentences.extend(lines_listt)
          exclude = 0
          for sentence in sentences:
            log.info(sentence)
            if ("!" in sentence or "?" in sentence) and len(sentence.strip()) == 1: 
              exclude += 1 
            stt = sid.polarity_scores(sentence)
            paragraphSentimentsTitle += stt["compound"]
            negTitle += stt['neg']
            neuTitle += stt['neu']
            posTitle += stt['pos']
            log.info(str(stt['compound']) + " " + str(stt['neg']) + " " + str(stt['neu']) + " " + str(stt['pos']))
          i = len(sentences)-exclude
          paragraphSentimentsTitle/=i
          negTitle/=i
          neuTitle/=i
          posTitle/=i
          sentt = stats(compound=round(paragraphSentimentsTitle, 4), neg=round(negTitle, 4), neu=round(neuTitle, 4), pos=round(posTitle, 4))
          log.info(str(sentt.compound) + " " + str(sentt.neg) + " " + str(sentt.neu) + " " + str(sentt.pos) + " " + str(i))

          sentences = []
          paragraphSentimentsDescription= 0.0
          negDescription= 0.0
          neuDescription= 0.0
          posDescription= 0.0
          lines_listd = tokenize.sent_tokenize(description)
          sentences.extend(lines_listd)
          exclude = 0
          for sentence in sentences:
            log.info(sentence)
            if ("!" in sentence or "?" in sentence) and len(sentence.strip()) == 1: 
              exclude += 1 
            std = sid.polarity_scores(sentence)
            paragraphSentimentsDescription += std["compound"]
            negDescription += std['neg']
            neuDescription += std['neu']
            posDescription += std['pos']
            log.info(str(std['compound']) + " " + str(std['neg']) + " " + str(std['neu']) + " " + str(std['pos']))
          i = len(sentences)-exclude
          paragraphSentimentsDescription/=i
          negDescription/=i
          neuDescription/=i
          posDescription/=i
          sentd = stats(compound=round(paragraphSentimentsDescription, 4), neg=round(negDescription, 4), neu=round(neuDescription, 4), pos=round(posDescription, 4))
          log.info(str(sentd.compound) + " " + str(sentd.neg) + " " + str(sentd.neu) + " " + str(sentd.pos) + " " + str(i))

          compound_ = (paragraphSentimentsDescription*0.85+paragraphSentimentsTitle*0.15)
          neg_ = (negDescription*0.85+negTitle*0.15)
          neu_ = (neuDescription*0.85+neuTitle*0.15)
          pos_ = (posDescription*0.85+posTitle*0.15)
          sent = stats(compound=round(compound_, 4), neg=round(neg_, 4), neu=round(neu_, 4), pos=round(pos_, 4))
          log.info(str(sent.compound) + " " + str(sent.neg) + " " + str(sent.neu) + " " + str(sent.pos) + " review")

    context = {
      'form': formu,
      'menu': 'compute',
      'sentt': sentt,
      'sentd': sentd,
      'sent': sent,
    }
    return render(request, 'form.html', context)

# url
@login_required
def restaurant(request, name):
  log.info("DETAIL -")

  log.info("REVIEWS SA -")
  sid = SentimentIntensityAnalyzer()
  resta = restaurant_.objects(id=name).as_pymongo()[0]

  countReviews = 0
  sumCompound = 0.0
  sumNeg = 0.0
  sumNeu = 0.0
  sumPos = 0.0
  for r in resta['reviews']:
    countReviews += 1
    paragraphSentimentsTitle= 0.0
    negTitle= 0.0
    neuTitle= 0.0
    posTitle= 0.0
    try:
      if len(r['title_res']):
          log.info("SA TITLE EXISTs -")
          paragraphSentimentsTitle= r['title_res']['compound']
          negTitle= r['title_res']['neg']
          neuTitle= r['title_res']['neu']
          posTitle= r['title_res']['pos']
    except:
      sentences = []
      lines_listt = tokenize.sent_tokenize(r['title'])
      sentences.extend(lines_listt)
      exclude = 0
      for sentence in sentences:
        log.info(sentence)
        if ("!" in sentence or "?" in sentence) and len(sentence.strip()) == 1: 
          exclude += 1 
        stt = sid.polarity_scores(sentence)
        paragraphSentimentsTitle += stt["compound"]
        negTitle += stt['neg']
        neuTitle += stt['neu']
        posTitle += stt['pos']
        log.info(str(stt['compound']) + " " + str(stt['neg']) + " " + str(stt['neu']) + " " + str(stt['pos']))
      i = len(sentences)-exclude
      paragraphSentimentsTitle/=i
      negTitle/=i
      neuTitle/=i
      posTitle/=i
      sentt = stats(compound=round(paragraphSentimentsTitle, 4), neg=round(negTitle, 4), neu=round(neuTitle, 4), pos=round(posTitle, 4))
      log.info(str(sentt.compound) + " " + str(sentt.neg) + " " + str(sentt.neu) + " " + str(sentt.pos) + " " + str(i))
      restaurant_.objects(id=resta['_id'], reviews__match=r).update_one(set__reviews__S__title_res=sentt, upsert=True)
      log.info("SA TITLE ADD -")

    paragraphSentimentsDescription= 0.0
    negDescription= 0.0
    neuDescription= 0.0
    posDescription= 0.0
    try:
      if len(r['description_res']):
          log.info("SA DESCRIPTION EXISTs -")
          paragraphSentimentsDescription= r['description_res']['compound']
          negDescription= r['description_res']['neg']
          neuDescription= r['description_res']['neu']
          posDescription= r['description_res']['pos']
    except:
      sentences = []
      for index in range(len(r['description'])):
        lines_listd = tokenize.sent_tokenize(r['description'][index])
        sentences.extend(lines_listd)
      exclude = 0
      for sentence in sentences:
        log.info(sentence)
        if ("!" in sentence or "?" in sentence) and len(sentence.strip()) == 1: 
          exclude += 1 
        std = sid.polarity_scores(sentence)
        paragraphSentimentsDescription += std["compound"]
        negDescription += std['neg']
        neuDescription += std['neu']
        posDescription += std['pos']
        log.info(str(std['compound']) + " " + str(std['neg']) + " " + str(std['neu']) + " " + str(std['pos']))
      i = len(sentences)-exclude
      paragraphSentimentsDescription/=i
      negDescription/=i
      neuDescription/=i
      posDescription/=i
      sentd = stats(compound=round(paragraphSentimentsDescription, 4), neg=round(negDescription, 4), neu=round(neuDescription, 4), pos=round(posDescription, 4))
      log.info(str(sentd.compound) + " " + str(sentd.neg) + " " + str(sentd.neu) + " " + str(sentd.pos) + " " + str(i))
      restaurant_.objects(id=resta['_id'], reviews__match=r).update_one(set__reviews__S__description_res=sentd, upsert=True)
      log.info("SA DESCRIPTION ADD -")

    compound_ = (paragraphSentimentsDescription*0.85+paragraphSentimentsTitle*0.15)
    neg_ = (negDescription*0.85+negTitle*0.15)
    neu_ = (neuDescription*0.85+neuTitle*0.15)
    pos_ = (posDescription*0.85+posTitle*0.15)
    sumCompound += compound_
    sumNeg += neg_
    sumNeu += neu_
    sumPos += pos_
    try:
      if len(r['review_res']):
        log.info("SA REVIEW EXISTs -")
    except:
      sent = stats(compound=round(compound_, 4), neg=round(neg_, 4), neu=round(neu_, 4), pos=round(pos_, 4))
      log.info(str(sent.compound) + " " + str(sent.neg) + " " + str(sent.neu) + " " + str(sent.pos) + " review")
      restaurant_.objects(id=resta['_id'], reviews__match=r).update_one(set__reviews__S__review_res=sent, upsert=True)
      log.info("SA REVIEW ADD -")

  log.info("RETURN DETAIL -")
  resta = restaurant_.objects(id=name)[0]
  restaSentiment =  stats(compound=round(sumCompound/countReviews, 4), neg=round(sumNeg/countReviews, 4), neu=round(sumNeu/countReviews, 4), pos=round(sumPos/countReviews, 4))

  context = {
      'resta'         : resta,
      'countReviews'  : countReviews,
      'restaSentiment': restaSentiment,
      'menu': 'list'
  }
  return render(request, 'detalle.html', context)

@login_required
def user(request):
  log.info("USER -")
  search = request.GET.get('user')
  resta = restaurant_._get_collection().aggregate([
    { "$unwind": '$reviews'},
    { "$match": {'reviews.user': search }},
    { "$group": {"_id": '$_id', "name": { "$first": '$name' },
      "id": { "$first": '$_id' }, "address": { "$first": '$address' },
      "avg_stars": { "$first": '$avg_stars'}, "reviews": { "$push": '$reviews'}}},
    { "$sort": { "reviews.date": -1 } },
  ])

  sid = SentimentIntensityAnalyzer()
  userStars = 0.0
  countReviews = 0
  sumCompound = 0.0
  sumNeg = 0.0
  sumNeu = 0.0
  sumPos = 0.0
  for rr in resta:
      for r in rr['reviews']:
        countReviews += 1
        userStars += r['stars']
        paragraphSentimentsTitle= 0.0
        negTitle= 0.0
        neuTitle= 0.0
        posTitle= 0.0
        try:
          if len(r['title_res']):
              log.info("SA TITLE EXISTs -")
              paragraphSentimentsTitle= r['title_res']['compound']
              negTitle= r['title_res']['neg']
              neuTitle= r['title_res']['neu']
              posTitle= r['title_res']['pos']
        except:
          sentences = []
          lines_listt = tokenize.sent_tokenize(r['title'])
          sentences.extend(lines_listt)
          exclude = 0
          for sentence in sentences:
            log.info(sentence)
            if ("!" in sentence or "?" in sentence) and len(sentence.strip()) == 1: 
              exclude += 1 
            stt = sid.polarity_scores(sentence)
            paragraphSentimentsTitle += stt["compound"]
            negTitle += stt['neg']
            neuTitle += stt['neu']
            posTitle += stt['pos']
            log.info(str(stt['compound']) + " " + str(stt['neg']) + " " + str(stt['neu']) + " " + str(stt['pos']))
          i = len(sentences)-exclude
          paragraphSentimentsTitle/=i
          negTitle/=i
          neuTitle/=i
          posTitle/=i
          sentt = stats(compound=round(paragraphSentimentsTitle, 4), neg=round(negTitle, 4), neu=round(neuTitle, 4), pos=round(posTitle, 4))
          log.info(str(sentt.compound) + " " + str(sentt.neg) + " " + str(sentt.neu) + " " + str(sentt.pos) + " " + str(i))
          restaurant_.objects(id=rr['_id'], reviews__match=r).update_one(set__reviews__S__title_res=sentt, upsert=True)
          log.info("SA TITLE ADD -")

        paragraphSentimentsDescription= 0.0
        negDescription= 0.0
        neuDescription= 0.0
        posDescription= 0.0
        try:
          if len(r['description_res']):
              log.info("SA DESCRIPTION EXISTs -")
              paragraphSentimentsDescription= r['description_res']['compound']
              negDescription= r['description_res']['neg']
              neuDescription= r['description_res']['neu']
              posDescription= r['description_res']['pos']
        except:
          sentences = []
          for index in range(len(r['description'])):
            lines_listd = tokenize.sent_tokenize(r['description'][index])
            sentences.extend(lines_listd)
          exclude = 0
          for sentence in sentences:
            log.info(sentence)
            if ("!" in sentence or "?" in sentence) and len(sentence.strip()) == 1: 
              exclude += 1
            std = sid.polarity_scores(sentence)
            paragraphSentimentsDescription += std["compound"]
            negDescription += std['neg']
            neuDescription += std['neu']
            posDescription += std['pos']
            log.info(str(std['compound']) + " " + str(std['neg']) + " " + str(std['neu']) + " " + str(std['pos']))
          i = len(sentences)-exclude
          paragraphSentimentsDescription/=i
          negDescription/=i
          neuDescription/=i
          posDescription/=i
          sentd = stats(compound=round(paragraphSentimentsDescription, 4), neg=round(negDescription, 4), neu=round(neuDescription, 4), pos=round(posDescription, 4))
          log.info(str(sentd.compound) + " " + str(sentd.neg) + " " + str(sentd.neu) + " " + str(sentd.pos) + " " + str(i))
          restaurant_.objects(id=rr['_id'], reviews__match=r).update_one(set__reviews__S__description_res=sentd, upsert=True)
          log.info("SA DESCRIPTION ADD -")

        compound_ = (paragraphSentimentsDescription*0.85+paragraphSentimentsTitle*0.15)
        neg_ = (negDescription*0.85+negTitle*0.15)
        neu_ = (neuDescription*0.85+neuTitle*0.15)
        pos_ = (posDescription*0.85+posTitle*0.15)
        sumCompound += compound_
        sumNeg += neg_
        sumNeu += neu_
        sumPos += pos_
        try:
          if len(r['review_res']):
            log.info("SA REVIEW EXISTs -")
        except:
          sent = stats(compound=round(compound_, 4), neg=round(neg_, 4), neu=round(neu_, 4), pos=round(pos_, 4))
          log.info(str(sent.compound) + " " + str(sent.neg) + " " + str(sent.neu) + " " + str(sent.pos) + " review")
          restaurant_.objects(id=rr['_id'], reviews__match=r).update_one(set__reviews__S__review_res=sent, upsert=True)
          log.info("SA REVIEW ADD -")

  restaSentiment =  stats(compound=round(sumCompound/countReviews, 4), neg=round(sumNeg/countReviews, 4), neu=round(sumNeu/countReviews, 4), pos=round(sumPos/countReviews, 4))
  userStars /= countReviews
  resta = restaurant_._get_collection().aggregate([
    { "$unwind": '$reviews'},
    { "$match": {'reviews.user': search }},
    { "$group": {"_id": '$_id', "name": { "$first": '$name' },
      "id": { "$first": '$_id' }, "address": { "$first": '$address' },
      "avg_stars": { "$first": '$avg_stars'},
      "reviews": { "$push": '$reviews'}}},
    { "$sort": { "reviews.date": -1 } } ])

  context = {
      'resta' : resta,
      'username'  : search,
      'countReviews'  : countReviews,
      'restaSentiment': restaSentiment,
      'userStars': userStars,
      'menu': 'users'
  }
  return render(request, 'user.html', context)

def scrape(request):
    jsonList = []
    req = requests.get('http://localhost:9080/crawl.json?spider_name=tripadvisor-restaurant&start_requests=True')
    req.raise_for_status()
    jsonList.append(json.loads(req.content.decode('utf-8')))
    content = []
    myData = {}
    for data in jsonList:
      myData['status'] = data['status']
      if myData['status'] == "ok":
        myData['spider_name'] = data['spider_name']
        myData['items'] = len(data['items'])
        myData['status'] = data['status']
        myData['stats'] = data['stats']
        myData['items_dropped'] = len(data['items_dropped'])
      if myData['status'] == "error":
        myData['code'] = data['code']
        myData['message'] = data['message']
    content.append(myData)
    '''req = requests.get('http://localhost:9080/crawl.json?spider_name=tripadvisor-restaurant&start_requests=True')
    content = req.text'''
    context = {
      'result': content,
      'menu': 'scrape'
    }
    return render(request, 'scrape.html', context)

# recuperar foto
@login_required
def imagen(request, name):
    log.info("IMAGE -")
    resta = restaurant_.objects(id=name)[0]

    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]
    for i in range(len(resta.reviews)):
        x.append(datetime.datetime.strptime(resta.reviews[i].date, '%Y-%m-%d').date())
        y.append(int(resta.reviews[i].stars))
    ax.set_title("Rating History")
    ax.plot_date(x, y, 'b.-.')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    response=HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response

#@login_required
def globali(request):
  log.info("GLOBAL -")

  fig1 = Figure()
  ax1 = fig1.add_subplot(111)

  name = request.GET.get('i')
  uname = request.GET.get('u')
  if name == "rate":
    resta = restaurant_._get_collection().aggregate([
    { "$unwind": "$reviews"},
    { "$group": {"_id": '$avg_stars', "avg_stars": { "$first": '$avg_stars'}, "count": { "$sum": 1 }}},
    { "$sort": { "avg_stars": -1 } }
    ])

    lbl = ["★","★★","★★★","★★★★","★★★★★"]
    num = []
    for i in range(5):
       num.append(0)
    for r in resta:
      if float(r['avg_stars']) == 5.0:
        num[4] += r['count']
      if float(r['avg_stars']) < 5.0:
        num[3] += r['count']
      if float(r['avg_stars']) < 4.0:
        num[2] += r['count']
      if float(r['avg_stars']) < 3.0:
        num[1] += r['count']
      if float(r['avg_stars']) < 2.0:
        num[0] += r['count']

    explode = []
    for i in range(5):
       explode.append(0.125)
    colors = ["red","red","yellow","green","green"]
    ax1.pie(num, labels=lbl, shadow=True, startangle=180, autopct='%1.1f%%', pctdistance=0.9, labeldistance=1.1, explode=explode, colors=colors)

  if name == "city":
    resta = restaurant_._get_collection().aggregate([
    { "$group": {"_id": '$address.locality', "locality": { "$first": '$address.locality'}, "count": { "$sum": 1 }}},
    { "$match": {"locality": {'$regex' : '^((?!18).)*$', '$options' : 'i'} }},
    { "$sort": { "count": -1 } },
    { "$limit": 10 }
    ])

    lbl = []
    num = []
    explode = []
    for r in resta:
      num.append(r['count'])
      lbl.append(r['locality'])
      explode.append(0.15)

    ax1.pie(num, labels=lbl, shadow=True, startangle=180, autopct='%1.1f%%', pctdistance=0.7, labeldistance=0.9, explode=explode)

  if name == "review":
    resta = restaurant_._get_collection().aggregate([
    { "$unwind": "$reviews"},
    { "$group": {"_id": '$name', "restaurant": { "$first": '$name'}, "count": { "$sum": 1 }}},
    { "$sort": { "count": -1 } },
    { "$limit": 10 }
    ])

    lbl = []
    num = []
    explode = []
    for r in resta:
      num.append(r['count'])
      lbl.append(r['restaurant'])
      explode.append(0.05)

    ax1.pie(num, labels=lbl, shadow=True, startangle=90, autopct='%1.1f%%', pctdistance=0.5, labeldistance=0.7, explode=explode)

  if name == "user":
    if uname:
        review = restaurant_._get_collection().aggregate([
            { "$unwind": '$reviews'},
            { "$match": {'reviews.user': uname }},
            { "$group": {"_id": '$reviews.date', "date": { "$first": '$reviews.date'}, "stars": { "$avg": '$reviews.stars'} }},
            { "$sort": { "date": 1 } },
        ])

        lbl = []
        num = []
        for r in review:
            lbl.append(datetime.datetime.strptime(r['date'], '%Y-%m-%d').date())
            num.append(r['stars'])

        ax1.set_title("Rating History")
        ax1.plot(lbl, num, 'b.-.')
        ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    else:
        resta = restaurant_._get_collection().aggregate([
        { "$unwind": "$reviews"},
        { "$group": {"_id": '$reviews.user', "user": { "$first": '$reviews.user'}, "count": { "$sum": 1 }}},
        { "$sort": { "count": -1 } },
        { "$limit": 50 }
        ])

        lbl = []
        num = []
        explode = []
        for r in resta:
          if r['user'] == "A TripAdvisor Member" or r['user'] == " ":
            continue

          num.append(r['count'])
          lbl.append(r['user'])
          explode.append(0.05)

          if len(num) == 10:
            break

        ax1.pie(num, labels=lbl, shadow=True, startangle=90, autopct='%1.1f%%', pctdistance=0.8, labeldistance=1.0, explode=explode)

  if uname is None:
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
  fig1.autofmt_xdate()
  canvas=FigureCanvas(fig1)
  response=HttpResponse(content_type='image/png')
  canvas.print_png(response)

  fig1.clear()

  return response

def r_ajax(request, name):
  log.info("AJAX MAP -")
  resta = restaurant_.objects(id=name)[0]
  maps = '<div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://maps.google.com/maps?q='+str(resta.name) + ' ' + str(resta.address.street) + ' ' + str(resta.address.postal_code) + ' ' + str(resta.address.locality)+'&amp;ie=UTF8&amp;&amp;output=embed" allowfullscreen></iframe></div>'
  return JsonResponse({'map':maps})    # podría ser string o HTML

def i_ajax(request):
  log.info("AJAX IMAGE -")
  name = request.GET.get('i')
  url = 'globali/?i='+name
  return JsonResponse({'url':url})
