from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from .forms import GroupForm, PostForm
from .models import Post, Group


def index(request):
    if request.method != "GET":
        return HttpResponseNotAllowed("GET")

    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def group_new(request):
    if request.method == "GET":
        form = GroupForm()
        return render(request, "posts/group_new.html", {"form": form})
    else:
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save()
            return render(request, "posts/group_detail.html", {"group": new_group})
        return render(request, "posts/group_new.html", {"form": form})


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        bound_form = GroupForm(request.POST, instance=group)
        if bound_form.is_valid():
            group = bound_form.save()
            return render(request, 'posts/group_detail.html', {"group": group, "title": "Group detail form"})
    else:
        bound_form = GroupForm(instance=group)
        return render(request, 'posts/group_edit.html', {"form": bound_form, "title": "Group edit form", "group": group})


@login_required
def new_post(request):
    if not request.method == 'POST':
        form = PostForm()
        return render(
            request, "posts/new_post.html", {'form': form}
        )

    form = PostForm(request.POST)
    if not form.is_valid():
        return render(
            request, "posts/new_post.html", {'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect('posts:index')
