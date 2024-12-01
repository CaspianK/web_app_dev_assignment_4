from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Post, Comment

class BlogAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')

        self.user_token = Token.objects.create(user=self.user)
        self.other_user_token = Token.objects.create(user=self.other_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)

        self.post = Post.objects.create(title="Test Post", content="Test Content", author=self.user)
        self.comment = Comment.objects.create(post=self.post, content="Test Comment", author=self.user)

    def test_signup(self):
        data = {"username": "newuser", "password": "securepassword", "email": "email@test.com"}
        response = self.client.post('/signup/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        data = {"username": "testuser", "password": "password"}
        response = self.client.post('/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_post(self):
        data = {"title": "New Post", "content": "New Content"}
        response = self.client.post('/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Post")

    def test_create_post_unauthorized(self):
        self.client.credentials()
        data = {"title": "Unauthorized Post", "content": "No token"}
        response = self.client.post('/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_posts(self):
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_post_by_id(self):
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.post.id)
        self.assertEqual(response.data['title'], self.post.title)

    def test_update_post(self):
        data = {"title": "Updated Title", "content": "Updated Content"}
        response = self.client.put(f'/posts/{self.post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_update_post_unauthorized(self):
        self.client.credentials()
        data = {"title": "Unauthorized Update", "content": "No token"}
        response = self.client.put(f'/posts/{self.post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_author_cannot_update_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_user_token.key)
        data = {"title": "Hacked Title", "content": "Hacked Content"}
        response = self.client.put(f'/posts/{self.post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        response = self.client.delete(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_unauthorized(self):
        self.client.credentials() 
        response = self.client.delete(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_author_cannot_delete_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_user_token.key)
        response = self.client.delete(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment(self):
        data = {"post": self.post.id, "content": "New Comment"}
        response = self.client.post('/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "New Comment")

    def test_create_comment_unauthorized(self):
        self.client.credentials()
        data = {"post": self.post.id, "content": "Unauthorized Comment"}
        response = self.client.post('/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_comments(self):
        response = self.client.get('/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_comment_by_id(self):
        response = self.client.get(f'/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.comment.id)
        self.assertEqual(response.data['content'], self.comment.content)

    def test_update_comment(self):
        data = {"post": self.post.id, "content": "Updated Comment"}
        response = self.client.put(f'/comments/{self.comment.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated Comment")

    def test_update_comment_unauthorized(self):
        self.client.credentials() 
        data = {"content": "Unauthorized Update"}
        response = self.client.put(f'/comments/{self.comment.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_author_cannot_update_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_user_token.key)
        data = {"content": "Hacked Comment"}
        response = self.client.put(f'/comments/{self.comment.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment(self):
        response = self.client.delete(f'/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthorized(self):
        self.client.credentials()
        response = self.client.delete(f'/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_author_cannot_delete_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_user_token.key)
        response = self.client.delete(f'/comments/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)