from django.http import Http404
from django.shortcuts import render

from blog.models import Post


def post_list(request):
    posts = Post.cm_published.all()
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, year, month, day, slug):
    try:
        post = Post.cm_published.get(status=Post.Status.PUBLISHED,
                                     slug=slug,
                                     publish__year=year,
                                     publish__month=month,
                                     publish__day=day)
    except Post.DoesNotExist:
        raise Http404("No Post found.")

    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
