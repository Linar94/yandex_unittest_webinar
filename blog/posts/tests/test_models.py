"""
    Необходимо проверить следующее:
    - проверить help_text
    - проверить __str__
    - проверить валидаторы
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем тестового пользователя
        cls.user = User.objects.create_user(username='test_user')
        # создаем тестовый пост
        cls.post = Post.objects.create(
            text='text', author=cls.user
        )
        # создаем тестовую группу
        cls.group = Group.objects.create(
            title='Test title',
            description='Test description',
            slug='test-slug'
        )

    def test_post_help_text(self):
        """Тест, проверяющий атрибут поля help_text"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу поста',
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text, expected)

    def test_group_object_name_is_title_field(self):
        """Тест, проверяющий метод __str__"""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)

    def test_post_validators(self):
        """Тест, проверяющий максимальную длинну поста"""
        post = PostModelTest.post
        self.assertEqual(post._meta.get_field("text").validators[0].limit_value, 50)

    def test_validation_fail(self):
        """Тест, проверяющий работу валидатора поста"""
        post_invalid = Post.objects.create(text='text'*20, author=PostModelTest.user)
        with self.assertRaises(ValidationError):
            post_invalid.full_clean()
            post_invalid.save()
