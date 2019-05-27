import base64
from io import BytesIO
from itertools import chain

from django.contrib import admin, messages
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import *
from .forms import PhotoAdminForm, GalleryEventAdminForm


def make_assign_to_gallery(gallery):
    def assign_to_gallery(modeladmin, request, queryset):
        for photo in queryset:
            changed = photo.assign_to(gallery)
            if changed:
                messages.info(request, "Fotka {0} zařazena do galerie {1}".format(photo.name, gallery.__str__()))

    assign_to_gallery.short_description = "Zařadit do {0}".format(gallery.__str__())
    assign_to_gallery.__name__ = 'assign_to_gallery_{0}'.format(gallery.pk)

    return assign_to_gallery


class PublishMixin:
    actions = ['publish', 'hide']

    def publish(self, request, queryset):
        queryset.update(published=True)

    def hide(self, request, queryset):
        queryset.update(published=False)

    publish.short_description = 'Publikovat'
    hide.short_description = 'Skrýt'


class PhotoInline(admin.TabularInline):
    model = Photo
    fields = ['original', 'description', ]
    extra = 1


class NewsAdmin(PublishMixin, admin.ModelAdmin):
    list_display = ['headline', 'date', 'published']
    list_editable = ['published']
    fieldsets = (
        (None, {
            'fields': (
                'date', 'headline', 'short_text', 'published', 'gallery_link', 'gallery_link_text'
            )
        }),
        ('Obsah', {
            'fields': (
                'photo', 'text_before', 'text_beside', 'text_after'
            )
        })
    )


class InfoAdmin(PublishMixin, admin.ModelAdmin):
    list_display = ['headline', 'link', 'order', 'published']
    list_editable = ['order', 'published']
    fieldsets = (
        (None, {
            'fields': (
                'headline', 'link', 'order', 'published', 'gallery_link', 'gallery_link_text'
            )
        }),
        ('Obsah', {
            'fields': (
                'photo', 'text_before', 'text_beside', 'text_after'
            )
        })
    )


class LiveEventAdmin(PublishMixin, admin.ModelAdmin):
    list_display = ['headline', 'link', 'date', 'date2', 'published']
    list_editable = ['published']
    fieldsets = (
        (None, {
            'fields': (
                'date', 'date2', 'headline', 'link', 'published', 'gallery_link', 'gallery_link_text'
            )
        }),
        ('Obsah', {
            'fields': (
                'photo', 'text_before', 'text_beside', 'text_after'
            )
        })
    )


class GalleryEventAdmin(PublishMixin, admin.ModelAdmin):
    list_display = ['headline', 'date', 'date2', 'year', 'published']
    list_editable = ['published']
    inlines = [PhotoInline, ]
    form = GalleryEventAdminForm
    fieldsets = (
        (None, {
            'fields': (
                'date', 'date2', 'headline', 'published', 'photo', 'photo_list', 'photo_list_description'
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        photo_list = dict(form.files).get('photo_list', [])
        for photo in photo_list:
            Photo.objects.create(original=photo, description=form.cleaned_data.get('photo_list_description') or obj.headline, gallery=obj)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'get_usage', 'get_members', 'gallery']
    list_display_links = ['description']
    form = PhotoAdminForm
    actions = ['unassign']
    readonly_fields = ['get_img_url']

    def get_usage(self, obj):
        return ", ".join([article.str_dist() or article.__str__() for article in chain(
            obj.news_set.all(),
            obj.info_set.all(),
            obj.liveevent_set.all(),
            obj.galleryevent_set.all(),
        )])

    def get_members(self, obj):
        return ", ".join([member.__str__() for member in obj.member_set.all()])

    def get_img_url(self, obj):
        return obj.original.url

    get_usage.short_description = "použití"
    get_members.short_description = "profilovka"
    get_img_url.short_description = "url fotky"

    def unassign(self, request, queryset):
        for photo in queryset:
            if photo.gallery:
                messages.info(request, "Fotka {0} vyřazena z galerie {1}.".format(photo.__str__(), photo.gallery))
        queryset.update(gallery=None)

    unassign.short_description = "Vyřadit z galerie"

    def get_actions(self, request):
        actions = super().get_actions(request)

        for gallery in list(GalleryEvent.objects.all()):
            action = make_assign_to_gallery(gallery)
            actions[action.__name__] = (action, action.__name__, action.short_description)

        return actions

    def save_model(self, request, obj, form, change):
        # if request.POST.get('cropped'):
        if 'cropped' in form.changed_data:
            format, imgstr = request.POST['cropped'].split(';base64,')
            ext = format.split('/')[-1]
            file = BytesIO(base64.b64decode(imgstr))
            image = InMemoryUploadedFile(file,
                                         field_name='cropped',
                                         name=str(obj.id) + ext,
                                         content_type="image/jpeg",
                                         size=len(file.getvalue()),
                                         charset=None)
            obj.cropped = image
        super().save_model(request, obj, form, change)

    class Media:
        js = ['https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js',
              'https://cdnjs.cloudflare.com/ajax/libs/croppie/2.6.1/croppie.min.js',
              '/static/petank/js/croppie_image_field.js']
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/croppie/2.6.1/croppie.min.css',)
        }


class MemberAdmin(PublishMixin, admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'user', 'published']
    list_editable = ['published']
    fieldsets = (
        (None, {
            'fields': (
                'first_name', 'last_name', 'user', 'published', 'gallery_link', 'gallery_link_text'
            )
        }),
        ('Obsah', {
            'fields': (
                'photo', 'text_before', 'text_beside', 'text_after'
            )
        })
    )

admin.site.register(News, NewsAdmin)
admin.site.register(Info, InfoAdmin)
admin.site.register(LiveEvent, LiveEventAdmin)
admin.site.register(GalleryEvent, GalleryEventAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Member, MemberAdmin)
