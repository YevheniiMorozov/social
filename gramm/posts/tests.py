from django.urls import reverse
from .models import Post, PostTags, Upvote
from socialnet.tests import BasicTestCase


class PostTestCase(BasicTestCase):

    def test_main(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cool title")

    def test_anon_user(self):
        response = self.client.get((reverse("follow_post")))
        self.assertEqual(response.status_code, 302)

    def test_view_post(self):
        self.client.force_login(user=self.l_user)
        response = self.client.get(reverse("view_post", kwargs={"post_id": 1}))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Cool title")
        self.assertContains(response, "Some cool description")

        response = self.client.post(reverse("upvote_post", kwargs={"post_id": 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Upvote.objects.filter(post__id=1).count(), 0)

        response = self.client.post(reverse("view_post", kwargs={"post_id": 1}), {"body": "Cool comment"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cool comment")

        self.client.logout()

    def test_post_create(self):
        self.client.force_login(user=self.l_user)
        response = self.client.get(reverse("create_post"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("create_post"),
                                    {"title": "title1", "description": "desc1", "name": "test_tag"}, follow=True)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(title="title1")
        post_tag = PostTags.objects.get(post=post)
        self.assertEqual(post_tag.tag.name, "test_tag")
        self.client.logout()

