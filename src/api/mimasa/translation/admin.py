from django.contrib import admin

from .models import MimasaModel, TranslationNotification


@admin.register(MimasaModel)
class MimasaModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "input_language", "output_language", "task_status", "created_at")
    search_fields = ("id", "user__username", "task_id")
    list_filter = ("task_status", "input_language", "output_language")


@admin.register(TranslationNotification)
class TranslationNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "translation", "is_read", "created_at")
    search_fields = ("user__username", "translation__id", "message")
    list_filter = ("is_read",)
