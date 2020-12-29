from django.core.cache import cache
from django.core.management.base import BaseCommand
from AskNakaznoy.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        rating = Tag.objects.best()
        cache.set('best_tags', rating[:10], 86400 + 3600)
        authors = Profile.objects.best(Question.objects.best())
        cache.set('best_users', authors[:20], 86400 + 3600)
