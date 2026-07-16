from django.contrib import admin
from .models import AirCentral, OxygenCentral, Hospital, ChatTelegram, Fault, HospitalGroup


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "grupo",
        "multiplicador_acumulado",
    )

    search_fields = ("nome",)
    list_filter = ("grupo",)

    fieldsets = (
        (
            "Informações",
            {
                "fields": (
                    "nome",
                    "grupo",
                )
            },
        ),
        (
            "Fluxo Acumulado",
            {
                "fields": (
                    "multiplicador_acumulado",
                    "offset_acumulado",
                )
            },
        ),
        (
            "Pressão da Rede",
            {
                "fields": (
                    "multiplicador_pressao",
                    "offset_pressao",
                )
            },
        ),
        (
            "Pressão do Produto",
            {
                "fields": (
                    "multiplicador_pressao_produto",
                    "offset_pressao_produto",
                )
            },
        ),
        (
            "Pureza",
            {
                "fields": (
                    "multiplicador_pureza",
                    "offset_pureza",
                )
            },
        ),
    )
    

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

    list_per_page = 500




@admin.register(HospitalGroup)
class HospitalGroupAdmin(admin.ModelAdmin):
    list_display = ("nome", "total_hospitais", "total_usuarios")
    search_fields = ("nome",)
    filter_horizontal = ("usuarios",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "nome",
                    "usuarios",
                )
            },
        ),
    )

    def total_hospitais(self, obj):
        return obj.hospitais.count()
    total_hospitais.short_description = "Hospitais"

    def total_usuarios(self, obj):
        return obj.usuarios.count()
    total_usuarios.short_description = "Usuários"