from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import views


admin.site.site_header = 'petank.cz'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('aktuality/', views.NewsListView.as_view()),
    path('aktuality/<slug:slug>/', views.NewsDetailView.as_view()),
    path('o_nas/<slug:slug>/', views.InfoDetailView.as_view()),
    path('clenove/', views.MemberListView.as_view()),
    path('clenove/<slug:slug>/', views.MemberDetailView.as_view()),
    path('poradame/<slug:slug>/', views.LiveEventDetailView.as_view()),
    path('galerie/', views.GalleryEventListView.as_view()),
    path('galerie/<slug:slug>/', views.GalleryEventDetailView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
