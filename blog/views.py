from django.shortcuts import render
from .models import Post

# Create your views here.

def index(request):
    posts = Post.objects.all()
    return render(
        request,
        'blog/post_index.html',
        {
         'posts': posts,

        }
    )
