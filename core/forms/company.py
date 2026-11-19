from django import forms

from ..models import Company
from .content import FILE_CLASSES, INPUT_CLASSES


class CompanyForm(forms.ModelForm):
    """Fiche entreprise : contacts par ligne et réseaux sociaux par ligne."""

    phones = forms.CharField(
        label="Numéros de contact",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "+237 600 000 000",
                "class": INPUT_CLASSES,
            }
        ),
        required=False,
        help_text="Un numéro par ligne.",
    )
    social_links = forms.CharField(
        label="Réseaux sociaux",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Facebook | https://facebook.com/votrepage\nInstagram | https://instagram.com/votrepage",
                "class": INPUT_CLASSES,
            }
        ),
        required=False,
        help_text="Un lien par ligne, au format : Nom | URL",
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
            "social_links",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "logo": forms.ClearableFileInput(
                attrs={"class": FILE_CLASSES, "accept": "image/*", "data-preview": "company-logo"}
            ),
            "presentation": forms.Textarea(
                attrs={"rows": 4, "class": INPUT_CLASSES}
            ),
            "mission": forms.Textarea(attrs={"rows": 3, "class": INPUT_CLASSES}),
            "vision": forms.Textarea(attrs={"rows": 3, "class": INPUT_CLASSES}),
            "location": forms.TextInput(
                attrs={"placeholder": "Ville, quartier…", "class": INPUT_CLASSES}
            ),
            "whatsapp": forms.TextInput(
                attrs={"placeholder": "600000000", "class": INPUT_CLASSES}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "contact@example.com", "class": INPUT_CLASSES}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if isinstance(self.instance.phones, list):
                self.initial["phones"] = "\n".join(self.instance.phone_list)
            if isinstance(self.instance.social_links, list):
                self.initial["social_links"] = "\n".join(
                    f"{link.get('label', '')} | {link.get('url', '')}".strip(" |")
                    for link in self.instance.social_links
                    if isinstance(link, dict) and link.get("url")
                )

    def clean_phones(self):
        raw = self.cleaned_data.get("phones") or ""
        phones = [line.strip() for line in raw.splitlines() if line.strip()]
        for phone in phones:
            if len(phone) > 40:
                raise forms.ValidationError(f"Numéro trop long : {phone}")
        return phones

    def clean_social_links(self):
        raw = self.cleaned_data.get("social_links") or ""
        links = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" not in line:
                raise forms.ValidationError(
                    f"Ligne invalide « {line} » : utilisez le format Nom | URL."
                )
            label, _, url = (part.strip() for part in line.partition("|"))
            if not url.startswith(("http://", "https://")):
                raise forms.ValidationError(
                    f"L'adresse « {url} » doit commencer par http:// ou https://."
                )
            links.append({"label": label or url, "url": url})
        return links
