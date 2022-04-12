from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTest(TestCase):
    """Класс тестирования постов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='smeo')
        cls.group = Group.objects.create(title='test_group',
                                         slug='test_slug',
                                         description='test_descripton')
        cls.post = Post.objects.create(author=cls.user,
                                       group=cls.group,
                                       text='Text_3')
        cls.post_edit = Post.objects.create(author=cls.user,
                                            group=cls.group,
                                            text='Edit Text')
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_create_form_post(self):
        """Проверка создания нового поста."""
        post_count = Post.objects.count()
        form = {
            'text': self.post.text,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}))

        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
            ).exists())
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_eddit_post_success(self):
        """Проверка редактирования поста."""
        post_count = Post.objects.count()
        form = {
            'text': self.post_edit.text,
            'group': self.post_edit.group,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}), data=form)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertTrue(
            Post.objects.filter(
                text=self.post_edit.text,
                group=self.post_edit.group,
            ).exists())
        self.assertEqual(Post.objects.count(), post_count)

    def test_form_create_post_unauthorized_user(self):
        """
        Проверяем, что неавторизованный пользователь не может
        отправить запрос на создание поста
        """
        post_count = Post.objects.count()
        form = {
            'text': 'Text_3',
            'group': self.group.id,
        }
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form,
                                          follow=True)
        self.assertRedirects(response,
                             reverse('users:login') + '?next=/create/')
        self.assertEqual(Post.objects.count(), post_count)
