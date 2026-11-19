import uuid
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def populate_existing_rows(apps, schema_editor):
    """Donne une référence aux devis existants et recalcule leurs montants."""
    Quote = apps.get_model("devis", "Quote")
    QuoteItem = apps.get_model("devis", "QuoteItem")

    counters = {}
    for quote in Quote.objects.order_by("created_at", "pk"):
        year = quote.created_at.year if quote.created_at else 2026
        counters[year] = counters.get(year, 0) + 1
        quote.reference = f"DEV-{year}-{counters[year]:04d}"
        quote.save(update_fields=["reference"])

    for item in QuoteItem.objects.all():
        item.total_price = (item.quantity * item.unit_price).quantize(Decimal("0.01"))
        item.save(update_fields=["total_price"])

    for quote in Quote.objects.all():
        items = QuoteItem.objects.filter(quote=quote)
        subtotal = sum((item.total_price for item in items), Decimal("0.00"))
        quote.subtotal = subtotal
        quote.total_amount = subtotal - quote.discount + quote.transport_cost
        quote.save(update_fields=["subtotal", "total_amount"])


class Migration(migrations.Migration):

    dependencies = [
        ("devis", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="quoteitem",
            old_name="label",
            new_name="title",
        ),
        migrations.AlterField(
            model_name="quoteitem",
            name="title",
            field=models.CharField(max_length=200, verbose_name="désignation"),
        ),
        migrations.AddField(
            model_name="quoteitem",
            name="total_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                editable=False,
                max_digits=14,
                verbose_name="total de la ligne",
            ),
        ),
        migrations.AlterField(
            model_name="quoteitem",
            name="quantity",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("1"),
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                verbose_name="quantité",
            ),
        ),
        migrations.AlterField(
            model_name="quoteitem",
            name="unit_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0"),
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                verbose_name="prix unitaire",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="reference",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                max_length=30,
                verbose_name="référence",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="quote",
            name="title",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="objet"
            ),
        ),
        migrations.AlterField(
            model_name="quote",
            name="client_name",
            field=models.CharField(max_length=200, verbose_name="nom du client"),
        ),
        migrations.AlterField(
            model_name="quote",
            name="client_phone",
            field=models.CharField(
                max_length=40, verbose_name="téléphone du client"
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="client_address",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="adresse du client"
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="event_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="date de l'événement"
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="event_location",
            field=models.CharField(
                default="", max_length=255, verbose_name="lieu de l'événement"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="quote",
            name="subtotal",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=14,
                verbose_name="sous-total",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="discount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=14,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                verbose_name="réduction",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="transport_cost",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=14,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                verbose_name="frais de transport",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="total_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=14,
                verbose_name="montant total",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="deposit_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=14,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                verbose_name="acompte prévu",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Brouillon"),
                    ("sent", "Envoyé"),
                    ("accepted", "Accepté"),
                    ("refused", "Refusé"),
                    ("converted", "Converti en commande"),
                ],
                default="draft",
                max_length=20,
                verbose_name="statut",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="valid_until",
            field=models.DateField(
                blank=True, null=True, verbose_name="valable jusqu'au"
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="notes",
            field=models.TextField(blank=True, verbose_name="conditions particulières"),
        ),
        migrations.RunPython(populate_existing_rows, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="quote",
            name="reference",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=30,
                unique=True,
                verbose_name="référence",
            ),
        ),
        migrations.AlterModelOptions(
            name="quote",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "devis",
                "verbose_name_plural": "devis",
            },
        ),
        migrations.AddConstraint(
            model_name="quoteitem",
            constraint=models.CheckConstraint(
                condition=models.Q(("quantity__gt", 0)),
                name="quote_item_quantity_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="quoteitem",
            constraint=models.CheckConstraint(
                condition=models.Q(("unit_price__gte", 0)),
                name="quote_item_unit_price_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="quote",
            constraint=models.CheckConstraint(
                condition=models.Q(("discount__gte", 0)),
                name="quote_discount_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="quote",
            constraint=models.CheckConstraint(
                condition=models.Q(("transport_cost__gte", 0)),
                name="quote_transport_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="quote",
            constraint=models.CheckConstraint(
                condition=models.Q(("deposit_amount__gte", 0)),
                name="quote_deposit_non_negative",
            ),
        ),
    ]
