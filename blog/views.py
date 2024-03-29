from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger

from blog.models import Post
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

from django.views.generic import ListView


# class PostListView(ListView):
#     """Существует огромное множество различных View.
#      Они работают по принципу миксинов и по умолчанию обладают определенным поведением.
#      Это поведение по умолчанию переопределяется переменными внутри класса."""
#
#     queryset = Post.cm_published.all()  # по умолчанию достаточно передать модель и выполнится запрос Post.objects.all
#     context_object_name = 'posts'  # по умолчанию название переменной object_list
#     paginate_by = 3
#     template_name = 'blog/post/list.html'  # по умолчанию ищет шаблон 'blog/post_list.html'


def post_list(request, tag_slug=None):
    post_list = Post.cm_published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        """Если запрошенная страница вне диапазона страниц, то отрисовать последнюю."""
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        """Если вместо номера страницы в браузере указано не целое число."""
        posts = paginator.page(1)

    return render(request,
                  'blog/post/list.html',
                  {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)

    form = CommentForm()

    # список схожих постов
    # список с id тегов, связанных с текущим постом
    post_tags_ids = post.tags.values_list('id', flat=True)  # flat=True - вернуть список без кортежей

    # Достать все посты которые связаны с тегами (связанные посты вычисляются по id тегов).
    # Посты и теги имеют связь многие ко многим.
    # Имеется таблица taggit_taggeditem, которая хранит связи.
    # При обращении к tags через OMR - получу менеджер тегов, здесь же в "tags__in" речь о проверки значения поля в БД.
    # По логике у post в поле tags должен лежать id тега, с которым он связан, но все не так явно при работе через ORM.
    similar_post = Post.cm_published.filter(tags__in=post_tags_ids).exclude(id=post.id)

    # annotate создает временное поле same_tags
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html', {
                      'post': post,
                      'comments': comments,
                      'form': form,
                      'similar_post': similar_post,
                  })


def post_share(request, post_id):
    # извлечь пост по идентификатору ID
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)

    sent = False

    if request.method == 'POST':
        # форма передана на обработку
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} {cd['name']} \'s comments: {cd['comments']}"
            send_mail(subject, message, 'egorlagner@gmail.com', [cd['to']])
            sent = True

    else:
        # если тип запроса не POST, а следовательно GET, то отобразить пустую форму
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)

    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {
                      'post': post,
                      'form': form,
                      'comment': comment, })


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (Post.cm_published.
                       annotate(similarity=TrigramSimilarity('title', query),).
                       filter(similarity__gt=0.1).
                       order_by('-similarity'))

    return render(request, 'blog/post/search.html',
                  {
                      'form': form,
                      'query': query,
                      'results': results
                  })
