from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F

from AskNakaznoy.models import *


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class RegisterForm(UserCreationForm):
    nickname = forms.CharField(max_length=32, label='Nickname')
    email = forms.EmailField(label='Email')
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'nickname', 'avatar']

    def save(self, commit=False):
        if User.objects.filter(email=self.cleaned_data['email']) is None:
            return None

        user = super(RegisterForm, self).save(commit=True)
        Profile.objects.create(user_id=user.id, nickname=self.cleaned_data['nickname'])

        if self.files.get('avatar'):
            profile = Profile.objects.get(user_id=user.id)
            profile.avatar = self.files.get('avatar')
            profile.save()

        if commit:
            user.save()
        return user


class SettingsForm(forms.ModelForm):
    nickname = forms.CharField(max_length=32, label='Nickname', required=False)
    email = forms.EmailField(label='Email', required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'avatar']

    def save(self, commit=False):
        user = super(SettingsForm, self).save(commit=True)
        Profile.objects.filter(user=user).update(nickname=self.cleaned_data['nickname'])

        if self.files.get('avatar'):
            profile = Profile.objects.get(user_id=user.id)
            profile.avatar = self.files.get('avatar')
            profile.save()

        if commit:
            user.save()
        return user


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(label='Tags')

    class Meta:
        model = Question
        fields = ['title', 'text']

    def __init__(self, profile, *args, **kwargs):
        self.profile = profile
        super(QuestionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        question = super(QuestionForm, self).save(commit=False)
        question.author = self.profile

        if commit:
            question.save()
            for tag in self.cleaned_data['tags'].split(' '):
                try:
                    tag_id = Tag.objects.get(name=tag).id
                except Tag.DoesNotExist:
                    tag_id = Tag.objects.create(name=tag).id
                question.tags.add(tag_id)
        return question


class CommentQuestionForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea()
        }

    def __init__(self, profile, question, *args, **kwargs):
        self.profile = profile
        self.question = question
        super(CommentQuestionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super(CommentQuestionForm, self).save(commit=False)
        answer.author = self.profile
        answer.question = self.question
        if commit:
            answer.save()
        return answer


class CorrectForm(forms.Form):
    answer_id = forms.IntegerField()
    checked = forms.BooleanField(required=False)

    def save(self):
        answer = Answer.objects.get(id=self.cleaned_data['answer_id'])
        answer.is_correct = self.cleaned_data['checked']
        answer.save()
        return answer


class VoteQuestionForm(forms.ModelForm):
    class Meta:
        model = QuestionLike
        fields = ['user', 'question', 'is_liked']

    def __init__(self, action, *args, **kwargs):
        self.action = action
        super(VoteQuestionForm, self).__init__(*args, **kwargs)

    def save(self, commit=False):
        vote = super(VoteQuestionForm, self).save(commit=False)
        qid = self.cleaned_data['question'].id

        try:
            like_id = QuestionLike.objects.get(user_id=self.cleaned_data['user'].id, question_id=qid)
        except QuestionLike.DoesNotExist:
            print('create')
            vote = QuestionLike.objects.create(user_id=self.cleaned_data['user'].id,
                                               question_id=qid,
                                               is_liked=self.cleaned_data['is_liked'])
            if self.cleaned_data['is_liked']:
                count = 1
            else:
                count = -1
            self.action = 'done'

        if self.action == 'create' and like_id.is_liked == self.cleaned_data['is_liked']:
            self.action = 'delete'

        if self.action == 'create' and like_id.is_liked != self.cleaned_data['is_liked']:
            self.action = 'update'

        if self.action == 'update':
            print('update')
            vote = QuestionLike.objects.get(user_id=self.cleaned_data['user'].id,
                                            question_id=qid)
            vote.is_liked = self.cleaned_data['is_liked']
            vote.save()

            if self.cleaned_data['is_liked']:
                count = 2
            else:
                count = -2
        elif self.action == 'delete':
            print('delete')
            vote = QuestionLike.objects.filter(user_id=self.cleaned_data['user'].id,
                                               question_id=qid).delete()
            if self.cleaned_data['is_liked']:
                count = -1
            else:
                count = 1
        Question.objects.filter(id=qid).update(rating=F('rating') + count)

        if commit:
            vote.save()

        return vote


class VoteAnswerForm(forms.ModelForm):
    class Meta:
        model = AnswerLike
        fields = ['user', 'answer', 'is_liked']

    def __init__(self, action, *args, **kwargs):
        self.action = action
        super(VoteAnswerForm, self).__init__(*args, **kwargs)

    def save(self, commit=False):
        vote = super(VoteAnswerForm, self).save(commit=False)
        aid = self.cleaned_data['answer'].id

        try:
            like_id = AnswerLike.objects.get(user_id=self.cleaned_data['user'].id, answer_id=aid)
        except AnswerLike.DoesNotExist:
            print('create')
            vote = AnswerLike.objects.create(user_id=self.cleaned_data['user'].id,
                                             answer_id=aid,
                                             is_liked=self.cleaned_data['is_liked'])
            if self.cleaned_data['is_liked']:
                count = 1
            else:
                count = -1
            self.action = 'done'

        if self.action == 'create' and like_id.is_liked == self.cleaned_data['is_liked']:
            self.action = 'delete'

        if self.action == 'create' and like_id.is_liked != self.cleaned_data['is_liked']:
            self.action = 'update'

        if self.action == 'update':
            print('update')
            vote = AnswerLike.objects.get(user_id=self.cleaned_data['user'].id,
                                          answer_id=aid)
            vote.is_liked = self.cleaned_data['is_liked']
            vote.save()

            if self.cleaned_data['is_liked']:
                count = 2
            else:
                count = -2
        elif self.action == 'delete':
            print('delete')
            vote = AnswerLike.objects.filter(user_id=self.cleaned_data['user'].id,
                                             answer_id=aid).delete()
            if self.cleaned_data['is_liked']:
                count = -1
            else:
                count = 1
        Answer.objects.filter(id=aid).update(rating=F('rating') + count)

        if commit:
            vote.save()

        return vote
