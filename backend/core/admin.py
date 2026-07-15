#type: ignore
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Monitoramento",
            {
                "fields": (
                    "hospital",
                    "grupo",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Monitoramento",
            {
                "classes": ("wide",),
                "fields": (
                    "hospital",
                    "grupo",
                ),
            },
        ),
    )

    list_display = (
        "username",
        "hospital",
        "grupo",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "grupo",
        "hospital",
        "is_staff",
        "is_active",
    )
# admin.site.register(CustomUser, CustomUserAdmin)