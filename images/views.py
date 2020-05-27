from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from .forms import ImageCreateForm
from .models import Image
from common.decorators import ajax_required
from actions.utils import create_action
from hitcount.views import HitCountDetailView


class ImageCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'images/image/create.html'

    def post(self, **kwargs):
        form = ImageCreateForm(data=self.request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.user = self.request.user
            new_item.save()
            create_action(self.request.user, 'bookmarked image', new_item)
            messages.success(self.request, 'Image added successfully')
            return redirect(new_item.get_absolute_url())
        else:
            return HttpResponse(form)

    def get(self, request, *args, **kwargs):
        form = ImageCreateForm(data=request.GET)
        return self.render_to_response({'section': 'images', 'form': form})


class ImageDetailView(HitCountDetailView):
    model = Image
    template_name = 'images/image/detail.html'
    context_object_name = 'image'
    count_hit = True
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'images'
        return context


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'})


class ImageListView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        images = Image.objects.all().order_by('-created')
        paginator = Paginator(images, 9)
        page = request.GET.get('page')
        try:
            images = paginator.page(page)
        except PageNotAnInteger:
            images = paginator.page(1)
        except EmptyPage:
            if request.is_ajax():
                return HttpResponse('')
            images = paginator.page(paginator.num_pages)
        if request.is_ajax():
            return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})
        return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


class ImageRankingView(LoginRequiredMixin, ListView):
    template_name = 'images/image/ranking.html'
    context_object_name = 'most_viewed'

    def get_queryset(self):
        return Image.objects.order_by('-hit_count_generic__hits')[:10]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'images'
        return context
