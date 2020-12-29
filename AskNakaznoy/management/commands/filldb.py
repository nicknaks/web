from math import ceil
from random import choice, choices

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from AskNakaznoy.models import *

from faker import Faker

faker = Faker('en_US')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', type=int)
        parser.add_argument('-t', '--tags', type=int)
        parser.add_argument('-q', '--questions', type=int)
        parser.add_argument('-a', '--answers', type=int)
        parser.add_argument('-l', '--likes', type=int)

    def handle(self, *args, **options):
        count_users = options['users']
        count_questions = options['questions']
        count_answers = options['answers']
        count_tags = options['tags']
        count_likes = options['likes']

        if count_tags:
            self.fill_tags(count_tags)
        if count_users:
            self.fill_users(count_users)
        if count_questions:
            self.fill_questions(count_questions)
        if count_answers:
            self.fill_answers(count_answers)
        if count_likes:
            self.fill_likes(count_likes)

    def fill_questions(self, count):
        all_users = list(Profile.objects.values_list('id', flat=True))
        all_tags = list(Tag.objects.values_list('id', flat=True))
        for i in range(count):
            author_id = faker.random.randint(0, len(all_users) - 1)
            question = Question(author_id=all_users[author_id],
                                title=faker.sentence(),
                                text=faker.text(),
                                published_date=faker.date_between('-100d', 'today'))
            question.save()
            tags_amount = faker.random.randint(1, 4)
            for j in range(tags_amount):
                tag_id = faker.random.randint(0, len(all_tags) - 1)
                question.tags.add(all_tags[tag_id])
            question.save()

    def fill_users(self, count):
        usernames = set()
        users = []
        profiles = []

        while len(usernames) != count:
            usernames.add(faker.user_name() + str(faker.random.randint(0, 1000000)))

        for name in usernames:
            user = User(username=name, password=faker.password(), email=faker.email())
            users.append(user)
            profile = Profile(user=user, nickname=faker.name())
            profiles.append(profile)

        self.bulk_create(count, profiles, Profile)
        self.bulk_create(count, users, User)

    def fill_tags(self, count):
        db_tags = []
        while len(db_tags) != count:
            db_tags.append(Tag(name=faker.word() + str(faker.random.randint(0, 100000))))

        self.bulk_create(count, db_tags, Tag)

    def fill_answers(self, count):
        all_users = list(Profile.objects.values_list('id', flat=True))
        all_questions = list(Question.objects.values_list('id', flat=True))
        answers = []

        for i in range(count):
            author_id = faker.random.randint(0, len(all_users) - 1)
            question_id = faker.random.randint(0, len(all_questions) - 1)
            answer = Answer(author_id=author_id, question_id=question_id, text=faker.text())
            answers.append(answer)

        self.bulk_create(count, answers, Answer)

    def fill_likes(self, count):
        all_users = list(Profile.objects.values_list('id', flat=True))
        all_questions = list(Question.objects.values_list('id', flat=True))
        all_answers = list(Answer.objects.values_list('id', flat=True))

        questions_likes_amount = round(count / 2)
        answers_likes_amount = count - questions_likes_amount
        question_likes = []
        for i in range(questions_likes_amount):
            author_id = faker.random.randint(0, len(all_users) - 1)
            question_id = faker.random.randint(0, len(all_questions) - 1)
            question_likes.append(QuestionLike(user_id=author_id,
                                               question_id=question_id,
                                               is_liked=faker.random.randint(0, 1)))
        self.bulk_create(questions_likes_amount, question_likes, QuestionLike)

        answers_likes = []
        for i in range(answers_likes_amount):
            author_id = faker.random.randint(0, len(all_users) - 1)
            answer_id = faker.random.randint(0, len(all_answers) - 1)
            answers_likes.append(AnswerLike(user_id=author_id,
                                            answer_id=answer_id,
                                            is_liked=faker.random.randint(0, 1)))

        self.bulk_create(answers_likes_amount, answers_likes, AnswerLike)

    def bulk_create(self, count, data, model_type):
        if count > 500:
            count_batch = ceil(count / 500)
            for i in range(count_batch):
                one_batch = slice(data, 500)
                model_type.objects.bulk_create(one_batch)
                print("ADD 500 ")
        else:
            model_type.objects.bulk_create(data)
            print("ADD " + str(count))
