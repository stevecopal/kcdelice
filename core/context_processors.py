from .models import Company


def company(request):
    """Expose la fiche entreprise à tous les templates."""
    return {"company": Company.get_solo()}
