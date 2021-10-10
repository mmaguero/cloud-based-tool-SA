# restaurantes/urls.py

from django.conf.urls import url, include
from . import views

# add for rest #
from rest_framework_mongoengine import routers
from . import serializers

# this is DRF router for REST API viewsets
router = routers.DefaultRouter()

# register REST API endpoints with DRF router
router.register(r'restaurants', serializers.restaurantsViewSet, r"restaurants")
# end add #

urlpatterns = [

  url(r'^$', views.index, name='index'), # init page
  url(r'^test/$', views.test, name='test'),
  url(r'^buscar/$', views.buscar, name='buscar'), # search by name
  url(r'^listar/$', views.listar, name='listar'), # list items
  url(r'^compute/$', views.compute, name='compute'), # add item
  url(r'^restaurant/(?P<name>.+)$', views.restaurant, name='restaurant'), # item details
  url(r'^imagen/(?P<name>.+)$', views.imagen, name='imagen'), # show image item
  url(r'^r_ajax/(?P<name>.+)$', views.r_ajax, name='r_ajax'), # JQuery Ajax map load
  url(r'^api/', include(router.urls, namespace='api')), # REST API root view (generated by DRF router)
  url(r'^users/$', views.users, name='users'), # list users
  url(r'^user/$', views.user, name='user'), # search by user
  url(r'^globali/$', views.globali, name='globali'), # show image global
  url(r'^i_ajax/$', views.i_ajax, name='i_ajax'), # load image by Ajax
  url(r'^scrape/$', views.scrape, name='scrape'), # add item
]