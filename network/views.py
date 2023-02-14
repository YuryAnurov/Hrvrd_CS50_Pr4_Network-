from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
import datetime, json
from django.contrib.auth.decorators import login_required
#from django.views.decorators.csrf import csrf_exempt #- убрал, т.к. добавил csrf

from .models import User, Post


def post(request): #создаем пост, сохраняем и грузим в индекс
    if request.method == "POST":
        new_post = Post()
        new_post.content = request.POST.get('content')
        new_post.author = request.user
        new_post.created = datetime.datetime.now()
        new_post.save()
    return HttpResponseRedirect(reverse("index"))


def edit(request, post_id): #редактируем в javascript @csrf_exempt - убрал, т.к. добавил csrf в Cookie js

    # Запрос нужного поста
    try:
        edpost = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Обновляем пост
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("edpost") is not None:
            edpost.content = data["edpost"]
        edpost.save()
        return HttpResponse(status=204) #обязательно нужен return, без него (хоть с пустым return, хоть вообще без return - ошибка 500, но работает

    # Обновление д.б. чз PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

 
@login_required
def like(request, post_id): #ставим лайки в javascript
    # Запрос нужного поста
    try:
        likedpost = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    # Обновляем пост
    if request.method == "PUT":
        r = request.user
        if r in likedpost.liked.all(): 
            likedpost.liked.remove(r)
        else:
            likedpost.liked.add(r)
        # add/remove - сохраняются без save
        return HttpResponse(status=204) 
    

def profile(request, user_id): # страница с профилем пользователя
    userpage = User.objects.get(pk=user_id)
    r = request.user
    
    #Отрисовка кнопки при загрузке страницы:
    if r.is_authenticated:
        if userpage in r.follows.all(): 
            followBtn =  "Unfollow"
        else:
            followBtn = "Follow"
    else:
        followBtn = "False"
    
    #Считаем на скольких подписаны и подписчиков
    follows = userpage.follows.all().count()
    followers = User.objects.filter(follows=userpage).count()
    
    #Выводим чз paginator только посты просматримаемого профиля
    posts = Post.objects.filter(author=userpage).order_by('created').reverse()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {"followBtn":followBtn, "follows":follows, "followers":followers, "userpage":userpage, "page_obj": page_obj})


def follow(request, user_id):#Нажатие кнопки follow / unfollow
    userpage = User.objects.get(pk=user_id)
    r = request.user
    if userpage in r.follows.all(): 
        r.follows.remove(userpage)
    else:
        r.follows.add(userpage)
    return HttpResponseRedirect(reverse("profile", args=(user_id,)))


def following(request): #обработка для страницы с постами тех, на кого подписан пользователь, грузим индекс
    #фильтруем только посты пользователей, на кого подписаны
    qst =  request.user.follows.all() #qst = User.objects.filter(follows=request.user) - это фоловверы
    posts = Post.objects.filter(author__in=qst).order_by('created').reverse() #скобочки важны  после reverse, д.б метод
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {"page_obj": page_obj})


def index(request): #основная страница
    posts = Post.objects.all().order_by('created').reverse() #скобочки важны  после reverse, д.б метод, вот в {html}  без них
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {"page_obj": page_obj})


def login_view(request):
    if request.method == "POST":

        # Пытаемся залогиниться
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Проверяем, успешность аутентификации
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Убеждаемся, что пароль соответствует подтверждению
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Пытаемся создать юзера
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
