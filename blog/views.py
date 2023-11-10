from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from blog.models import Post


# def post_list(request):
#     post_list = Post.cm_published.all()
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         """Если запрошенная страница вне диапазона страниц, то отрисовать последнюю."""
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         """Если вместо номера страницы в браузере указано не целое число."""
#         posts = paginator.page(1)
#
#     return render(request,
#                   'blog/post/list.html',
#                   {'posts': posts})

class PostListView(ListView):

    queryset = Post.cm_published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
