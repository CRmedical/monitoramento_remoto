from django.contrib import admin
from .models import AirCentral, OxygenCentral, Hospital, ChatTelegram, Fault

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    list_filter = ['nome']

    fieldsets = [
        (
            None, 
            {'fields': ('nome',)}
        ),
    ]


@admin.register(ChatTelegram)
class ChatTelegramAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'chat_id']
    search_fields = ['hospital']
    list_filter = ['hospital']

    fieldsets = [
        (
            None,
            {'fields': ('hospital', 'chat_id',)}
        ),
    ]

@admin.register(Fault)
class FaultAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'falha', 'dados', 'criado_em']
    search_fields = ['hospital__nome', 'falha', 'dados']
    list_filter = ['hospital', 'criado_em']
    ordering = ['-criado_em']
    list_select_related = ['hospital']