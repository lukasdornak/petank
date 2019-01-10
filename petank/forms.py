from django import forms
from . models import Photo, GalleryEvent


class PhotoAdminForm(forms.ModelForm):
    cropped = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        fields = ['original', 'descript', 'gallery', ]
        model = Photo
