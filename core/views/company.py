import re

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from ..forms import CompanyForm
from ..models import Company, EventCategory
from .mixins import StaffRequiredMixin

# Contenu de repli de la page À propos.
# Ces textes sont affichés tant que les champs correspondants de la fiche
# entreprise (présentation, mission, vision) sont vides ; dès qu'un texte est
# enregistré en base, c'est lui qui est utilisé, paragraphe par paragraphe.
ABOUT_FALLBACK = {
    "presentation": [
        "Depuis 2015, KCDélices imagine et réalise des événements qui marquent les "
        "esprits à Douala et dans tout le Cameroun. Née d'une passion pour la "
        "pâtisserie et l'art de recevoir, notre maison a grandi en gardant une "
        "exigence intacte : le goût, la beauté et l'émotion.",
        "Mariages, anniversaires, baptêmes, cérémonies d'entreprise ou soirées "
        "privées : chaque projet est unique. Nous commençons par écouter, comprendre "
        "votre univers et vos contraintes, puis nous concevons une expérience qui "
        "vous ressemble, du premier croquis à la dernière décoration.",
        "Une équipe pluridisciplinaire — pâtissiers, décorateurs, cuisiniers et "
        "logisticiens — travaille main dans la main vers un seul objectif : une "
        "réception fluide, généreuse et sans fausse note, dont vos invités parlent "
        "longtemps après la fête.",
    ],
    "mission": [
        "Notre mission est de transformer chaque événement en un souvenir intact, "
        "en réunissant saveurs, décor et organisation au même niveau d'exigence.",
        "Nous voulons être le partenaire sur qui vous pouvez compter : présent des "
        "premières idées jusqu'au dernier rangement, transparent sur les prix, "
        "ponctuel le jour J et attentif aux détails qui font la différence.",
    ],
    "vision": [
        "Devenir la référence de l'événementiel sur mesure en Afrique centrale, "
        "reconnue pour la finesse de ses créations et la fiabilité de son organisation.",
        "Nous voulons aussi faire grandir les talents locaux : former des pâtissiers, "
        "des décorateurs et des organisateurs capables de porter cette exigence loin.",
    ],
}

# Piliers de la mission (futurs champs d'un modèle dédié).
MISSION_PILLARS = [
    {
        "title": "Écoute",
        "description": "Chaque projet commence par une conversation : vos envies, "
        "vos contraintes, votre budget, sans jamais forcer la main.",
    },
    {
        "title": "Exigence",
        "description": "Produits sélectionnés, finitions soignées et contrôle "
        "qualité avant chaque livraison, du gâteau à la scénographie.",
    },
    {
        "title": "Sérénité",
        "description": "Un interlocuteur unique, un rétroplanning clair et une "
        "équipe sur place le jour J pour que vous profitez pleinement.",
    },
]

# Chiffres clés (valeurs de démonstration, remplaçables par des données en base).
KEY_FIGURES = [
    {"value": "10 ans", "label": "d'expérience"},
    {"value": "500+", "label": "événements réalisés"},
    {"value": "2", "label": "villes couvertes"},
    {"value": "98 %", "label": "de clients satisfaits"},
]


def split_paragraphs(text: str) -> list[str]:
    """Découpe un texte libre en paragraphes (ligne vide ou simple retour)."""
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    blocks = [block.strip() for block in re.split(r"\n\s*\n", cleaned) if block.strip()]
    if len(blocks) == 1:
        blocks = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return blocks


def build_section(key: str, title: str, text: str) -> dict:
    """Section éditoriale : le texte de la base prime sur le contenu de repli."""
    paragraphs = split_paragraphs(text) or ABOUT_FALLBACK[key]
    return {"key": key, "title": title, "paragraphs": paragraphs}


class AboutView(TemplateView):
    """À propos : présentation, mission et vision, complétées par des textes de repli."""

    template_name = "public/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.get_solo()
        context["company"] = company
        context["sections"] = {
            key: build_section(key, title, getattr(company, key, "") or "")
            for key, title in (
                ("presentation", "Présentation"),
                ("mission", "Mission"),
                ("vision", "Vision"),
            )
        }
        context["mission_pillars"] = MISSION_PILLARS
        context["key_figures"] = KEY_FIGURES
        # Demande de devis : le message WhatsApp est construit côté navigateur
        # à partir de ces informations.
        context["whatsapp_number"] = company.whatsapp_digits if company else ""
        context["event_categories"] = EventCategory.objects.filter(is_active=True).order_by(
            "name"
        ).values_list("name", flat=True)
        return context


class CompanyUpdateView(StaffRequiredMixin, UpdateView):
    """Formulaire unique de la fiche entreprise (création si absente)."""

    model = Company
    form_class = CompanyForm
    template_name = "espace/company_form.html"

    def get_object(self, queryset=None):
        return Company.get_solo() or Company()

    def form_valid(self, form):
        messages.success(self.request, "Informations de l'entreprise mises à jour avec succès.")
        return super().form_valid(form)

    success_url = reverse_lazy("company_update")
