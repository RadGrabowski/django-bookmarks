import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmarks.settings')

import django

django.setup()

from faker import Faker
from images.models import Image
from django.contrib.auth.models import User

fake = Faker()

if __name__ == '__main__':
    for user in User.objects.all():
        while Image.objects.filter(user=user).count() < 50:
            i = Image()
            i.user = user
            i.title = 'Example of a simple HTML page'
            i.url = 'http://help.websiteos.com/websiteos/htmlpage.jpg'
            i.image = 'images/2020/04/24/example-of-a-simple-html-page_jpg'
            i.save()
