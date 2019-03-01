# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from imagekit import ImageSpec, register
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill
from django.core.exceptions import ValidationError


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


def path_photo(instance, filename):
    return 'photo/{0}-{1}.jpg'.format(instance.id, slugify(instance.description))

def path_photo_cropped(instance, filename):
    return 'photo/{0}-{1}_cropped.png'.format(instance.id, slugify(instance.description))


class AutoCrop(ImageSpec):
    processors = [ResizeToFill(500, 500)]
    format = 'JPEG'
    options = {'quality': 100}


register.generator('petank:auto_crop', AutoCrop)


class Article(models.Model):
    date = models.DateField('datum')
    headline = models.CharField('nadpis', max_length=100, unique=True)
    photo = models.ForeignKey('Photo', verbose_name='fotka', on_delete=models.PROTECT)
    published = models.BooleanField('publikováno', default=False, help_text='Bude se zobrazovat všem návštěvníkům webu.')
    slug = models.SlugField(unique=True, editable=False)
    text_before = RichTextField('obsah nad obrázkem', null=True, blank=True)
    text_beside = RichTextField('obsah vedle obrázku', null=True, blank=True, help_text='Pro optimální vzhled je vhodné použít toto pole pouze je-li fotka na výšku.')
    text_after = RichTextField('obsah pod obrázkem', null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.headline

    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        return super().save(*args, **kwargs)

    def get_slug(self):
        return slugify(self.headline)


class News(Article):
    short_text = models.TextField('úvod', max_length=200, help_text='Zobrazuje se na hlavní stránce.')

    class Meta:
        verbose_name = 'aktualita'
        verbose_name_plural = 'aktuality'
        ordering = ['-date']

    def str_dist(self):
        return '{0} (A)'.format(super().__str__())


class Info(Article):
    date = None
    link = models.CharField('odkaz v menu', max_length=50)
    photo = models.ForeignKey('Photo', verbose_name='fotka', on_delete=models.PROTECT, null=True, blank=True)
    order = models.PositiveSmallIntegerField('pořadí v menu', default=1)

    class Meta:
        verbose_name = 'o nás'
        verbose_name_plural = 'o nás'
        ordering = ['order']

    def str_dist(self):
        return '{0} (O)'.format(super().__str__())


class LiveEvent(Article):
    date2 = models.DateField('datum do', null=True, blank=True,
                             help_text='Pořádáme-li něco dělší dobu a ne jen jednoho dene, pak "datum do" slouží jako konec takové doby.')
    link = models.CharField('odkaz v menu', max_length=33,
                            help_text='Odkaz v menu může být stejný jako nadpis, ale maximální délka je 33 znaků (u nadpisu 100).')
    photo = models.ForeignKey('Photo', verbose_name='fotka', on_delete=models.PROTECT, null=True, blank=True)

    class Meta(Article.Meta):
        verbose_name = 'pořádáme'
        verbose_name_plural = 'pořádáme'
        ordering = ['-date']

    def str_dist(self):
        return '{0} (P)'.format(super().__str__())


class GalleryEvent(Article):
    date2 = models.DateField('datum do', null=True, blank=True,
                             help_text='Není-li galerie z jednoho dne ale za nějakou dobu, pak "datum do" slouží jako konec takové doby.')
    year = models.DecimalField(max_digits=4, decimal_places=0, editable=False)
    headline = models.CharField('nadpis', max_length=100)
    photo = models.ForeignKey('Photo', verbose_name='fotka', on_delete=models.PROTECT,
                              help_text='Pro zobrazení v seznamu galerií.')

    class Meta:
        verbose_name = 'galerie'
        verbose_name_plural = 'galerie'
        unique_together = ('year', 'headline')
        ordering = ['-date']

    def __str__(self):
        return '{0} ({1})'.format(super().__str__(), self.year)

    def save(self, *args, **kwargs):
        self.year = self.date.year
        return super().save(*args, **kwargs)

    def str_dist(self):
        return False

    def get_slug(self):
        return '{}-{}'.format(slugify(self.headline), str(self.year))


class Photo(models.Model):
    original = models.ImageField('fotka', width_field='width', height_field='height', upload_to=path_photo, storage=OverwriteStorage(), null=True, blank=False)
    width = models.PositiveSmallIntegerField('šířka', null=True, blank=True, editable=False)
    height = models.PositiveSmallIntegerField('šířka', null=True, blank=True, editable=False)
    cropped = models.ImageField('ořez', upload_to=path_photo_cropped, storage=OverwriteStorage(), null=True, blank=False)
    small = ImageSpecField(source='original', processors=[ResizeToFit(600, 600)], format='JPEG', options={'quality': 100})
    large = ImageSpecField(source='original', processors=[ResizeToFit(1200, 1200)], format='JPEG', options={'quality': 100})
    description = models.CharField('popisek', max_length=150)
    gallery = models.ForeignKey(GalleryEvent, verbose_name='galerie', on_delete=models.CASCADE,
                                related_name='photos', null=True, blank=True)
    class Meta:
        verbose_name = 'fotka'
        verbose_name_plural = 'fotky'

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        hidden_original = self.original
        hidden_cropped = self.cropped
        self.original = None
        self.cropped = None
        super().save(*args, **kwargs)
        self.original = hidden_original
        self.cropped = hidden_cropped
        super().save(update_fields=['original', 'cropped'])

    def get_ratio(self):
        return round(100*self.height/self.width) if (self.height and self.width) else 0

    def assign_to(self, gallery):
        gallery.photos.add(self)


class Member(Article):
    date = None
    headline = None
    user = models.OneToOneField(User, verbose_name='uživatel', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField('jméno', max_length=50)
    last_name = models.CharField('příjmení', max_length=50)

    class Meta:
        verbose_name = 'Člen'
        verbose_name_plural = 'Členové'

    def __str__(self):
        return self.full_name()

    def save(self, *args, **kwargs):
        if self.user:
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.save(update_fields=['first_name', 'last_name'])
        super().save(*args, **kwargs)

    def get_slug(self):
        slug = slugify(self.full_name())
        i = 2
        while Member.objects.filter(slug=slug).exists():
            slug = '{0}_{1}'.format(slugify(self.full_name()), i)
            i += 1
        return slug

    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name).strip()
