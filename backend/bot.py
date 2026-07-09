import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo,
)
from sqlalchemy import select

from database import SessionLocal
from models import Order, User

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("kivo-bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0") or 0)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.com")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()

# status -> (label shown to admin/customer, next status, button text)
STATUS_FLOW = [
    ("pending", "confirmed", "✅ Confirm"),
    ("confirmed", "packed", "📦 Packed"),
    ("packed", "shipped", "🚚 Shipped"),
    ("shipped", "delivered", "✅ Delivered"),
]
STATUS_LABEL_UZ = {
    "pending": "Kutilmoqda",
    "confirmed": "Tasdiqlandi",
    "packed": "Yig'ildi",
    "shipped": "Yo'lda",
    "delivered": "Yetkazildi",
}


def admin_keyboard(order_id: int, current_status: str) -> InlineKeyboardMarkup | None:
    for cur, nxt, label in STATUS_FLOW:
        if cur == current_status:
            return InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=label, callback_data=f"order:{order_id}:{nxt}")
            ]])
    return None  # delivered = final state, no more buttons


def order_admin_text(order: Order) -> str:
    lines = [f"🆕 Buyurtma #{order.id:04d}", ""]
    lines.append(f"👤 {order.name}")
    lines.append(f"📞 {order.phone}")
    lines.append(f"📍 {order.address}")
    if order.comment:
        lines.append(f"💬 {order.comment}")
    lines.append("")
    for item in order.items:
        lines.append(f"• {item.name} x{item.qty} — {item.price:,} so'm".replace(",", " "))
    lines.append("")
    lines.append(f"💰 Jami: {order.total:,} so'm".replace(",", " "))
    lines.append(f"Holat: {STATUS_LABEL_UZ.get(order.status, order.status)}")
    return "\n".join(lines)


async def notify_admin_new_order(order: Order):
    if not bot or not ADMIN_CHAT_ID:
        log.warning("Bot yoki ADMIN_CHAT_ID sozlanmagan — admin xabari yuborilmadi")
        return
    msg = await bot.send_message(
        ADMIN_CHAT_ID,
        order_admin_text(order),
        reply_markup=admin_keyboard(order.id, order.status),
    )
    async with SessionLocal() as session:
        db_order = await session.get(Order, order.id)
        db_order.admin_message_id = msg.message_id
        await session.commit()


async def notify_customer_status(order: Order):
    if not bot:
        return
    async with SessionLocal() as session:
        user = await session.get(User, order.user_id)
    if not user:
        return
    text = {
        "confirmed": f"✅ Buyurtma #{order.id:04d} tasdiqlandi. Tez orada tayyorlanadi.",
        "packed": f"📦 Buyurtma #{order.id:04d} qadoqlandi.",
        "shipped": f"🚚 Buyurtma #{order.id:04d} yo'lda!",
        "delivered": f"🎉 Buyurtma #{order.id:04d} yetkazildi. KIVO NEST'ni tanlaganingiz uchun rahmat!",
    }.get(order.status)
    if text:
        try:
            await bot.send_message(user.telegram_id, text)
        except Exception as e:
            log.warning(f"Mijozga xabar yuborib bo'lmadi: {e}")


@dp.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✨ Enter Store", web_app=WebAppInfo(url=WEBAPP_URL))
    ]])
    await message.answer(
        "KIVO NEST\nCurated Workspace & Tech\n\n"
        "Biz ko'p mahsulot sotmaymiz. Biz eng yaxshi mahsulotlarni tanlaymiz.",
        reply_markup=kb,
    )


@dp.callback_query(F.data.startswith("order:"))
async def order_status_callback(callback: CallbackQuery):
    _, order_id_str, new_status = callback.data.split(":")
    order_id = int(order_id_str)

    async with SessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            await callback.answer("Buyurtma topilmadi", show_alert=True)
            return

        order.status = new_status
        await session.commit()
        await session.refresh(order)
        # load items for the updated text
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        )
        order = result.scalar_one()

    try:
        await callback.message.edit_text(
            order_admin_text(order),
            reply_markup=admin_keyboard(order.id, order.status),
        )
    except Exception:
        pass

    await callback.answer(f"Holat yangilandi: {STATUS_LABEL_UZ.get(new_status, new_status)}")
    await notify_customer_status(order)
