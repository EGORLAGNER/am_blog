from django.http import Http404
from django.shortcuts import render

from blog.models import Post


def post_list(request):
    posts = Post.cm_published.all()
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, id):
    try:
        post = Post.cm_published.get(id=id)
    except Post.DoesNotExist:
        raise Http404("No Post found.")

    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
