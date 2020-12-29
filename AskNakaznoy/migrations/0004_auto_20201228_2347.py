# Generated by Django 3.1.4 on 2020-12-28 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AskNakaznoy', '0003_auto_20201227_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerlike',
            name='is_liked',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='pizza.jpg', upload_to='avatar/%Y/%m/%d', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='is_liked',
            field=models.BooleanField(default=True),
        ),
    ]