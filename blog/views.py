from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/blog.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-publication_date']


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'topic', 'content', 'publicized']
    success_url = '/news'

    def form_valid(self, form):
        form.instance.author = self.request.user.personnelprofile
        if form.instance.publicized is True:
            form.instance.publication_date = timezone.now()

        return super().form_valid(form)

    def test_func(self):
        if self.request.user.personnelprofile is not None:
            return True
        return False


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'topic', 'content', 'publicized']

    def form_valid(self, form):
        if form.instance.publicized is True:
            form.instance.publication_date = timezone.now()

        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser and self.request.user.personnelprofile is not None:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/news'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser and self.request.user.personnelprofile is not None:
            return True
        return False
