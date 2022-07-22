from django.urls import path

from .views import *


urlpatterns = [
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("register/", register_user, name="register"),
    path("switch_follow/<int:profile_id>/", follow_unfollow, name="following"),
    path("profile/<int:user_id>/", ViewProfile.as_view(), name="profile"),
    path("profile/<int:user_id>/history", ViewHistory.as_view(), name="history"),
    path("profile/view_photo/<int:image_id>/", ViewPhoto.as_view(), name="view_photo"),
    path("profile/view_photo/<int:image_id>/upvote/", upvote_photo, name="upvote_photo"),
    path("profile/view_photo/<int:image_id>/downvote", downvote_photo, name="downvote_photo"),
    path("profile/<int:user_id>/followers/", FollowerList.as_view(), name="followers"),
    path("profile/change_user_info/", change_user_info, name="change_info"),
    path("profile/change_password/", change_password, name="change_password"),
    path("profile/add_avatar/", add_avatar, name="add_avatar"),
]
