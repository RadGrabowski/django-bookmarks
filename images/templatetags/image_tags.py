from django import template
from ..models import Image
from hitcount.models import HitCount

register = template.Library()


@register.simple_tag
def total_likes(user):
    likes = 0
    for image in Image.objects.filter(user=user):
        likes += image.users_like.count()
    return likes


@register.simple_tag
def total_views(user):
    views = 0
    for image in Image.objects.filter(user=user):
        hit = HitCount.objects.get(object_pk=image.pk)
        views += hit.hits
    return views
