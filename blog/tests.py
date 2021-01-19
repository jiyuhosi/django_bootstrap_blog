

# Create your tests here.

from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category ,Tag
from django.utils import timezone
from django.contrib.auth.models import User


def create_post(title, content, author,category=None):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category,
    )
    return  blog_post

def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description,
    )

    category.slug = category.name.replace('','-').replace('/','')
    category.save()

    return category


def create_tag(name='some_tag'):
    tag, is_created = Tag.objects.get_or_create(
        name=name
    )
    tag.slug = tag.name.replace('','-').replace('/','')
    tag.save()

    return tag


class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def text_category(self):
        category = create_category()

    def test_tag(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )

        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title='i can do it',
            content='story of me',
            author=self.author_000,
        )

        post_001.tags.add(tag_001)
        post_001.save()


        # post have 2 more tags
        self.assertEqual(post_000.tags.count(), 2)
        self.assertEqual(tag_001.post_set.count(), 2)  # tag have 2 more post
        self.assertEqual(tag_001.post_set.first(), post_000)
        self.assertEqual(tag_001.post_set.last(), post_001)







    def test_post(self):
        category = create_category()

        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
            category=category
        )

        self.assertEqual(category.post_set.count(),1)





class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def check_navbar(self,soup):
        navbar = soup.find('nav', id="navbar")
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def check_right_side(self, soup):
        #category
        category_card = soup.find('div', id='category-card')

        self.assertIn('unclassified (1)', category_card.text)
        self.assertIn('political/society (1)', category_card.text)


    def test_post_list_no_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, 'Blog')

        self.check_navbar(soup)

        # navbar = soup.find('nav', id="navbar")
        # self.assertIn('Blog', navbar.text)
        # self.assertIn('About me', navbar.text)

        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('no sentence', soup.body.text)

    def test_post_list_with_post(self):
        tag_america =create_tag(name='america')

        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )

        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,
            category=create_category(name='political/society'),
        )
        post_001.tags.add(tag_america)
        post_001.save()

        self.assertGreater(Post.objects.count(), 0)



        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('no sentence', body.text)
        self.assertIn(post_000.title, body.text)

        post_000_read_more_btn = body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_btn['href'],post_000.get_absolute_url())

        self.check_right_side(soup)

        # main
        main_div = soup.find('div', id='main-div')
        self.assertIn('unclassified', main_div.text)
        self.assertIn('political/society', main_div.text)

        # Tag
        post_card_000 = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#america',post_card_000.text)

    def test_post_detail(self):
        tag_america =create_tag(name='america')
        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )
        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,
            category=create_category(name='political/society'),
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))

        self.check_navbar(soup)

        body = soup.body

        main_div = body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)

        self.assertIn(post_000.content, main_div.text)

        self.check_right_side(soup)

        # Tag
        self.assertIn('#america',main_div.text)

    def test_post_list_by_category(self):
        category_politics = create_category(name='political/society')

        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,
            category=category_politics,
        )

        response = self.client.get(category_politics.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual('Blog - {}'.format(category_politics.name),soup.title.text)

        main_div = soup.find('div', id='main-div')
        self.assertNotIn('unclassified', main_div.text)
        self.assertIn(category_politics.name, main_div.text)

    def test_post_list_no_category(self):
        category_politics = create_category(name='political/society')

        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,
            category=category_politics,
        )

        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual('Blog - {}'.format(category_politics.name),soup.title.text)

        main_div = soup.find('div', id='main-div')
        self.assertIn('unclassified', main_div.text)
        self.assertNotIn(category_politics.name, main_div.text)








