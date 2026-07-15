import redis
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Fault, Hospital, HospitalGroup

import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_password = os.getenv('REDIS_PASSWORD')
r = redis.Redis(host=redis_host, port=6379, db=0, password=redis_password, decode_responses=True)


def processar_redis(hospitais_permitidos=None):
    """
    hospitais_permitidos:
        None -> retorna todos
        set() -> retorna apenas os hospitais do conjunto
    """

    multiplicadores = {
        h.nome: h.multiplicador_acumulado
        for h in Hospital.objects.all()
    }

    hospitais = []

    for redis_key in ("Central", "Usina"):
        redis_data = r.hgetall(redis_key)

        for hospital_nome, dados in redis_data.items():

            if hospitais_permitidos is not None and hospital_nome not in hospitais_permitidos:
                continue

            try:
                detalhes = json.loads(dados)

                if "accumulated" in detalhes:
                    try:
                        fator = float(multiplicadores.get(hospital_nome, 1.0))
                        detalhes["accumulated"] = round(
                            float(detalhes["accumulated"]) * fator,
                            2
                        )
                        print(
                            hospital_nome,
                            detalhes.get("accumulated"),
                            fator
                        )
                    except (TypeError, ValueError):
                        print('erro')
                        pass

                detalhes["hospital"] = hospital_nome
                hospitais.append(detalhes)

            except Exception as e:
                print(e)

    return hospitais


@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "hospitals": processar_redis()
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
            "hospitals": processar_redis(hospitais_permitidos),
            "grupo": request.user.grupo,
        }
    )

@login_required
def dashboard(request):
    hospital = request.user.hospital

    if request.user.hospital_groups.exists():
        print('redirect grupo')
        return redirect("group_dashboard")

    if hospital.nome == 'CRADMIN':
        return redirect('admin_dashboard')
    
    if hospital.nome == 'Tecnico':
        return redirect('relatorio')
    
    
    keys = ["Central", "Usina"]

    for key in ("Central", "Usina"):
        data = r.hget(key, hospital.nome)

        if data:
            hospital_details = json.loads(data)

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
    hospital = request.GET.get('hospital')

    faults = Fault.objects.all()

    if hospital:
        faults = faults.filter(hospital__nome__icontains=hospital)

    faults = faults.order_by('-criado_em')
    context = {
        'faults': faults
    }

    return render(
        request, 'dashboard/faults.html',
        context
    )

@login_required
def get_all_data(request):

    if request.user.is_superuser:
        hospitais_permitidos = None

    elif request.user.grupo:
        hospitais_permitidos = set(
            Hospital.objects.filter(
                grupo=request.user.grupo
            ).values_list("nome", flat=True)
        )

    else:
        hospitais_permitidos = {request.user.hospital.nome}

    hospitais = processar_redis(hospitais_permitidos)

    locais = {}

    for hospital in hospitais:
        nome = hospital.pop("hospital")
        locais[nome] = hospital

    return JsonResponse({
        "locais": locais
    })