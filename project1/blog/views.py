from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm  
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.utils import timezone
from django.db import models
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])  # Only filter if tag exists

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)  # Deliver the first page if not an integer
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # Deliver the last page if out of range

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})  # Make sure 'tag' is singular

from django.db.models import Count

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, 
        slug=post, 
        status='published',
        publish__year=year,   
        publish__month=month,  
        publish__day=day
    )

    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # ✅ Ensure similar posts logic runs
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    print(post_tags_ids)  # Debugging
    print(similar_posts)  # Debugging

    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,  # ✅ Fix the variable name
    })



def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)  
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'mznpingol@tip.edu.ph', [cd['to']])
            sent = True
    
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
    

#def post_list(request):
#    object_list = Post.published.all()
#    paginator = Paginator(object_list, 3)


class PostListView(ListView):
     queryset = Post.published.all()
     context_object_name = 'posts'
     paginate_by = 100
     template_name = 'blog/post/list.html'