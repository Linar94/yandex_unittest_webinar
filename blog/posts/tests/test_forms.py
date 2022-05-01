"""
    Необходимо проверить следующее:
    - проверить создание поста
    - проверить метод clean для slug
"""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем тестового пользователя
        cls.user = User.objects.create_user(username='test_user')
        # создаем тестовую группу
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='test description'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_user_can_create_post(self):
        """Тест, проверяющий создание поста."""
        post_data = {'text': 'new post', 'group': PostFormTests.group.id}
        response = self.authorized_client.post(reverse('posts:new_post'), data=post_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        post = Post.objects.first()

        self.assertEqual(post.text, post_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostFormTests.group)

    def test_slug_filed_fail(self):
        """Тест, проверяющий работу метода clean для поля slug."""
        group_data = {'title': 'new', 'slug': 'new', 'description': 'new description'}
        response = self.authorized_client.post(reverse('posts:group_new_url'), data=group_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Group.objects.count(), 1)
        self.assertIsNotNone(response.context["form"].errors)

    def test_unauthorized_user_cant_create_post(self):
        """Тест, проверяющий создание поста неавторизованным пользователем."""
        count = Post.objects.count()
        response = self.client.post(
            reverse('posts:new_post'),
            data={'text': 'Test post', 'group': PostFormTests.group.id},
        )
        login_url = reverse('users:login')
        new_post_url = reverse('posts:new_post')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertRedirects(response, target_url)
        self.assertEqual(Post.objects.count(), count)

    def test_authorized_user_cant_edit_group(self):
        """Тест, проверяющий редактирование группы неавторизованным пользователем."""
        group_data = {'title': 'new group', 'slug': 'new-slug', 'description': 'new description'}
        group_edit_tmpl = 'posts/group_detail.html'
        response = self.authorized_client.post(
            reverse('posts:group_edit_url', args=(PostFormTests.group.pk,)),
            data=group_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, group_edit_tmpl)
        self.assertEqual(Group.objects.first().title, group_data['title'])

    def test_not_allowed_method_main_page(self):
        response = self.authorized_client.post(reverse('posts:index'), data={"key": "value"})
        self.assertEqual(response.status_code, 405)
