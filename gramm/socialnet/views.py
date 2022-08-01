from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from .forms import UserLoginForm, AccountRegisterForm, ImageForm, ChangeUserInfoForm
from posts.models import Post
from .models import Account, Avatar, Following, Image, UpvotePhoto, DownvotePhoto, History
from social_django.models import UserSocialAuth

import trafaret as tr
from trafaret import DataError

LOGIN_URL = "login"


def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("main")
    else:
        form = UserLoginForm()
    return render(request, "login.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("login")


def register_user(request):
    if request.method == "POST":
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('change_info')
        else:
            messages.error(request, "This mail box is already register or password are too short")
            return redirect("register")
    else:
        form = AccountRegisterForm()
        return render(request, "register.html", {"form": form})


@login_required
def change_user_info(request):
    if request.method == "POST":
        form = ChangeUserInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            Account.objects.filter(email=request.user.email).update(
                first_name=form.instance.first_name,
                last_name=form.instance.last_name,
                bio=form.instance.bio,
            )
            login(request, Account.objects.get(email=request.user.email),
                  backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Success!")
            return redirect("profile", user_id=request.user.id)
        else:
            messages.error(request, "Invalid data, please try again")
            return redirect("change_info")
    else:
        user = request.user
        try:
            github_login = user.social_auth.get(provider='github')
        except UserSocialAuth.DoesNotExist:
            github_login = None
        can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
        form = ChangeUserInfoForm()
        return render(request, "change_info.html", {"form": form,
                                                    'github_login': github_login,
                                                    'can_disconnect': can_disconnect})


@login_required
def change_password(request):
    if request.user.has_usable_password():
        pass_form = PasswordChangeForm
    else:
        pass_form = AdminPasswordChangeForm
    if request.method == "POST":
        form = pass_form(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("main")
        else:
            messages.error(request, "Invalid data, please try again")
            return redirect("change_password")
    else:
        form = pass_form(user=request.user)
        return render(request, "pass.html", {"form": form})


class ViewProfile(LoginRequiredMixin, DetailView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    template_name = "profile.html"
    context_object_name = "profile"

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        try:
            tr.Int().check(user_id)
        except DataError:
            raise Http404("Invalid data")
        try:
            account = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            raise Http404("User does not exist")
        return account

    def get_context_data(self, *args, **kwargs):
        context = super(ViewProfile, self).get_context_data(**kwargs)
        user_id = self.kwargs.get("user_id")
        if not (user_id and Account.objects.filter(id=user_id).exists()):
            raise Http404("Invalid data")
        try:
            tr.Int().check(user_id)
        except DataError:
            raise Http404("Invalid data")
        context["post"] = Post.objects.filter(author__id=user_id).all()
        context["all_images"] = Avatar.objects.filter(account__id=user_id).select_related("image").all()
        context['img'] = context['all_images'][0] if context['all_images'] else None
        context["follower"] = Following.objects.filter(user__id=user_id).all()
        context["follow"] = Following.objects.filter(user__id=user_id, follow__id=self.request.user.id).first()
        return context


class ViewPhoto(LoginRequiredMixin, DetailView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    template_name = "view_photo.html"
    context_object_name = "photo"

    def get_object(self):
        image_id = self.kwargs.get("image_id")
        try:
            tr.Int().check(image_id)
        except DataError:
            raise Http404("Invalid data")
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            raise Http404("Image does not exist")
        return image

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ViewPhoto, self).get_context_data(**kwargs)
        image_id = self.kwargs.get("image_id")
        if not (image_id and Image.objects.filter(id=image_id).exists()):
            raise Http404("Invalid data")
        try:
            tr.Int().check(image_id)
        except DataError:
            raise Http404("Invalid data")
        context["upvotes"] = UpvotePhoto.objects.filter(photo__id=image_id).all()
        context["downvotes"] = DownvotePhoto.objects.filter(photo__id=image_id).all()
        context["upvote"] = UpvotePhoto.objects.filter(user__id=self.request.user.id, photo__id=image_id).first()
        context["downvote"] = DownvotePhoto.objects.filter(user__id=self.request.user.id, photo__id=image_id).first()
        return context


@login_required
def add_avatar(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form.instance.account.add(request.user)
            return redirect("profile", request.user.id)
        else:
            messages.error(request, "File must be image and < 10mb")
            return redirect("add_avatar")
    else:
        form = ImageForm()
        return render(request, "add_avatar.html", {"form": form})


class FollowerList(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    paginate_by = 4
    model = Following
    template_name = "profile_list.html"
    context_object_name = "profiles"
    allow_empty = True

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        try:
            tr.Int().check(user_id)
        except DataError:
            raise Http404("Invalid data")
        if not (user_id and Account.objects.filter(id=user_id).exists()):
            raise Http404("Invalid data")
        return Following.objects.filter(user__id=user_id).all()


@login_required
def follow_unfollow(request, profile_id):
    if request.method == "POST":
        if not Account.objects.filter(id=profile_id).exists():
            raise Http404("User does not exist")
        deleted = Following.objects.filter(user_id=profile_id, follow_id=request.user.id).delete()
        if deleted[0] == 0:
            follow = Following.objects.create(user_id=profile_id, follow_id=request.user.id)
            if not History.objects.filter(account_id=profile_id, follow=follow).exists():
                History.objects.create(account_id=profile_id, follow_id=follow.id)
        return redirect("profile", user_id=profile_id)


@login_required
def upvote_photo(request, image_id):
    if request.method == "POST":
        if not Image.objects.filter(id=image_id).exists():
            raise Http404("Image does not exist")
        deleted = UpvotePhoto.objects.filter(user_id=request.user.id, photo_id=image_id).delete()
        avatar = Avatar.objects.filter(image_id=image_id).select_related("account").first()
        # deleted return tuple (int, {})
        if deleted[0] == 0:
            u = UpvotePhoto.objects.create(user_id=request.user.id, photo_id=image_id)
            if not History.objects.filter(account=avatar.account, upvote_photo=u).exists():
                History.objects.create(account=avatar.account, upvote_photo=u)
            if DownvotePhoto.objects.filter(user_id=request.user.id, photo_id=image_id).exists():
                DownvotePhoto.objects.filter(user_id=request.user.id, photo_id=image_id).delete()
        return redirect("view_photo", image_id=image_id)


@login_required
def downvote_photo(request, image_id):
    if request.method == "POST":
        if not Image.objects.filter(id=image_id).exists():
            raise Http404("Image does not exist")
        deleted = DownvotePhoto.objects.filter(user_id=request.user.id, photo_id=image_id).delete()
        if deleted[0] == 0:
            DownvotePhoto.objects.create(user_id=request.user.id, photo_id=image_id)
            if UpvotePhoto.objects.filter(user_id=request.user.id, photo_id=image_id).exists():
                UpvotePhoto.objects.filter(user_id=request.user.id, photo_id=image_id).delete()
        return redirect("view_photo", image_id=image_id)


class ViewHistory(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    redirect_field_name = "login"
    model = History
    template_name = "history.html"
    allow_empty = True

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        try:
            tr.Int().check(user_id)
        except DataError:
            raise Http404("Invalid data")
        if not user_id or user_id != self.request.user.id:
            raise Http404("Page does not exist or you don`t have permission to view it")
        history = History.objects.filter(
            account_id=user_id).select_related("upvote_post", "upvote_photo", "follow").all()[:100]
        return history
