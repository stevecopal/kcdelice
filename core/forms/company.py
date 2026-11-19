from django import forms

from ..models import Company


class CompanyForm(forms.ModelForm):
    """Un numéro de contact par ligne pour la fiche entreprise."""

    phones = forms.CharField(
        label="Numéros de contact",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "+237 600 000 000",
                "class": (
                    "w-full rounded-xl bg-neutral-100 px-4 py-3 text-noir "
                    "placeholder:text-neutral-400 focus:outline-none focus:ring-2 "
                    "focus:ring-vert/40"
                ),
            }
        ),
        required=False,
        help_text="Un numéro par ligne.",
    )

    class Meta:
        model = Company
        fields = [
            "name",
            "logo",
            "presentation",
            "mission",
            "vision",
            "location",
            "phones",
            "whatsapp",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and isinstance(self.instance.phones, list):
            self.initial["phones"] = "\n".join(self.instance.phone_list)

    def clean_phones(self):
        raw = self.cleaned_data.get("phones") or ""
        phones = [line.strip() for line in raw.splitlines() if line.strip()]
        for phone in phones:
            if len(phone) > 40:
                raise forms.ValidationError(f"Numéro trop long : {phone}")
        return phones
