from django.http import HttpResponseRedirect
from django.views import generic

from . models import *


def home(request):
    return HttpResponseRedirect('/aktuality/')


class ContextMixin:

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['info_list'] = Info.objects.all() if self.request.user.has_perm('petank.change_info') else \
            Info.objects.filter(published=True)
        context_data['liveevent_list'] = LiveEvent.objects.all() if self.request.user.has_perm('petank.change_liveevent') else \
            LiveEvent.objects.filter(published=True)
        context_data['model'] = self.model.__name__
        return context_data

    def get_queryset(self):
        return super().get_queryset() if self.request.user.has_perm('petank.change_' + self.model.__name__) else \
            super().get_queryset().filter(published=True)


class NewsListView(ContextMixin, generic.ListView):
    model = News


class NewsDetailView(ContextMixin, generic.DetailView):
    model = News


class InfoDetailView(ContextMixin, generic.DetailView):
    model = Info


class LiveEventDetailView(ContextMixin, generic.DetailView):
    model = LiveEvent


# class MemberListView(ContextMixin, generic.ListView):
#     model = Member
#
#
# class MemberDetailView(ContextMixin, generic.DetailView):
#     model = Member


class SponsorListView(ContextMixin, generic.ListView):
    model = Sponsor


class GalleryEventListView(ContextMixin, generic.ListView):
    model = GalleryEvent


class GalleryEventDetailView(ContextMixin, generic.DetailView):
    model = GalleryEvent


class PhotoDetailView(generic.DetailView):
    model = Photo

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data()
        context_data['gallery_info'] = self.object.get_gallery_info()
        return context_data

    def get_queryset(self):
        return super().get_queryset().filter(gallery__slug=self.kwargs.get('gallery'))
