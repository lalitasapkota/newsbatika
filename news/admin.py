from django.contrib import admin

from .models import CustomUser
from .models import Headline
from .models import vocabulary

# Register your models here.
admin.site.register(CustomUser)


@admin.register(Headline)
class HeadlineAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "url", "news_source", "vector"]
    list_filter = ["news_source"]


@admin.register(vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ["word_vocab", "identifier"]
