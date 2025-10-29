from django.contrib import admin

from .models import Character


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    fieldsets = (
        (None, {
            "fields": ("name", "header_description", "short_description", "greeting"),
        }),
        ("Treść i wygląd", {
            "fields": ("description", "avatar", "avatar_url"),
        }),
    )
