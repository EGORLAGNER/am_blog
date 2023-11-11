from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from blog.models import Post
from .forms import EmailPostForm


class PostListView(ListView):
    """Существует огромное множество различных View.
     Они работают по принципу миксинов и по умолчанию обладают определенным поведением.
     Это поведение по умолчанию переопределяется переменными внутри класса."""

    queryset = Post.cm_published.all()  # по умолчанию достаточно передать модель и выполнится запрос Post.objects.all
    context_object_name = 'posts'  # по умолчанию название переменной object_list
    paginate_by = 3
    template_name = 'blog/post/list.html'  # по умолчанию ищет шаблон 'blog/post_list.html'


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


def post_share(request, post_id):
    # извлечь пост по идентификатору ID
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)

    if request.method == 'POST':
        # форма передана на обработку
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # отправить письмо
    else:
        # если тип запроса не POST, а следовательно GET, то отобразить пустую форму
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form})


