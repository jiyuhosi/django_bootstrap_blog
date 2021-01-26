

# Create your tests here.

from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category,Tag,Comment
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

def create_comment(post, text='a comment', author=None):
    if author is None:

        author, is_created = User.objects.get_or_create(
            username='guest',
            passsword='guestpassword'
        )

    comment = Comment.objects.create(
        post=post,
        text=text,
        author=author,
    )

    return comment

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


    # def test_comment(self):
    #
    #     post_000 = create_post(
    #         title='The first post',
    #         content='the the',
    #         author=self.author_000,
    #     )
    #
    #     self.assertEqual(Comment.objects.count(), 0)
    #
    #     comment_000 = create_comment(
    #         post=post_000,
    #         text='second comment',
    #     )
    #
    #     comment_001 = create_comment(
    #         post=post_000,
    #         text='second comment',
    #     )
    #
    #     self.assertEqual(Comment.objects.count(),2)
    #     self.assertEqual(post_000.comment_set.count(),2)





class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username='smith', password='nopassword')
        self.user_obama = User.objects.create_user(username='obama', password='nopassword')

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
        self.assertIn('No Contents', soup.body.text)

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

    def test_pagination(self):
        #small post
        for i in range(0,3):
            post = create_post(
                title='The post no. {}'.format(i),
                content='content{}'.format(i),
                author=self.author_000,
            )
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertNotIn('Older', soup.body.text)
        self.assertNotIn('Newer', soup.body.text)

        # many post
        for i in range(3, 10):
            post = create_post(
                title='The post no. {}'.format(i),
                content='content{}'.format(i),
                author=self.author_000,
            )
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertIn('Older', soup.body.text)
        self.assertIn('Newer', soup.body.text)


    def test_post_detail(self):
        tag_america =create_tag(name='america')
        category_politics = create_category(name='political/society')
        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
            category= category_politics,
        )
        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,

        )

        comment_000 = create_comment(post_000, text='a test comment', author=self.author_000)
        comment_001 = create_comment(post_000, text='a test comment', author=self.user_obama)



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

        # Comment

        comment_div = main_div.find('div', id='comment-list')
        self.assertIn(comment_000.author.username, comment_div.text)
        self.assertIn(comment_000.text, comment_div.text)

        # Tag
        self.assertIn('#america',main_div.text)

        # exist cagegory
        self.assertIn(category_politics.name, main_div.text)
        # edit 버튼이 로근이하지 않는경우 보이지 않음
        self.assertNotIn('EDIT', main_div.text)

        login_success = self.client.login(username='smith', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertEqual(post_000.author, self.author_000)
        self.assertIn('EDIT', main_div.text)

        login_success = self.client.login(username='obama', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertEqual(post_000.author, self.author_000)
        self.assertNotIn('EDIT', main_div.text)


        # comment_div = main_div.find('div', id='comment-list')
        # comment_000_div = comment_div.find('div', id='comment-id-{}'.format(comment_000.pk))
        # self.assertIn('edit', comment_000_div.text)
        # self.assertIn('delete', comment_000_div.text)
        #
        # comment_001_div = comment_div.find('div', id='comment-id-{}'.format(comment_001.pk))
        # self.assertNotIn('edit', comment_001_div.text)
        # self.assertNotIn('delete', comment_001_div.text)


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

    def test_tag_page(self):
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

        response = self.client.get(tag_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        blog_h1 = main_div.find('h1', id='blog-list-title')

        self.assertIn('#{}'.format(tag_000.name), blog_h1.text)
        self.assertIn(post_000.title,main_div.text)
        self.assertNotIn(post_001.title,main_div.text)

    def test_post_create(self):
        response = self.client.get('/blog/create/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='smith', password='nopassword')
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')




    def test_post_update(self):
        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )

        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')

        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertNotIn('Created',main_div.text)
        self.assertNotIn('Author',main_div.text)

    def test_new_comment(self):
        post_000 = create_post(
            title='The first post',
            content='the the',
            author=self.author_000,
        )
        login_success = self.client.login(username='smith', password='nopassword')
        self.assertTrue(login_success)


        response = self.client.post(
            post_000.get_absolute_url() + 'new_comment/',
            {'text': 'a test comment'},
            follow=True
        )
        self.assertEqual(response.status_code,200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title,main_div.text)
        self.assertIn('a test comment',main_div.text)

    def test_delete_comment(self):
        post_000 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,

        )

        comment_000 = create_comment(post_000, text='a test comment', author=self.user_obama)
        comment_001 = create_comment(post_000, text='a test comment', author=self.author_000)

        self.assertEqual(Comment.objects.count(),2)
        self.assertEqual(post_000.comment_set.count(),2)

        login_success = self.client.login(username='smith', password='nopassword')

        self.assertTrue(login_success)
        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow=True)
            self.assertEqual(Comment.objects.count(),2)
            self.assertEqual(post_000.comment_set.count(),2)

        login_success = self.client.login(username='obama', password='nopassword')

        response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(),1)
        self.assertEqual(post_000.comment_set.count(),1)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertNotIn('obama', main_div.text)

    def test_edit_comment(self):

        post_000 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,

            )

        comment_000 = create_comment(post_000, text='i am pr', author=self.user_obama)
        comment_001 = create_comment(post_000, text='a test comment', author=self.author_000)

        # without log in
        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))


        #login as smith

        login_success = self.client.login(username='smith', password='nopassword')
        self.assertTrue(login_success)

        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))


        #login as author the comment obama
        login_success = self.client.login(username='obama', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))
        self.assertEqual(response.status_code,200)

        # soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertin('Edit Comment: ', soup.body.h3)
        #
        # response = self.client.post(
        #     '/blog/edit_comment/{}/'.format(comment_000.pk),
        #     {'text: I was pr'},
        #     follow=True
        #
        # )
        #
        # self.assertEqual(response.status_code, 200)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertNotIn('I am pr', soup.body.text)
        # self.assertIn('I was pr', soup.body.text)
        #
    def test_search(self):
        post_000 = create_post(
            title='The first post',
            content='first first',
            author=self.author_000,
            )
        post_001 = create_post(
            title='The second post',
            content='second second',
            author=self.author_000,
            )

        response = self.client.get('/blog/search/the first post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(post_000.title, soup.body.text)
        self.assertNotIn(post_001.title, soup.body.text)

        response = self.client.get('/blog/search/The second post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(post_001.title, soup.body.text)
        self.assertNotIn(post_000.title, soup.body.text)





















