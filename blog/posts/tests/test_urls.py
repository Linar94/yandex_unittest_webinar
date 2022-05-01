"""
    Необходимо проверить следующее:
    - статус коды возвращаемые от публичных урлов
    - проверить доступ неавторизованного пользователя до приватных урлов
    - проверить доступ авторизованного пользователя до приватных урлов
"""


from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем тестового пользователя
        cls.user = User.objects.create_user(username='auth_user')
        # создаем тестовую группу
        cls.group = Group.objects.create(
            title='test title',
            description='Test description',
            slug='test-slug'
        )
        # создаем тестовый пост
        cls.post = Post.objects.create(
            text='Test text', author=cls.user, group=cls.group
        )
        # готовим урлы
        cls.new_post_url = f'/post/new/'
        cls.edit_group_url = f'/group/{cls.group.pk}/edit/'

        cls.public_urls = ('/', 'index.html'),
        cls.private_urls = (
            (cls.new_post_url, 'new_post.html'),
            (cls.edit_group_url, 'group_edit.html')
        )

    def setUp(self):
        """Создаем клиента и авторизуем пользователя"""
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_public_urls_work(self):
        """Тест, проверяющий работу публичных урлов, проверяем статус код"""
        for url, _ in PostsURLTests.public_urls:
            with self.subTest(url=url):
                response = self.unauthorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_cannot_access_private_urls(self):
        """Тест, проверяющий доступ к закрытым урлам для неавторизованного пользователя"""
        login_url = reverse('login')

        for url, _ in PostsURLTests.private_urls:
            with self.subTest(url=url):
                target_url = f'{login_url}?next={url}'
                response = self.unauthorized_client.get(url)
                self.assertRedirects(response, target_url)

    def test_authenticated_author_can_access_private_urls(self):
        """Тест, проверяющий доступ к закрытым урлам для авторизованного пользователя """
        for url, _ in PostsURLTests.private_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
