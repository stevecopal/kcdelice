from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from ..forms import QuoteForm, QuoteItemFormSet, posted_totals
from ..models import Quote


class QuoteFormView(LoginRequiredMixin, TemplateView):
    """Création d'un devis, ou modification d'un brouillon, avec lignes dynamiques."""

    template_name = "devis/quote_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.quote = None
        if kwargs.get("pk"):
            self.quote = get_object_or_404(Quote, pk=kwargs["pk"])
            if not self.quote.is_editable:
                messages.error(
                    request,
                    "Un devis envoyé ou finalisé ne peut plus être modifié.",
                )
                return redirect("quote_detail", pk=self.quote.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", QuoteForm(instance=self.quote))
        context.setdefault(
            "formset",
            QuoteItemFormSet(instance=self.quote, prefix="items"),
        )
        context["quote"] = self.quote
        return context

    def post(self, request, *args, **kwargs):
        form = QuoteForm(request.POST, instance=self.quote)
        formset = QuoteItemFormSet(
            request.POST, instance=self.quote or Quote(), prefix="items"
        )

        if form.is_valid() and formset.is_valid():
            subtotal, total = posted_totals(form, formset)
            if not self._has_lines(formset):
                form.add_error(None, "Ajoutez au moins une ligne au devis.")
            elif form.cleaned_data.get("discount", 0) > subtotal:
                form.add_error(
                    "discount", "La réduction ne peut pas dépasser le sous-total."
                )
            elif form.cleaned_data.get("deposit_amount", 0) > total:
                form.add_error(
                    "deposit_amount",
                    "L'acompte ne peut pas dépasser le montant total du devis.",
                )
            else:
                quote = self._save(form, formset)
                messages.success(
                    request,
                    f"Devis {quote.reference} "
                    + ("mis à jour." if self.quote else "créé avec succès."),
                )
                return redirect("quote_detail", pk=quote.pk)

        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    @staticmethod
    def _has_lines(formset) -> bool:
        return any(
            (item_form.cleaned_data.get("title") or "").strip()
            for item_form in formset.forms
            if item_form.cleaned_data and not item_form.cleaned_data.get("DELETE")
        )

    @staticmethod
    def _save(form, formset) -> Quote:
        with transaction.atomic():
            quote = form.save()
            formset.instance = quote
            formset.save()
            quote.recalculate()
        return quote
