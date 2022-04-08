from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='neo')
        cls.author = User.objects.create_user(username='auth')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'

        )
        cls.post = Post.objects.create(
            text='test_text',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.force_login(self.author)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_test_slug_url_exists_at_desired_location(self):
        """Страница '/group/test_slug/' доступна любому пользователю."""
        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_test_slug_url_exists_at_desired_location(self):
        """Страница '/profile/neo/' доступна любому пользователю."""
        response = self.guest_client.get('/profile/neo/')
        self.assertEqual(response.status_code, 200)

    def test_profile_test_slug_url_exists_at_desired_location(self):
        """Страница  '/posts/1/' доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /posts/1/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/')

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_profile_test_slug_url_exists_at_desired_location(self):
        """Страница  '/unexisting_page/' доступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_correct_template(self):
        templates_url_name = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/neo/',
            'posts/post_detail.html': '/posts/1/',
            'posts/post_create.html': '/posts/1/edit/',
            'posts/post_create.html': '/create/', }

        for template, address in templates_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
