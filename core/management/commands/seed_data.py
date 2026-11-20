"""Commande : charge les fausses données depuis config/seed.json.

Usage :
    uv run python manage.py seed_data
    uv run python manage.py seed_data --wipe   # repart de zéro (devis conservés)

Couvre : entreprise (nom, présentation, mission, vision, contacts), catégories,
réalisations + galerie, services. Les devis ne sont jamais lus ni écrits.
Les images absentes de media/ sont ignorées : on peut relancer après dépôt.
"""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Achievement, AchievementImage, Company, EventCategory, Service

DEFAULT_CONFIG = Path(settings.BASE_DIR) / "config" / "seed.json"

COMPANY_FIELDS = (
    "name",
    "presentation",
    "mission",
    "vision",
    "location",
    "phones",
    "whatsapp",
    "email",
    "social_links",
)


class Command(BaseCommand):
    help = (
        "Charge les fausses données (entreprise, catégories, réalisations, services) "
        "depuis config/seed.json. Les devis ne sont jamais modifiés."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            default=str(DEFAULT_CONFIG),
            help="Fichier JSON de configuration (défaut : config/seed.json).",
        )
        parser.add_argument(
            "--wipe",
            action="store_true",
            help=(
                "Supprime d'abord entreprises, catégories, réalisations et services. "
                "Les devis et comptes sont conservés."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["config"])
        if not path.is_file():
            raise CommandError(f"Fichier de configuration introuvable : {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"JSON invalide dans {path} : {exc}") from exc

        if options["wipe"]:
            self._wipe()

        stats = {
            "company": [0, 0],
            "categories": [0, 0],
            "achievements": [0, 0],
            "services": [0, 0],
            "images": 0,
        }
        missing: list[str] = []

        self._seed_company(data.get("company") or {}, stats, missing)
        categories = self._seed_categories(data.get("categories") or [], stats, missing)
        self._seed_achievements(
            data.get("achievements") or [], categories, stats, missing
        )
        self._seed_services(data.get("services") or [], stats, missing)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Seed terminé ({path}) :"))
        self.stdout.write(f"  entreprise : {self._fmt(stats['company'])}")
        self.stdout.write(f"  catégories : {self._fmt(stats['categories'])}")
        self.stdout.write(
            f"  réalisations : {self._fmt(stats['achievements'])} "
            f"(+ {stats['images']} image(s) ajoutée(s))"
        )
        self.stdout.write(f"  services : {self._fmt(stats['services'])}")

        if missing:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    f"Images introuvables dans media/ ({len(missing)}) — "
                    "déposez les fichiers puis relancez seed_data :"
                )
            )
            for rel in missing:
                self.stdout.write(f"  - media/{rel}")
        else:
            self.stdout.write(self.style.SUCCESS("Toutes les images sont en place."))

    @staticmethod
    def _fmt(pair: list[int]) -> str:
        created, updated = pair
        parts = []
        if created:
            parts.append(f"{created} créée(s)")
        if updated:
            parts.append(f"{updated} mise(s) à jour")
        return ", ".join(parts) if parts else "inchangé"

    @staticmethod
    def _bump(stats: dict, key: str, created: bool) -> None:
        stats[key][0 if created else 1] += 1

    @staticmethod
    def _file_exists(rel: str) -> bool:
        return bool(rel) and (Path(settings.MEDIA_ROOT) / rel).exists()

    def _wipe(self) -> None:
        Achievement.objects.all().delete()
        EventCategory.objects.all().delete()
        Service.objects.all().delete()
        Company.objects.all().delete()
        self.stdout.write(
            "Données de contenu effacées (devis et comptes conservés)."
        )

    def _seed_company(self, cfg: dict, stats: dict, missing: list[str]) -> None:
        if not cfg:
            return
        company = Company.get_solo()
        created = company is None
        if created:
            company = Company()
        for field in COMPANY_FIELDS:
            if field in cfg:
                setattr(company, field, cfg[field])
        logo = cfg.get("logo")
        if logo:
            if self._file_exists(logo):
                company.logo = logo
            else:
                missing.append(logo)
        company.save()
        self._bump(stats, "company", created)
        self.stdout.write(
            f"Entreprise : {company.name} "
            f"({'créée' if created else 'mise à jour'})"
        )

    def _seed_categories(
        self, items: list[dict], stats: dict, missing: list[str]
    ) -> dict[str, EventCategory]:
        result: dict[str, EventCategory] = {}
        for item in items:
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            obj, created = EventCategory.objects.get_or_create(name=name)
            changed = False
            if "is_active" in item and obj.is_active != item["is_active"]:
                obj.is_active = item["is_active"]
                changed = True
            cover = item.get("cover_image")
            if cover:
                if self._file_exists(cover):
                    if obj.cover_image.name != cover:
                        obj.cover_image = cover
                        changed = True
                else:
                    missing.append(cover)
            if created or changed:
                obj.save()
            self._bump(stats, "categories", created)
            result[name] = obj
        return result

    def _seed_achievements(
        self,
        items: list[dict],
        categories: dict[str, EventCategory],
        stats: dict,
        missing: list[str],
    ) -> None:
        for item in items:
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            cat_name = str(item.get("category") or "").strip()
            category = categories.get(cat_name)
            if category is None:
                raise CommandError(
                    f"Réalisation « {title} » : catégorie inconnue « {cat_name} »."
                )
            obj = Achievement.objects.filter(title=title).first()
            created = obj is None
            if created:
                obj = Achievement.objects.create(
                    title=title,
                    category=category,
                    is_active=item.get("is_active", True),
                )
            else:
                changed = False
                if obj.category_id != category.id:
                    obj.category = category
                    changed = True
                if "is_active" in item and obj.is_active != item["is_active"]:
                    obj.is_active = item["is_active"]
                    changed = True
                if changed:
                    obj.save()
            self._bump(stats, "achievements", created)

            existing = set(obj.images.values_list("image", flat=True))
            for rel in item.get("images") or []:
                if rel in existing:
                    continue
                if self._file_exists(rel):
                    AchievementImage.objects.create(achievement=obj, image=rel)
                    stats["images"] += 1
                else:
                    missing.append(rel)

    def _seed_services(self, items: list[dict], stats: dict, missing: list[str]) -> None:
        for item in items:
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            obj = Service.objects.filter(title=title).first()
            created = obj is None
            if created:
                obj = Service(title=title)
            if "description" in item:
                obj.description = item["description"] or ""
            if "is_active" in item:
                obj.is_active = item["is_active"]
            cover = item.get("cover_image")
            if cover:
                if self._file_exists(cover):
                    if obj.cover_image.name != cover:
                        obj.cover_image = cover
                else:
                    missing.append(cover)
            obj.save()
            self._bump(stats, "services", created)
