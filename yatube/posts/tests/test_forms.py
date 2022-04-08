from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='smeo')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user=cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_descripton'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Text_3'
        )
        cls.form = PostForm()

    def test_create_form_post(self):
        """Проверка создания нового поста."""
        post_count = Post.objects.count()
        form = {
            'text': 'Text_3',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))

        self.assertTrue(
            Post.objects.filter(
                text='Text_3',
                group=self.group.pk,
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_eddit_post_success(self):
        """Проверка редактирования поста."""
        self.url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        new_text = 'new_text'
        data = dict(
            text=new_text,
        )
        response = self.authorized_client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.post.refresh_from_db()
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertTrue(
            Post.objects.filter(
                text='new_text',
            ).exists())
