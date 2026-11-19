from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory

from ..models import Quote, QuoteItem

INPUT_CLASSES = (
    "w-full rounded-xl border border-noir/15 bg-blanc px-4 py-3 text-noir "
    "placeholder:text-noir/40 focus:border-vert focus:outline-none focus:ring-2 focus:ring-vert/20"
)
TEXTAREA_CLASSES = INPUT_CLASSES + " min-h-24 resize-y"
MONEY_CLASSES = INPUT_CLASSES + " text-right tabular-nums"


def _money_widget(placeholder: str = "0") -> forms.NumberInput:
    return forms.NumberInput(
        attrs={
            "min": "0",
            "step": "0.01",
            "inputmode": "decimal",
            "placeholder": placeholder,
            "class": MONEY_CLASSES,
            "data-money": "",
        }
    )


class QuoteForm(forms.ModelForm):
    """Identité du client, informations d'événement et montants du devis."""

    class Meta:
        model = Quote
        fields = [
            "title",
            "client_name",
            "client_phone",
            "client_email",
            "client_address",
            "event_location",
            "event_date",
            "valid_until",
            "discount",
            "transport_cost",
            "deposit_amount",
            "notes",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Ex. : Mariage de Jean et Marie",
                    "class": INPUT_CLASSES,
                }
            ),
            "client_name": forms.TextInput(
                attrs={"placeholder": "Nom complet du client", "class": INPUT_CLASSES}
            ),
            "client_phone": forms.TextInput(
                attrs={
                    "placeholder": "+237 6XX XXX XXX",
                    "class": INPUT_CLASSES,
                    "inputmode": "tel",
                }
            ),
            "client_email": forms.EmailInput(
                attrs={
                    "placeholder": "adresse@exemple.com (facultatif)",
                    "class": INPUT_CLASSES,
                }
            ),
            "client_address": forms.TextInput(
                attrs={
                    "placeholder": "Quartier, ville (facultatif)",
                    "class": INPUT_CLASSES,
                }
            ),
            "event_location": forms.TextInput(
                attrs={"placeholder": "Lieu de l'événement", "class": INPUT_CLASSES}
            ),
            "event_date": forms.DateInput(
                attrs={"type": "date", "class": INPUT_CLASSES}
            ),
            "valid_until": forms.DateInput(
                attrs={"type": "date", "class": INPUT_CLASSES}
            ),
            "discount": _money_widget(),
            "transport_cost": _money_widget(),
            "deposit_amount": _money_widget(),
            "notes": forms.Textarea(
                attrs={
                    "placeholder": "Conditions particulières, précisions… (facultatif)",
                    "rows": 3,
                    "class": TEXTAREA_CLASSES,
                }
            ),
        }

    def clean_client_name(self):
        name = (self.cleaned_data.get("client_name") or "").strip()
        if not name:
            raise forms.ValidationError("Le nom du client est obligatoire.")
        return name

    def clean_client_phone(self):
        phone = (self.cleaned_data.get("client_phone") or "").strip()
        if not phone:
            raise forms.ValidationError("Le numéro du client est obligatoire.")
        if len(phone) < 6:
            raise forms.ValidationError("Le numéro du client semble incomplet.")
        return phone

    def clean_event_location(self):
        location = (self.cleaned_data.get("event_location") or "").strip()
        if not location:
            raise forms.ValidationError("Le lieu de l'événement est obligatoire.")
        return location

    def clean_client_email(self):
        return (self.cleaned_data.get("client_email") or "").strip()

    def clean(self):
        cleaned = super().clean()
        for field in ("discount", "transport_cost", "deposit_amount"):
            value = cleaned.get(field)
            if value is not None and value < 0:
                self.add_error(field, "Le montant ne peut pas être négatif.")
        client_email = cleaned.get("client_email")
        if client_email == "":
            cleaned["client_email"] = ""
        return cleaned


class QuoteItemForm(forms.ModelForm):
    """Ligne de devis : désignation libre, quantité et prix unitaire."""

    class Meta:
        model = QuoteItem
        fields = ["title", "quantity", "unit_price"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Ex. : Location de 100 chaises",
                    "class": INPUT_CLASSES,
                    "data-item-title": "",
                    "aria-label": "Désignation",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "min": "0.01",
                    "step": "0.01",
                    "inputmode": "decimal",
                    "class": INPUT_CLASSES + " text-right tabular-nums",
                    "data-item-quantity": "",
                    "aria-label": "Quantité",
                }
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "inputmode": "decimal",
                    "class": INPUT_CLASSES + " text-right tabular-nums",
                    "data-item-price": "",
                    "aria-label": "Prix unitaire",
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("La quantité doit être strictement positive.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price is not None and unit_price < 0:
            raise forms.ValidationError("Le prix unitaire ne peut pas être négatif.")
        return unit_price


QuoteItemFormSet = inlineformset_factory(
    Quote,
    QuoteItem,
    form=QuoteItemForm,
    extra=2,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


def posted_totals(form, formset) -> tuple[Decimal, Decimal]:
    """Sous-total et total calculés à partir des données validées du formulaire.

    Sert uniquement à vérifier la cohérence réduction/acompte avant écriture :
    les montants enregistrés sont toujours recalculés depuis la base.
    """
    subtotal = Decimal("0.00")
    for item_form in formset.forms:
        cleaned = getattr(item_form, "cleaned_data", None)
        if not cleaned or cleaned.get("DELETE"):
            continue
        quantity = cleaned.get("quantity") or Decimal("0")
        unit_price = cleaned.get("unit_price") or Decimal("0")
        subtotal += (quantity * unit_price).quantize(Decimal("0.01"))
    total = (
        subtotal
        - (form.cleaned_data.get("discount") or Decimal("0"))
        + (form.cleaned_data.get("transport_cost") or Decimal("0"))
    )
    return subtotal, total
