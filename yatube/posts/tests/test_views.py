from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

POSTS_PER_PAGE_3 = 3


class PagesTests(TestCase):
    """Класс тестов для паджинатор."""

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='leo')
        super().setUpClass()
        cls.group = Group.objects.create(title='test_group',
                                         slug='test_slug',
                                         description='test_description')
        cls.group_test = Group.objects.create(title='test_group_test1',
                                              slug='test_slug1',
                                              description='test_description1')
        cls.post = Post.objects.create(text='test_text',
                                       author=cls.user,
                                       group=cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }

        for addres, template, in templates_pages_name.items():
            with self.subTest(addres=addres):
                response = self.authorized_client.get(addres)
                self.assertTemplateUsed(response, template)

    def test_home_page_correct_context(self):
        """Проверка списка постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        test_obj = response.context['page_obj'][0]
        self.assertEqual(test_obj, self.post)
              
    def test_group_list_page_correct_context(self):
        """Проверка списка постов отфильтрованных по группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.user.slug}))
        first_object = response.context['page_obj'][0]
        test_title = first_object.group.title
        test_text = first_object.text
        test_descripton = first_object.group.description
        test_group = first_object.group
        test_author = first_object.author
        self.assertEqual(first_object, self.post)
        self.assertEqual(test_title, 'test_group')
        self.assertEqual(test_author, self.user)
        self.assertEqual(test_text, 'test_text')
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_descripton, self.group.description)

    def test_group_list_page_correct_context(self):
        """Проверка списка постов отфильтрованных по пользователю."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        test_title = first_object.group.title
        test_text = first_object.text
        test_descripton = first_object.group.description
        test_count = first_object.author.posts.count()
        self.assertEqual(first_object, self.post)
        self.assertEqual(test_title, 'test_group')
        self.assertEqual(test_text, 'test_text')
        self.assertEqual(test_count, len(self.user.posts.all()))
        self.assertEqual(test_descripton, self.group.description)

    def test_group_list_page_id_correct_context(self):
        """Проверка одного поста отфильтрованного по id."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').text, 'test_text')
        self.assertEqual(
            response.context.get('post').author.posts.count(),
            len(self.user.posts.all()))
        self.assertEqual(response.context.get('post').author, self.user)

    def test_creat_page_correct_context(self):
        """Шаблон создания поста с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_correct_context(self):
        """Шаблон редактирования поста с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertIsInstance(response.context.get('form'), PostForm)
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context['is_edit']
        self.assertTrue('is_edit')
        self.assertIsInstance(is_edit, bool)

    def test_post_in_the_right_group(self):
        """ Проверяем что пост не попал в другую группу """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug1'}))
        self.assertEqual(len(response.context['page_obj']), 0)


class PiginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='meo')
        cls.group = Group.objects.create(title='test_group',
                                         slug='test_slug',
                                         description='test_description')
        for i in range(13):
            cls.posts = Post.objects.create(author=cls.user,
                                            text=f'{i} Text',
                                            group=cls.group)
        cls.templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username})
        ]
        cls.templates2 = [
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}) +
            '?page=2',
            reverse('posts:profile', kwargs={'username': cls.user.username}) +
            '?page=2'
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_correct(self):
        """Проверяет что на странице присутсвует 10 постов."""
        for i in range(len(self.templates)):
            with self.subTest(templates=self.templates[i]):
                response = self.authorized_client.get(self.templates[i])
                self.assertEqual(len(response.context['page_obj']),
                                 settings.POSTS_PER_PAGE)

    def test_paginator_correct_2(self):
        """Проверяет количество постов на 2ой странице -3."""
        for i in range(len(self.templates2)):
            with self.subTest(templates2=self.templates2[i]):
                response = self.authorized_client.get(self.templates2[i])
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_PER_PAGE_3)
