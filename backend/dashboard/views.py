import redis
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Fault, Hospital, HospitalGroup
from django.core.paginator import Paginator

from datetime import timedelta
from django.utils import timezone
from .models import TelemetryHistory

import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_password = os.getenv('REDIS_PASSWORD')
r = redis.Redis(host=redis_host, port=6379, db=0, password=redis_password, decode_responses=True)


def obter_hospitais_redis(hospitais_permitidos=None):
    """
    Lê os hospitais do Redis.

    hospitais_permitidos:
        None -> retorna todos
        set() -> retorna apenas os hospitais informados
    """

    hospitais = []

    for redis_key in ("Central", "Usina"):
        redis_data = r.hgetall(redis_key)

        for hospital_nome, dados in redis_data.items(): #type: ignore

            if hospitais_permitidos is not None and hospital_nome not in hospitais_permitidos:
                continue

            try:
                detalhes = json.loads(dados)
                detalhes["hospital"] = hospital_nome
                hospitais.append(detalhes)

            except Exception as e:
                print(e)

    return hospitais

@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    # Não está visualizando nenhum grupo específico
    request.session.pop("grupo_visualizado", None)

    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "hospitals": obter_hospitais_redis()
        }
    )


@login_required
def group_dashboard(request):

    if request.user.grupo is None:
        return redirect("dashboard")

    hospitais_permitidos = set(
        Hospital.objects.filter(
            grupo=request.user.grupo
        ).values_list("nome", flat=True)
    )

    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "hospitals": obter_hospitais_redis(hospitais_permitidos),
            "grupo": request.user.grupo,
        }
    )

@login_required
def dashboard(request):
    hospital = request.user.hospital

    if request.user.hospital_groups.exists():
        return redirect("group_dashboard")

    if hospital.nome == 'CRADMIN':
        return redirect('admin_dashboard')
    
    if hospital.nome == 'Tecnico':
        return redirect('relatorio')
    
    
    keys = ["Central", "Usina"]

    for key in ("Central", "Usina"):
        data = r.hget(key, hospital.nome)

        if data:
            hospital_details = json.loads(data) #type: ignore

            if "accumulated" in hospital_details:
                try:
                    hospital_details["accumulated"] = round(
                        float(hospital_details["accumulated"]) *
                        hospital.multiplicador_acumulado,
                        2
                    )
                    print(hospital.multiplicador_acumulado)
                except (TypeError, ValueError):
                    print('erro')
                    pass

            return render(
                request,
                "dashboard/dashboard_central.html",
                {
                    "hospital": hospital,
                    "hospital_details": hospital_details,
                },
            )
        # caso não encontre dados no Redis
    return render(
        request,
        "dashboard/hospital_404.html",
        {
            "hospital": hospital.nome,
            "error": "Detalhes do hospital não encontrados no Redis"
        }
    )


@login_required
def hospital_data(request):
    hospital = request.user.hospital

    data = r.hget("Usina", hospital.nome)
    if data: 
        return JsonResponse(json.loads(data)) #type: ignore
    
    data = r.hget("Central", hospital.nome)
    if data: 
        return JsonResponse(json.loads(data)) #type: ignore
        
    return JsonResponse({'error': 'Sem dados'}, status=404)

@login_required
def faults_admin_view(request):
    hospital = request.GET.get("hospital")
    page = request.GET.get("page", 1)

    faults = Fault.objects.select_related("hospital")

    if hospital:
        faults = faults.filter(hospital__nome__icontains=hospital)

    faults = faults.order_by("-criado_em")

    paginator = Paginator(faults, 50)  # 50 registros por página
    page_obj = paginator.get_page(page)

    return render(
        request,
        "dashboard/faults.html",
        {
            "page_obj": page_obj,
            "faults": page_obj.object_list,
            "hospital": hospital,
        },
    )


from django.shortcuts import get_object_or_404

@login_required
def group_dashboard_admin(request, grupo_id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    grupo = get_object_or_404(HospitalGroup, pk=grupo_id)

    # Salva o grupo que está sendo visualizado
    request.session["grupo_visualizado"] = grupo.id #type: ignore

    nomes = set(
        Hospital.objects.filter(grupo=grupo)
        .values_list("nome", flat=True)
    )

    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "hospitals": obter_hospitais_redis(nomes),
            "grupo": grupo,
        },
    )

@login_required
def get_all_data(request):

    hospitais_permitidos = None

    # Administrador visualizando um grupo
    if request.user.is_superuser:

        grupo_id = request.session.get("grupo_visualizado")

        if grupo_id:
            hospitais_permitidos = set(
                Hospital.objects.filter(grupo_id=grupo_id)
                .values_list("nome", flat=True)
            )

    # Usuário comum com grupo
    elif request.user.grupo:

        hospitais_permitidos = set(
            Hospital.objects.filter(grupo=request.user.grupo)
            .values_list("nome", flat=True)
        )

    # Usuário de um único hospital
    else:

        hospitais_permitidos = {request.user.hospital.nome}

    hospitais = obter_hospitais_redis(hospitais_permitidos)

    locais = {}

    for hospital in hospitais:
        nome = hospital.pop("hospital")
        locais[nome] = hospital

    return JsonResponse({
        "locais": locais
    })

@login_required
def telemetry_history(request):

    if not request.user.is_superuser:
        return JsonResponse(
            {
                "error": "Acesso permitido somente para superusuários."
            },
            status=403
        )

    hospital_id = request.GET.get("hospital")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not hospital_id:
        return JsonResponse(
            {
                "error": "Hospital não informado."
            },
            status=400
        )

    hospital = get_object_or_404(
        Hospital,
        id=hospital_id
    )

    queryset = TelemetryHistory.objects.filter(
        hospital=hospital
    )

    # --------------------------------------------------
    # Período
    # --------------------------------------------------

    if start and end:

        try:

            from django.utils.dateparse import parse_datetime

            start_date = parse_datetime(start)
            end_date = parse_datetime(end)

            if start_date and end_date:

                queryset = queryset.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                )

        except Exception:

            return JsonResponse(
                {
                    "error": "Período inválido."
                },
                status=400
            )

    else:

        # Padrão: últimos 30 dias
        inicio = timezone.now() - timedelta(days=30)

        queryset = queryset.filter(
            timestamp__gte=inicio
        )

    queryset = queryset.order_by("timestamp")

    dados = []

    for item in queryset:

        dados.append(
            {
                "timestamp": item.timestamp.isoformat(),

                "pressure": item.pressure,

                "product_pressure":
                    item.product_pressure,

                "purity":
                    item.purity,

                "flow":
                    item.flow,

                "accumulated":
                    item.accumulated,
            }
        )

    return JsonResponse(
        {
            "hospital": hospital.nome,
            "hospital_id": hospital.id,#type: ignore
            "data": dados,
        }
    )

@login_required
def telemetry_history_page(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    hospitals = Hospital.objects.all().order_by("nome")

    return render(
        request,
        "dashboard/telemetry_history.html",
        {
            "hospitals": hospitals,
        }
    )

@login_required
def accumulated_history(request):
    hospital = request.user.hospital

    inicio = timezone.now() - timedelta(days=30)

    queryset = (
        TelemetryHistory.objects
        .filter(
            hospital=hospital,
            timestamp__gte=inicio
        )
        .order_by("timestamp")
    )

    dados = []

    for item in queryset:
        dados.append({
            "timestamp": item.timestamp.isoformat(),
            "accumulated": item.accumulated,
        })

    return JsonResponse({
        "hospital": hospital.nome,
        "data": dados,
    })