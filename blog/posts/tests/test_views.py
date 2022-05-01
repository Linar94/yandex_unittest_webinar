"""
    Необходимо проверить следующее:
    - проверить главную страницу
    - проверить работу пагинатора
    - проверить контекс
    - проверить шаблоны
"""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm, GroupForm
from ..models import Group, Post

User = get_user_model()


class TestPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #  создаем тестовую группу
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='test description'
        )
        # создаем тестового пользователя
        cls.user = User.objects.create_user(username='test user')
        # создаем тестовый пост
        cls.post = Post.objects.create(
            text='Test post',
            author=TestPosts.user,
            group=TestPosts.group
        )
        # определяем урлы
        cls.new_post_url = ('posts:new_post', 'posts/new_post.html', None, PostForm)
        cls.new_group_url = ('posts:group_new_url', 'posts/group_new.html', None, GroupForm)
        cls.edit_group_url = ('posts:group_edit_url', 'posts/group_edit.html', None, GroupForm)
        cls.index_url = ('posts:index', 'posts/index.html', None, None)

        cls.template_list = (
            cls.index_url,
            cls.new_group_url,
            cls.new_post_url,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.unauthorized_client = Client()

        self.authorized_client.force_login(TestPosts.user)

    def test_index_page_context_is_correct(self):
        """Тест, проверяющий коннтекст из респонса."""
        response = self.client.get(reverse("posts:index"))

        self.assertIn('page', response.context)
        post = response.context['page'][0]

        self.assertEqual(post.author, TestPosts.user)
        self.assertEqual(post.pub_date, TestPosts.post.pub_date)
        self.assertEqual(post.text, TestPosts.post.text)
        self.assertEqual(post.group, TestPosts.post.group)

    def test_used_templates_is_correct(self):
        """Тест, проверяющий какие вызываются шаблоны, при вызове вьюхи."""

        for name, template, args, _ in TestPosts.template_list:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_new_post_pages_context_is_correct(self):
        """Тест, проверяющий контекст."""
        urls = (TestPosts.new_post_url, TestPosts.new_group_url)

        for name, _, args, form in urls:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], form)

    def test_paginator_in_pages_with_posts(self):
        """Тест, проверяющий работу пагинатора."""
        paginator_amount = 10
        all_posts_count = 14

        posts = [
            Post(
                text=f'test text {num}', author=TestPosts.user,
                group=TestPosts.group
            ) for num in range(1, all_posts_count)
        ]
        Post.objects.bulk_create(posts)

        pages = (
            (1, paginator_amount),
            (2, all_posts_count - paginator_amount)
        )

        for page, count in pages:
            response = self.unauthorized_client.get(reverse(TestPosts.index_url[0]), {'page': page})

            self.assertEqual(
                len(response.context.get('page').object_list), count
            )
