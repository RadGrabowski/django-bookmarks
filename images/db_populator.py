import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmarks.settings')

import django
from bookmarks import settings
import sqlite3

django.setup()

from faker import Faker
import random
from images.models import Image
from time import sleep
from account.models import Profile, Contact
from actions.utils import create_action
from django.contrib.auth.models import User
from hitcount.models import HitCount

fake = Faker()

if __name__ == '__main__':
    # for _ in range(20):
    #     try:
    #         fake = Faker()
    #         user = User()
    #         full_name = fake.name()
    #         user.username = full_name.split()[0].lower()
    #         user.first_name = full_name.split()[0]
    #         user.last_name = full_name.split()[1]
    #         user.email = full_name.split()[0].lower() + '@gmail.com'
    #         user.set_password('django1234')
    #         user.save()
    #     except sqlite3.IntegrityError:
    #         continue

    # for user in User.objects.all().exclude(is_superuser=True):
    #     profile = Profile()
    #     profile.user = user
    #     profile.date_of_birth = fake.date()
    #     profile.save()

    # for user in User.objects.filter(is_superuser=False):
    #     others = list(User.objects.filter(is_superuser=False).exclude(username=user.username))
    #     random.shuffle(others)
    #     for _ in range(random.randint(0, len(others) + 1)):
    #         contact = Contact()
    #         contact.user_from = user
    #         contact.user_to = others.pop()
    #         create_action(contact.user_from, 'is following', contact.user_to)
    #         contact.save()
    #         sleep(5)

    for user in User.objects.filter(is_superuser=False):
        for i in range(random.randint(1, 5)):
            others = list(user.followers.values_list('id', flat=True))
            random.shuffle(others)
            image = Image()
            image.user = user
            desc = fake.text()
            image.title = ' '.join(desc.split()[:2])
            image.description = desc
            image.image = random.choice(os.listdir(settings.BASE_DIR + '\\media\\')[:-3])
            image.url = fake.url()
            image.save()
            hit = HitCount(content_object=image, object_pk=image.pk)
            hit.hits = 0
            create_action(user, 'bookmarked image', image)
            sleep(5)

            for _ in range(random.randint(0, len(others))):
                like_by = others.pop()
                image.users_like.add(like_by)
                image.save()
                create_action(User.objects.get(pk=like_by), 'likes', image)
                sleep(1)

            for _ in range(random.randint(image.users_like.count(), user.followers.count()) + 1):
                hit.hits += 1
            hit.save()
            sleep(1)
