from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import User


class ProfileManager(models.Manager):
    def best(self):
        return self


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    avatar = models.ImageField(default="pizza.jpg", verbose_name="Аватар", upload_to='avatar/%Y/%m/%d')
    nickname = models.CharField(max_length=64, verbose_name='Имя')
    objects = ProfileManager()

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class TagManager(models.Manager):
    def best(self):
        return self.order_by('-rating')


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name="Имя тэга", unique=True)
    rating = models.PositiveIntegerField(default=0)
    objects = TagManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"


class QuestionManager(models.Manager):
    def best(self):
        return self.order_by('-rating')

    def new(self):
        return self.order_by('-published_date')


class Question(models.Model):
    author = models.ForeignKey("Profile", on_delete=models.CASCADE)
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Основной текст')
    published_date = models.DateField(default=date.today, verbose_name='Дата публикации')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    tags = models.ManyToManyField("Tag", verbose_name='Tags', blank=True, related_name="questions")
    likes = models.ManyToManyField("Profile", through="QuestionLike", blank=True, related_name="liked_questions")
    objects = QuestionManager()

    def short_text(self):
        if len(self.text) > 130:
            return self.text[:130] + '...'
        else:
            return self.text

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class AnswerManager(models.Manager):
    def best(self, pk):
        return self.filter(question_id=pk).order_by('-rating')


class Answer(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="answers")
    text = models.TextField(verbose_name='Основной текст')
    is_correct = models.BooleanField(default=False, verbose_name='Ответ верный?')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    likes = models.ManyToManyField("Profile", through="AnswerLike", blank=True, related_name="liked_answers")
    objects = AnswerManager()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class QuestionLike(models.Model):
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE, verbose_name="questionlikes")
    is_liked = models.BooleanField(null=True)

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки на вопросе'


class AnswerLike(models.Model):
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE, verbose_name="answerlikes")
    is_liked = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки на ответе'
