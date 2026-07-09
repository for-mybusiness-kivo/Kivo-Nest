import asyncio
import os
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database import init_db, get_session, SessionLocal
from models import Product, User, Favorite, CartItem, Order, OrderItem
from schemas import ProductOut, ProductCard, CartAddIn, CheckoutIn
from auth import validate_init_data, dev_fallback_user
from seed import seed_if_empty, CATEGORIES
import bot as botmod

log = logging.getLogger("kivo-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_if_empty()
    polling_task = None
    if botmod.bot:
        polling_task = asyncio.create_task(botmod.dp.start_polling(botmod.bot))
        log.info("Telegram bot polling started")
    else:
        log.warning("BOT_TOKEN yo'q — bot ishga tushmadi (faqat API/Mini App test rejimida)")
    yield
    if polling_task:
        polling_task.cancel()


app = FastAPI(title="KIVO NEST", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- auth dependency ----------

async def get_current_user(
    x_telegram_init_data: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    tg_user = validate_init_data(x_telegram_init_data) if x_telegram_init_data else None
    if not tg_user:
        # local/dev fallback so the Mini App also works in a plain browser while building
        if os.getenv("ALLOW_DEV_AUTH", "1") == "1":
            tg_user = dev_fallback_user()
        else:
            raise HTTPException(401, "Invalid Telegram init data")

    result = await session.execute(select(User).where(User.telegram_id == tg_user["id"]))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=tg_user["id"],
            username=tg_user.get("username"),
            full_name=f"{tg_user.get('first_name','')} {tg_user.get('last_name','')}".strip(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


# ---------- categories & home ----------

@app.get("/api/categories")
async def get_categories():
    return CATEGORIES


@app.get("/api/home")
async def get_home(session: AsyncSession = Depends(get_session)):
    featured = (await session.execute(
        select(Product).where(Product.is_featured == True).limit(3)
    )).scalars().all()
    choice = (await session.execute(
        select(Product).where(Product.is_choice == True).limit(1)
    )).scalars().first()
    return {
        "featured": [ProductCard.model_validate(p) for p in featured],
        "choice": ProductOut.model_validate(choice) if choice else None,
    }


# ---------- products ----------

@app.get("/api/products")
async def list_products(category: str | None = None, session: AsyncSession = Depends(get_session)):
    q = select(Product)
    if category:
        q = q.where(Product.category == category)
    products = (await session.execute(q)).scalars().all()
    grouped = {"essential": [], "recommended": [], "premium": []}
    for p in products:
        if p.tier in grouped:
            grouped[p.tier].append(ProductCard.model_validate(p))
    return grouped


@app.get("/api/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    p = await session.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    return p


@app.get("/api/products/{product_id}/compare")
async def compare_group(product_id: int, session: AsyncSession = Depends(get_session)):
    p = await session.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    siblings = (await session.execute(
        select(Product).where(Product.group_key == p.group_key)
    )).scalars().all()
    order = {"essential": 0, "recommended": 1, "premium": 2}
    siblings.sort(key=lambda x: order.get(x.tier, 9))
    return [ProductOut.model_validate(s) for s in siblings]


# ---------- AI search ----------

async def claude_extract_tags(query: str) -> list[str] | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=api_key)
        resp = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    "A user is browsing a curated tech/workspace store called KIVO NEST. "
                    f'Their search query is: "{query}"\n\n'
                    "Return ONLY a JSON array (no prose, no markdown fences) of 3-8 lowercase "
                    "English keywords describing what products would help them "
                    "(e.g. product types, use-case words). Example: "
                    '["laptop stand", "keyboard", "mouse", "university", "portable"]'
                ),
            }],
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        text = text.strip().strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
        tags = json.loads(text)
        if isinstance(tags, list):
            return [str(t).lower() for t in tags]
    except Exception as e:
        log.warning(f"Claude search fallback (heuristic used): {e}")
    return None


@app.get("/api/search")
async def search(q: str, session: AsyncSession = Depends(get_session)):
    q = q.strip()
    if not q:
        return []

    tags = await claude_extract_tags(q)
    keywords = tags if tags else [w.lower() for w in q.replace(",", " ").split() if len(w) > 2]

    products = (await session.execute(
        select(Product).where(Product.tier == "recommended")
    )).scalars().all()

    scored = []
    for p in products:
        haystack = f"{p.name} {p.category} {p.tags}".lower()
        score = sum(1 for kw in keywords if kw in haystack)
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: -x[0])
    return [ProductCard.model_validate(p) for _, p in scored[:10]]


# ---------- favorites ----------

@app.get("/api/favorites")
async def list_favorites(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    favs = (await session.execute(
        select(Product).join(Favorite, Favorite.product_id == Product.id)
        .where(Favorite.user_id == user.id)
    )).scalars().all()
    return [ProductCard.model_validate(p) for p in favs]


@app.post("/api/favorites/toggle/{product_id}")
async def toggle_favorite(product_id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    existing = (await session.execute(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.product_id == product_id)
    )).scalar_one_or_none()
    if existing:
        await session.delete(existing)
        await session.commit()
        return {"favorited": False}
    session.add(Favorite(user_id=user.id, product_id=product_id))
    await session.commit()
    return {"favorited": True}


# ---------- cart ----------

@app.get("/api/cart")
async def get_cart(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(CartItem, Product).join(Product, Product.id == CartItem.product_id)
        .where(CartItem.user_id == user.id)
    )).all()
    items = [{
        "cart_item_id": ci.id, "product": ProductCard.model_validate(p), "qty": ci.qty
    } for ci, p in rows]
    total = sum(i["product"].price * i["qty"] for i in items)
    return {"items": items, "total": total}


@app.post("/api/cart/add")
async def add_to_cart(body: CartAddIn, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    existing = (await session.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == body.product_id)
    )).scalar_one_or_none()
    if existing:
        existing.qty += body.qty
    else:
        session.add(CartItem(user_id=user.id, product_id=body.product_id, qty=body.qty))
    await session.commit()
    return {"ok": True}


@app.post("/api/cart/remove/{cart_item_id}")
async def remove_from_cart(cart_item_id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    item = await session.get(CartItem, cart_item_id)
    if item and item.user_id == user.id:
        await session.delete(item)
        await session.commit()
    return {"ok": True}


# ---------- checkout ----------

@app.post("/api/orders")
async def checkout(body: CheckoutIn, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(CartItem, Product).join(Product, Product.id == CartItem.product_id)
        .where(CartItem.user_id == user.id)
    )).all()
    if not rows:
        raise HTTPException(400, "Cart is empty")

    total = sum(p.price * ci.qty for ci, p in rows)
    order = Order(
        user_id=user.id,
        name=body.name,
        phone=body.phone,
        address=body.address,
        location_lat=body.location_lat,
        location_lng=body.location_lng,
        comment=body.comment,
        promo_code=body.promo_code,
        total=total,
    )
    session.add(order)
    await session.flush()

    for ci, p in rows:
        session.add(OrderItem(order_id=order.id, product_id=p.id, name=p.name, price=p.price, qty=ci.qty))
        await session.delete(ci)

    await session.commit()

    result = await session.execute(
        select(Order).where(Order.id == order.id).options(selectinload(Order.items))
    )
    order = result.scalar_one()

    asyncio.create_task(botmod.notify_admin_new_order(order))

    return {"order_id": order.id, "total": order.total}


# ---------- static frontend (Mini App) ----------

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
