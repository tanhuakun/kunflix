from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models import Show, Requests, Votes
from django.templatetags.static import static
from rest_framework import viewsets, generics
from .serializers import ShowShortSerializer
import os
import random
import string
from .tasks import sample_task
from django.conf import settings
import json
import requests
from django.views.decorators.http import require_http_methods
from django.core.files.base import ContentFile
from django.db.models import Count
from django.core.mail import send_mail

@login_required
def home_page(request):
    context = {}
    context['results'] = Show.objects.exclude(category='Unknown').order_by('-recentdate')[:5]
    
    if request.is_ajax():
        return JsonResponse({'html': render_to_string('mainsite/home_content.html', context, request=request)})
    return render(request, 'mainsite/home_page.html', context)

@login_required
def about_page(request):
    if request.is_ajax():
        print(request.headers['Referer'])
        return JsonResponse({'html': render_to_string('mainsite/about_content.html')})

    return render(request, 'mainsite/about_page.html')

@login_required
def shows_page(request, subcat=None):
    context = {}
    context['airing'] = Show.objects.exclude(category='Unknown').filter(airing=True)
    context['completed'] = Show.objects.exclude(category='Unknown').filter(airing=False)
    if subcat is None:
        context['english'] = Show.objects.filter(category='English')
        context['kdrama'] = Show.objects.filter(category='Kdrama')
        context['anime'] = Show.objects.filter(category='Anime')
        context['others'] = Show.objects.filter(category='Others')
        for k, v in context.items():
            context[k] = v.order_by('-recentdate')[0:10]
        if request.is_ajax():
            return JsonResponse({'html': render_to_string('mainsite/shows_content.html', context), 'script' : '/static/mainsite/search.js'})
        return render(request, 'mainsite/shows_page.html', context)
    elif subcat == 'English' or subcat == 'Kdrama' or subcat == 'Anime' or subcat == 'Others':
        for k, v in context.items():
            context[k] = v.order_by('-recentdate')[0:10]
        context['subcat'] = subcat
        context['shows'] = Show.objects.filter(category=subcat).order_by('title')
        if request.is_ajax():
            return JsonResponse({'html': render_to_string('mainsite/shows_subcat_content.html', context)})
        return render(request, 'mainsite/shows_subcat_page.html', context)
    else:
        return HttpResponse("You have done something wrong...", status=400)


    

@login_required
def requests_page(request):
    context = {'firstpage': True, 'lastpage':False, 'page': 1}
    
    qs = Requests.objects.all().filter(isfilled=False).filter(isrejected=False).annotate(numvotes=Count('votes')).order_by('-numvotes', '-reqdate')

    if len(qs) <= 10:
        context['lastpage'] = True
    
    context['results'] = qs[:10]
    for x in context['results']:
        try:
            Votes.objects.filter(request=x).get(voteuser=request.user)
            x.isuser = True
        except:
            x.isuser = False
    
    if request.is_ajax():
        return JsonResponse({'html': render_to_string('mainsite/requests_content.html', request=request, context=context), 'script' : '/static/mainsite/request.js' })
    return render(request, 'mainsite/requests_page.html', context)

@login_required
def search_request(request, requesttype, query = None, page = 1):
    context = {'firstpage' : False, 'lastpage': False}
    if page == 1:
        context['firstpage'] = True

    qs = Requests.objects.all()
    if requesttype == 'Pending':
        qs = qs.filter(isfilled=False).filter(isrejected=False)
    elif requesttype == 'Fulfilled':
        qs = qs.filter(isfilled=True)
    elif requesttype == 'Rejected':
        qs = qs.filter(isrejected=True)
    
    if query is not None:
        qs1 = qs.filter(title__iexact=query)
        qs1_length = len(qs1)
        query = query.split(' ')
        for word in query:      ## search query
            qs = qs.exclude(pk__in=qs1).filter(title__contains=word)
    
        qs = qs.annotate(numvotes=Count('votes')).order_by('-numvotes')

        if page == 1:
            qs1.annotate(numvotes=Count('votes'))
            if (len(qs)+qs1_length) <= page*10 and (len(qs)+qs1_length) > (page-1)*10:
                context['lastpage'] = True
            qs = qs[(page-1)*10:page*10-qs1_length]
            context['results'] = list(qs1) + list(qs)
            for x in context['results']:
                    try:
                        Votes.objects.filter(request=x).get(voteuser=request.user)
                        x.isuser = True
                    except:
                        x.isuser = False
        else:
            if len(qs) <= page*10 and len(qs) > (page-1)*10:
                context['lastpage'] = True
            qs = qs[(page-1)*10-qs1_length:page*10-qs1_length]
            context['results'] = qs
            for x in context['results']:
                try:
                    Votes.objects.filter(request=x).get(voteuser=request.user)
                    x.isuser = True
                except:
                    x.isuser = False        
    else:
        qs = qs.annotate(numvotes=Count('votes')).order_by('-numvotes')
        qs.order_by('-numvotes')
        if len(qs) <= page*10 and len(qs) > (page-1)*10:
            context['lastpage'] = True
        qs = qs[(page-1)*10:page*10]
        context['results'] = qs
        for x in context['results']:
            try:
                Votes.objects.filter(request=x).get(voteuser=request.user)
                x.isuser = True
            except:
                x.isuser = False
    
    context['page'] = page
    return JsonResponse({'html': render_to_string('mainsite/request_search.html', request=request, context=context)})

