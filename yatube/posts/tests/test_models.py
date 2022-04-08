from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()
LIMIT_SIMBOLS = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Класс для тестирования моедели Post."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:LIMIT_SIMBOLS])

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)
