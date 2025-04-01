from django.contrib.sitemaps import Sitemap
from .models import Post  # Make sure to import your Post model

class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        # Return all the published posts
        return Post.published.all()

    def lastmod(self, obj):
        # Return the last modified date of the post
        return obj.updated