@login_required
@require_http_methods(['POST'])
def vote_request(request):
    data = request.POST.copy()
    try:
        Votes.objects.filter(request__webid=data.get('requestid')).get(voteuser=request.user).delete()
    except:
        Votes.objects.create(request=Requests.objects.get(webid=data.get('requestid')), voteuser=request.user)
    return HttpResponse('Done')

@login_required
@require_http_methods(['POST'])
def delete_request(request):
    data = request.POST.copy()
    try: 
        myobj = Requests.objects.get(webid=data.get('requestid'))
    except:
        return HttpResponse('no such id?',status=400)
    if myobj.requser == request.user:
        myobj.delete()
        return HttpResponse('Done')
    else:
        return HttpResponse('naughty...', status=400)

@login_required
def get_request(request, showtype, query = None):
    apikey = removed
    omdb_url = 'http://www.omdbapi.com/'
    jikan_url = 'https://api.jikan.moe/v3/search/anime'
    context = {}

    if query == None:
        return JsonResponse({'html' : 'Please enter something to search'}, status=400)


    if showtype == 'Normal':
        context['isAnime'] = False
        myreq = requests.get(omdb_url, params={'s' : query, 'apikey' : apikey})
        if myreq.status_code == 200:
            myjson = json.loads(myreq.text)
            if myjson['Response'] == 'True':
                if int(myjson['totalResults']) > 6:
                    myjson['Search'] = myjson['Search'][:6]
                context['results'] = myjson['Search']  # add context
                for num, x in enumerate(myjson['Search']):
                    if x['Year'] is not None:
                        x['Year'] = x['Year'][:4]
                    request.session[str(num + 1)] = x

            else:
                return JsonResponse({'html' : "No Results Found"}, status=404)
        else:
            return JsonResponse({'html' : "There is an issue with the online database"}, status=404)
        
    elif showtype == 'Anime':
        context['isAnime'] = True
        myreq = requests.get(jikan_url, params={'q' : query, 'limit' : '8'})
        if myreq.status_code == 200:
            myjson = json.loads(myreq.text)
            print(json.dumps(myjson, indent=4))
            for x in myjson['results']:
                if x['start_date'] is not None:
                    x['start_date'] = x['start_date'][:4]

            try:    
                myjson['results'] = [i for i in myjson['results'] if i['rated'] != 'Rx'][:6]
            except IndexError:
                pass
            context['results'] = myjson['results']  # add context
            for num, x in enumerate(myjson['results']):
                request.session[str(num + 1)] = x

        else:
            return JsonResponse({'html' : "There is an issue with the online database"}, status=404)

    return JsonResponse({'html' : render_to_string('mainsite/request_get.html', context)})

@login_required
@require_http_methods(['POST'])
def make_request(request):
    data = request.POST.copy()
    if data.get('showtype') == 'Normal':
        myobj = request.session[str(data.get('choice'))]
        apikey = removed
        omdb_url = 'http://www.omdbapi.com/'
        if not Requests.objects.filter(webid = myobj['imdbID']).exists():
            myreq = requests.get(omdb_url, params={'i' : myobj['imdbID'], 'apikey' : apikey})
            if myreq.status_code != 200:
                return JsonResponse({'html' : 'An error occured when processing the request.'}, status=400)
            
            myjson = json.loads(myreq.text)
            print(json.dumps(myjson, indent=4))
            newreq = Requests(title=myjson['Title'], plot=myjson['Plot'], requser=request.user, webid=myjson['imdbID'])
            imgrequest = requests.get(myjson['Poster'])
            if imgrequest.status_code == 200:
                newreq.image.save('imdb' + myjson['imdbID'] + '.jpg', ContentFile(imgrequest.content), save=True)
            else:
                return JsonResponse({'html' : 'An error occured when processing the request.'}, status=400)
        else:
            return JsonResponse({'html': 'Request already exists!'}, status = 400)
    else:
        myobj = request.session[str(data.get('choice'))]
        if not Requests.objects.filter(webid = myobj['mal_id']).exists():
            newreq = Requests(title=myobj['title'], plot=myobj['synopsis'], requser=request.user, webid = myobj['mal_id'])
            imgrequest = requests.get(myobj['image_url'])
            if imgrequest.status_code == 200:
                newreq.image.save('mal' + str(myobj['mal_id']) + '.jpg', ContentFile(imgrequest.content), save=True)
            else:
                return JsonResponse({'html' : 'An error occured when processing the request.'}, status=400)
        else:
            return JsonResponse({'html': 'Request already exists!'}, status = 400)

    Votes.objects.create(request=newreq, voteuser=request.user)
    return HttpResponse('none')

