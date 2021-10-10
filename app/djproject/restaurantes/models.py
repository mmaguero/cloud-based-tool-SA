from django.db import models
from mongoengine import *
#import datetime
#import PIL

#connect('sadb', host='localhost', port=27017)
connect('sadb', host='restaurant_db', port=27017)

# Esquema para la BD de mongoDB
class addr(EmbeddedDocument):
    locality     = StringField()
    street       = StringField()
    postal_code  = StringField(required=False)
    country      = StringField(required=False)

class stats(EmbeddedDocument):
    compound  = FloatField(required=False)
    neg       = FloatField(required=False)
    neu       = FloatField(required=False)
    pos       = FloatField(required=False)

class likes(EmbeddedDocument):
    title           = StringField()
    description     = StringField()
    user            = StringField()
    stars           = StringField()
    date            = StringField()
    title_res       = EmbeddedDocumentField(stats)
    description_res = EmbeddedDocumentField(stats)
    review_res      = EmbeddedDocumentField(stats)
    
class restaurant(Document):
    name             = StringField()
    url              = StringField()
    datetime         = StringField()
    avg_stars        = StringField(required=False)
    address          = EmbeddedDocumentField(addr)
    reviews          = ListField(EmbeddedDocumentField(likes))
    origin           = StringField()

# Consulta, los tres primeros
# for r in restaurants.objects[:3]:
#    print (r.name, r.address.coord, r.grades[0].date)
