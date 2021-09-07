from django.urls import path, include
from . import views
from django.conf import settings



urlpatterns = [
    path('home', views.home_page, name = 'home_page'),
    path('about', views.about_page, name = 'about_page'),
    path('shows', views.shows_page, name = 'shows_page'),
    path('shows/<subcat>', views.shows_page, name = 'shows_pagewithcat'),
    path('requests', views.requests_page, name = 'requests_page'),
    path('searchrequest/<requesttype>/<query>/<int:page>', views.search_request, name = 'search_request'),
    path('searchrequest/<requesttype>//<int:page>', views.search_request, name = 'search_requestonlytype'),
    path('voterequest', views.vote_request, name = 'vote_request'),
    path('deleterequest', views.delete_request, name = 'delete_request'),
    path('getrequest/<showtype>/<query>', views.get_request, name = 'get_request'),
    path('getrequest/<showtype>/', views.get_request, name = 'get_requestnoinput'),
    path('makerequest', views.make_request, name = 'make_request'),
    path('logout', views.logout_page, name = 'logout_page'),
    path('search', views.search, name = 'search_noinput'),
    path('search/<inputq>', views.search, name = 'search_nopage'),
    path('search/<inputq>/<int:page>', views.search, name = 'search'),
    path('title/<showname>', views.title, name = 'title'),
    path('title', views.title, name = 'title_noinput'),
    path('title/<showname>/<int:ep>', views.episode, name ='episode'),
    path('upload', views.upload, name = 'upload'),
    path('videos/<title>/<name>', views.videos, name = 'video')
]