@login_required
def search(request, inputq=None, page = 1):
    if inputq is not None:
        qs = Show.objects.exclude(category='Unknown')
        context = {'lastpage' : False, 'firstpage': True, 'page': page, 'prevpage' : page-1, 'nextpage' : page+1, 'inputq' : inputq}
        titlelist = inputq.split(' ')
        
        for x in titlelist:
            qs = qs.filter(title__contains=x)
        
        if len(qs) <= page*10 and len(qs) > (page-1)*10:
            context['lastpage'] = True
        if page is not 1:
            context['firstpage'] = False

        qs = qs.order_by('-recentdate')[(page*10-10):(page*10)]
        context['results'] = qs

    if request.is_ajax():
        return JsonResponse({'html' : render_to_string('mainsite/search_content.html', context)})
    return render(request, 'mainsite/search_page.html', context)

@login_required
def title(request, showname=None):
    context = {}
    context['airing'] = Show.objects.exclude(category='Unknown').filter(airing=True)
    context['completed'] = Show.objects.exclude(category='Unknown').filter(airing=False)
    for k, v in context.items():
        context[k] = v.order_by('-recentdate')[0:10]
    try:
        listparams = showname.split('_')
        qs = Show.objects.filter(year=listparams[1])
        qs = qs.get(title=listparams[0])
    except:
        return HttpResponse('invalid title')
    if qs is not None:
        context['results'] = qs
    
    context['thumbnails'] = sorted(os.listdir(settings.THUMBNAIL_PATH + qs.path))
    #context['thumbnails'] = [1,2,3]

    if request.is_ajax():
        return JsonResponse({'html' : render_to_string('mainsite/title_content.html', context)})
    return render(request, "mainsite/title_page.html", context)

@login_required
def episode(request, showname, ep):
    try:
        listparams = showname.split('_')
        qs = Show.objects.filter(year=listparams[1])
        qs = qs.get(title=listparams[0])
    except:
        return HttpResponse('invalid title')
    if qs is not None:
        if ep > qs.episodes:
            return HttpResponse('invalid episode')
    context = {}
    context['results'] = qs
    context['video'] = sorted(os.listdir(settings.VIDEO_PATH + qs.path))[ep-1]
    context['caption'] = context['video'][:-4] + '.vtt'
    if request.is_ajax():
        return JsonResponse({'html' : render_to_string('mainsite/episode_episode.html', context), 'script' : '/static/mainsite/episode.js'})
    return render(request, "mainsite/episode_page.html", context)


@require_http_methods(['POST', 'GET'])
@user_passes_test(lambda u: u.is_superuser)
def upload(request):
    context = {'secondstep' : False}
    
    if request.method == "POST":
        if request.POST['action'] == 'NextStep':
            context['request'] = Requests.objects.get(pk=request.POST['request_choice'])
            if request.POST['show_choice'] != 'Reject':
                context['show'] = Show.objects.get(pk=request.POST['show_choice'])
                context['secondstep'] = True
            else: 
                context['request'].isrejected = True
                context['request'].save()
        if request.POST['action'] == 'Finally':
            therequest = Requests.objects.get(pk=request.POST['reqid'])
            theshow = Show.objects.get(pk=request.POST['showid'])
            
            theshow.title = request.POST['title']
            theshow.plot = request.POST['plot']
            theshow.year = request.POST['year']
            theshow.category = request.POST['category']
            theshow.airing = request.POST.get('airing', False)
            new_img = ContentFile(therequest.image.read())
            new_img_name = therequest.image.name.split('/')[-1]
            theshow.image.save(new_img_name, new_img)
            therequest.isfilled = True
            
            therequest.save()
            theshow.save()
            
            
    allreq = Requests.objects.filter(isfilled=False).filter(isrejected=False).order_by('title')
    unknownshows = Show.objects.filter(category='Unknown')
    context['requests'] = allreq
    context['shows'] = unknownshows
    return render(request, 'mainsite/upload_page.html', context)

@login_required
def videos(request, title, name):
    response = HttpResponse()
    response['Content-Type'] = ''
    response['X-Sendfile'] = (settings.VIDEO_PATH + title + '\\' + name)
    return response






@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

class ShowShortViewSet(generics.ListAPIView):
    
    serializer_class = ShowShortSerializer
    queryset = Show.objects.all()
    def get_queryset(self):
        queryset = Show.objects.exclude(category='Unknown')
        title = self.request.query_params.get('title', None)
        titlelist = title.split(' ')
        if title is not None:
            for x in titlelist:
                queryset = queryset.filter(title__contains=x)
            queryset = queryset.order_by('-recentdate')[:5]
        #for x in queryset:
        #    x.image = ('posters/' + queryset.image[6:])
        return queryset
# Create your views here.
