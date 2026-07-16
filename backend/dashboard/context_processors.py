from .models import HospitalGroup

def hospital_groups(request):
    return {
        "hospital_groups": HospitalGroup.objects.all().order_by("nome")
    }