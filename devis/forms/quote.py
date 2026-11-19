from django import forms

from ..models import Quote, QuoteItem

INPUT_CLASSES = (
    "w-full rounded-xl bg-neutral-100 px-4 py-3 text-noir "
    "placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-vert/40"
)


class QuoteForm(forms.ModelForm):
    """Formulaire bref : titre + client facultatif."""

    class Meta:
        model = Quote
        fields = ["title", "client_name", "client_phone", "client_email"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Ex. : Organisation anniversaire",
                    "class": INPUT_CLASSES,
                }
            ),
            "client_name": forms.TextInput(
                attrs={"placeholder": "Facultatif", "class": INPUT_CLASSES}
            ),
            "client_phone": forms.TextInput(
                attrs={"placeholder": "Facultatif", "class": INPUT_CLASSES}
            ),
            "client_email": forms.EmailInput(
                attrs={"placeholder": "Facultatif", "class": INPUT_CLASSES}
            ),
        }

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Le titre est obligatoire.")
        return title

    def clean_client_email(self):
        email = (self.cleaned_data.get("client_email") or "").strip()
        return email


class QuoteItemForm(forms.ModelForm):
    """Ligne de devis : désignation, quantité, prix unitaire."""

    class Meta:
        model = QuoteItem
        fields = ["label", "quantity", "unit_price"]
        widgets = {
            "label": forms.TextInput(
                attrs={
                    "placeholder": "Ex. : Salle, traiteur, décoration",
                    "class": INPUT_CLASSES,
                }
            ),
            "quantity": forms.NumberInput(
                attrs={"min": "0.01", "step": "0.01", "class": INPUT_CLASSES}
            ),
            "unit_price": forms.NumberInput(
                attrs={"min": "0", "step": "0.01", "class": INPUT_CLASSES}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        quantity = cleaned.get("quantity")
        unit_price = cleaned.get("unit_price")
        if quantity is not None and quantity <= 0:
            self.add_error("quantity", "La quantité doit être supérieure à 0.")
        if unit_price is not None and unit_price < 0:
            self.add_error("unit_price", "Le prix unitaire ne peut pas être négatif.")
        return cleaned
