

# Create your tests here.

from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, 'blog')

        navbar = soup.find('nav', id="navbar")
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('no sentence', soup.body.text)

        post_000 = Post.objects.create(
            title='The first post',
            content='the the',
            created=timezone.now(),
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)



        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('no sentence', body.text)
        self.assertIn(post_000.title, body.text)




