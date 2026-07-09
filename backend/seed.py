from sqlalchemy import select
from database import SessionLocal
from models import Product

CATEGORIES = [
    {"key": "workspace", "label": "Workspace", "icon": "💻"},
    {"key": "keyboards", "label": "Keyboards", "icon": "⌨️"},
    {"key": "mouse", "label": "Mouse", "icon": "🖱"},
    {"key": "usb_hub", "label": "USB Hub", "icon": "🔌"},
    {"key": "lighting", "label": "Lighting", "icon": "💡"},
    {"key": "audio", "label": "Audio", "icon": "🎧"},
    {"key": "organizers", "label": "Organizers", "icon": "📦"},
]

# Each entry: (category, group_key, group_label)
GROUPS = [
    ("workspace", "laptop_stand", "Laptop Stand"),
    ("keyboards", "keyboard", "Mechanical Keyboard"),
    ("mouse", "mouse", "Wireless Mouse"),
    ("usb_hub", "usb_hub", "USB-C Hub"),
    ("lighting", "desk_lamp", "Desk Lamp"),
    ("audio", "headphones", "Headphones"),
    ("organizers", "cable_organizer", "Cable Organizer"),
]

TIER_META = {
    "essential": {"badge": "🥉 Essential", "price_mult": 0.55, "score_mult": 0.80},
    "recommended": {"badge": "⭐ Recommended", "price_mult": 1.0, "score_mult": 0.96},
    "premium": {"badge": "👑 Premium", "price_mult": 1.9, "score_mult": 1.0},
}

BASE_PRICE = {
    "laptop_stand": 349000,
    "keyboard": 620000,
    "mouse": 290000,
    "usb_hub": 340000,
    "desk_lamp": 410000,
    "headphones": 890000,
    "cable_organizer": 95000,
}

WHY = {
    "essential": ["Yaxshi boshlang'ich tanlov", "Narxi qulay", "Kunlik ishlatish uchun yetarli"],
    "recommended": ["Narx va sifat balansi", "Ko'pchilik uchun eng mos", "Uzoq muddat xizmat qiladi"],
    "premium": ["Eng yuqori sifat materiallari", "Professional foydalanish uchun", "Uzoq muddatli investitsiya"],
}

NOT_FOR = {
    "essential": ["Siz professional darajada ishlatmoqchi bo'lsangiz", "Uzoq muddat kafolat kerak bo'lsa"],
    "recommended": ["Siz eng arzon variantni izlasangiz"],
    "premium": ["Byudjetingiz cheklangan bo'lsa", "Kunlik oddiy foydalanish uchun yetarlicha ortiqcha"],
}

TAGS_BY_GROUP = {
    "laptop_stand": "laptop stand aluminium ergonomic desk university student office",
    "keyboard": "keyboard mechanical typing office gaming student",
    "mouse": "mouse wireless ergonomic office portable university",
    "usb_hub": "usb hub type-c dock adapter laptop portability",
    "desk_lamp": "lamp lighting desk led eye-care study",
    "headphones": "headphones audio noise-cancelling music calls university",
    "cable_organizer": "organizer cable desk tidy accessories",
}


async def seed_if_empty():
    async with SessionLocal() as session:
        existing = (await session.execute(select(Product).limit(1))).first()
        if existing:
            return

        products = []
        for category, group_key, label in GROUPS:
            base_price = BASE_PRICE[group_key]
            for i, tier in enumerate(["essential", "recommended", "premium"]):
                meta = TIER_META[tier]
                price = int(round(base_price * meta["price_mult"] / 1000) * 1000)
                pq = round(9.6 * meta["score_mult"], 1)
                build = round(9.8 * meta["score_mult"], 1)
                design = round(9.5 * meta["score_mult"], 1)
                dur = round(9.4 * meta["score_mult"], 1)
                kivo = round((pq + build + design + dur) / 4, 1)

                products.append(Product(
                    name=f"{label} — {meta['badge'].split(' ',1)[1]}",
                    category=category,
                    group_key=group_key,
                    tier=tier,
                    price=price,
                    image_urls=[f"https://picsum.photos/seed/{group_key}{i}/800/800"],
                    why_recommend=WHY[tier],
                    not_for_you=NOT_FOR[tier],
                    tags=TAGS_BY_GROUP[group_key],
                    models_considered=56,
                    price_quality_score=pq,
                    build_score=build,
                    design_score=design,
                    durability_score=dur,
                    kivo_score=kivo,
                    is_choice=(group_key == "laptop_stand" and tier == "recommended"),
                    is_featured=(tier == "recommended" and group_key in ("laptop_stand", "keyboard", "headphones")),
                    in_stock=True,
                ))

        session.add_all(products)
        await session.commit()
