# from django.contrib.sitemaps import Sitemap
# from .models import Post
#
#
# class PostSitemap(Sitemap):
#     changefreq = 'weekly'
#     priority = 0.9
#
#     def items(self):
#         """Возвращает объекты подлежащие включению в карту сайта."""
#         return Post.cm_published.all()
#
#     def lastmod(self, obj):
#         """Принимает каждый пост и возвращает время последнего изменения поста."""
#         return obj.updated

from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.cm_published.all()

    def lastmod(self, obj):
        return obj.updated