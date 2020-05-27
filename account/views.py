from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, CreateView, ListView
from common.decorators import ajax_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from django.contrib import messages
from actions.utils import create_action
from actions.models import Action
from django.db.models import Q


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


class DashboardView(TemplateView, LoginRequiredMixin):
    template_name = 'account/dashboard.html'

    def get(self, request, *args, **kwargs):
        outdated_actions = Action.objects.filter(Q(verb='is following') | Q(verb='likes') | Q(verb='bookmarked image'))
        # if the target does not exist anymore (deleted account), delete the action
        for outdated_action in outdated_actions:
            if outdated_action.target is None:
                outdated_action.delete()
        actions = Action.objects.exclude(user=request.user)
        following_ids = request.user.following.values_list('id', flat=True)
        if following_ids:
            actions = actions.filter(Q(user_id__in=following_ids) | Q(target_id__isnull=True))
            actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
        else:
            actions = []
        return self.render_to_response({'section': 'dashboard', 'actions': actions})


class RegisterView(CreateView):
    template_name = 'account/register.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        Profile.objects.create(user=new_user)
        create_action(new_user, 'has created an account')
        return render(self.request, 'account/register_done.html', {'new_user': new_user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = self.get_form()
        return context


class EditView(TemplateView, LoginRequiredMixin):
    template_name = 'account/edit.html'

    def get(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return self.render_to_response({'user_form': user_form, 'profile_form': profile_form})

    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user, data=request.POST, user=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error during updating your profile')
        return self.render_to_response({'user_form': user_form, 'profile_form': profile_form})


class UserListView(LoginRequiredMixin, ListView):
    template_name = 'account/user/list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_active=True, is_superuser=False).exclude(username=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'section': 'people'})
        return context


class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'account/user/detail.html'

    def get_queryset(self):
        return get_object_or_404(User, username=self.kwargs['username'], is_active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'section': 'people', 'user': self.get_queryset()})
        return context


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
