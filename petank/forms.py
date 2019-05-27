from django import forms
from . models import Photo, GalleryEvent


class PhotoAdminForm(forms.ModelForm):
    cropped = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        fields = ['original', 'description', 'gallery', ]
        model = Photo

class GalleryEventAdminForm(forms.ModelForm):
    photo_list = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), required=False, label='fotky')
    photo_list_description = forms.CharField(required=False, label='popisek')

    class Meta:
        fields = ['date', 'date2', 'headline', 'published', 'photo', 'photo_list', 'photo_list_description']
        model = GalleryEvent
