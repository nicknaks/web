from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse

from django.core.cache import cache
from AskNakaznoy.models import *
from AskNakaznoy.forms import *
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def login(request):
    next_page = request.GET.get('next', default='/')
    if request.user.is_authenticated:
        return redirect(next_page)

    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login_page.html', {
            'form': form,
            'tags': cache.get('best_tags'),
            'best_users': cache.get('best_users'),
        })

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(request,
                                     username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'],
                                     )
            if user is not None:
                auth.login(request, user)
                return redirect(next_page)
            else:
                form.add_error(None, 'Sorry, wrong password or login!')
        print(form.errors)
        return render(request, 'login_page.html', {
            'form': form,
            'tags': cache.get('best_tags'),
            'best_users': cache.get('best_users'),
        })


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('next', default='/'))


def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            user = auth.authenticate(request,
                                     username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password1']
                                     )
            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                form.add_error(None, 'A user with that email already exists.')
        else:
            form.add_error(None, 'Sorry, password1 != password2!')
    else:
        form = RegisterForm()

    return render(request, 'registration_page.html', {
            'tags': cache.get('best_tags'),
            'form': form,
            'best_users': cache.get('best_users'),
    })


@login_required
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('settings'))
    else:
        user_data = {
            'username': request.user.username,
            'email': request.user.email,
            'nickname': request.user.profile.nickname,
            'avatar': request.user.profile.avatar,
        }

        form = SettingsForm(initial=user_data)

    return render(request, 'settings_page.html', {
        'tags': cache.get('best_tags'),
        'form': form,
        'best_users': cache.get('best_users'),
    })


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(data=request.POST, profile=request.user.profile)
        if form.is_valid():
            new_question = form.save()
            return redirect(reverse('question_page', kwargs={'pk': new_question.pk}))
    else:
        form = QuestionForm(profile=request.user.profile)

    return render(request, 'ask_question.html', {
        'tags': cache.get('best_tags'),
        'form': form,
        'best_users': cache.get('best_users'),
    })


def paginate(objects_list, request, per_page=20):
    limit = request.GET.get('limit', per_page)
    paginator = Paginator(objects_list, limit)
    page = request.GET.get('page')
    return paginator.get_page(page)


def new_questions(request):
    db_q = Question.objects.new()
    db_q_by_page = paginate(db_q, request)

    return render(request, 'new_question.html', {
        'questions': db_q_by_page,
        'tags': cache.get('best_tags'),
        'user': request.user,
        'best_users': cache.get('best_users'),
    })


def hot_questions(request):
    db_q = Question.objects.best()
    db_q_by_page = paginate(db_q, request)

    return render(request, 'hot_question.html', {
        'questions': db_q_by_page,
        'tags': cache.get('best_tags'),
        'user': request.user,
        'best_users': cache.get('best_users'),
    })


def tag_questions(request, pk):
    questions_by_tag = Question.objects.filter(tags__name=pk)
    question_pages = paginate(questions_by_tag, request, 5)

    return render(request, 'tag_question.html', {
        'tag': pk,
        'questions': question_pages,
        'tags': cache.get('best_tags'),
        'best_users': cache.get('best_users'),
    })


def question(request, pk):
    question_by_pk = get_object_or_404(Question, id=pk)
    answers = paginate(Answer.objects.best(pk), request, 5)

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentQuestionForm(profile=request.user.profile, question=question_by_pk, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('question_page', kwargs={'pk': pk}) + '?page=last')
    else:
        form = CommentQuestionForm(profile=None, question=question_by_pk)

    return render(request, 'question.html', {
        'tags': cache.get('best_tags'),
        'question': question_by_pk,
        'answers': answers,
        'form': form,
        'best_users': cache.get('best_users'),
    })


@require_POST
@login_required
def correct(request):
    data = request.POST
    form = CorrectForm(data=data)
    if form.is_valid():
        answer = form.save()
    return JsonResponse({'correct': answer.is_correct})


@require_POST
@login_required
def vote(request):
    data = request.POST

    if data['vote'] == 'like':
        user_vote = True
    else:
        user_vote = False

    if 'question' == data['name_class']:
        user_vote_data = {
            'user': request.user.profile,
            'is_liked': user_vote,
            'question': data['id'],
        }
        form = VoteQuestionForm(action=data['action'], data=user_vote_data)
        print(1)
        if form.is_valid():
            form.save()
            print(2)
        rating = Question.objects.get(id=data['id']).rating
        print(rating)

    if 'answer' == data['name_class']:
        user_vote_data = {
            'user': request.user.profile,
            'is_liked': user_vote,
            'answer': data['id'],
        }
        form = VoteAnswerForm(action=data['action'], data=user_vote_data)
        print(1)
        if form.is_valid():
            form.save()
            print(2)
        rating = Answer.objects.get(id=data['id']).rating
        print(rating)

    return JsonResponse({'rating': rating})
