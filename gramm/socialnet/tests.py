from django.test import TestCase, Client
from django.urls import reverse
from .models import Account, Post, Following
from posts.models import Tag, PostTags, Comments, Upvote


class BasicTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.f_user = Account.objects.create(id=1,
                                             first_name="first",
                                             last_name="FIRST",
                                             username="first_username",
                                             email="fff@111.com",
                                             password="password1",
                                             bio="first_bio")
        self.l_user = Account.objects.create(id=2,
                                             first_name="last",
                                             last_name="LAST",
                                             username="last_username",
                                             email="lll@222.com",
                                             password="password2",
                                             bio="last_bio")
        self.post = Post.objects.create(id=1,
                                        author=self.f_user,
                                        title="Cool title",
                                        description="Some cool description")
        self.tag = Tag.objects.create(name="tag")
        self.post_tag = PostTags.objects.create(post=self.post, tag=self.tag)
        self.comments = Comments.objects.create(author=self.l_user,
                                                post=self.post,
                                                body="comment")
        self.upvote = Upvote.objects.create(account=self.l_user, post=self.post)
        self.follow = Following.objects.create(user=self.f_user, follow=self.l_user)

    def test_user(self):
        self.assertEqual(Account.objects.count(), 2)


class ModelTestCase(BasicTestCase):

    def test_models(self):
        user = Account.objects.get(username="first_username")
        self.assertEqual(user.first_name, "first")
        self.assertEqual(user.last_name, "FIRST")
        self.assertEqual(user.username, "first_username")
        self.assertEqual(user.email, "fff@111.com")
        self.assertEqual(user.bio, "first_bio")

        post = Post.objects.get(author=user)
        self.assertEqual(post.title, "Cool title")
        self.assertEqual(post.description, "Some cool description")

        tag = PostTags.objects.get(post=post)
        self.assertEqual(tag.tag.name, "tag")

        comment = Comments.objects.get(post=post)
        self.assertEqual(comment.body, "comment")

        self.assertEqual(Upvote.objects.filter(post=post).count(), 1)

        self.assertEqual(Following.objects.filter(user=user).count(), 1)


class ViewTestCase(BasicTestCase):

    def test_register_user(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("register"), {"email": "email@email.com"})
        self.assertRedirects(response, reverse('update_user_info'))

        response = self.client.get(reverse("update_user_info"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("update_user_info"),
                                        {
                                            "first_name": "f",
                                            "last_name": "l",
                                            "username": "username123",
                                            "password": "13645687",
                                            "bio": "bio"
                                         })
        self.assertRedirects(response, reverse("main"))

        user = Account.objects.get(username="username123")
        self.assertEqual(user.first_name, "f")
        self.assertEqual(user.last_name, "l")
        self.assertEqual(user.username, "username123")
        self.assertEqual(user.bio, "bio")
        self.client.logout()

    def test_login_user(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("login"), {"email": "fff@111.com", "password": "password1"}, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.f_user.is_authenticated)
        response = self.client.get(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_user_follow(self):
        self.client.force_login(user=self.l_user)
        response = self.client.get(reverse("follow_post"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Some cool description")

        response = self.client.post(reverse("following", kwargs={"profile_id": 1}), follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("follow_post"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "oops, there still empty")
