"""Кошик і промокоди застосунку доставки їжі «Смакота».

User story FOOD-18: «Як користувач, я хочу ввести промокод,
щоб отримати знижку на замовлення».
Критерії приймання:
  1. Дійсний промокод зменшує суму замовлення на відсоток або фіксовану суму.
  2. Недійсний або прострочений промокод показує повідомлення про помилку.
  3. Промокод не діє, якщо сума замовлення менша за мінімальну для нього.
  4. Сума до сплати не може бути від’ємною.
"""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

# код -> (тип знижки, розмір, діє до, мінімальна сума замовлення)
PROMO_CODES = {
    "SMAKOTA10": ("percent", Decimal("10"), date(2026, 12, 31), Decimal("200")),
    "WELCOME50": ("fixed", Decimal("50"), date(2026, 11, 30), Decimal("300")),
    "AUTUMN15": ("percent", Decimal("15"), date(2026, 10, 31), Decimal("0")),
}


class CartError(ValueError):
    """Некоректна операція з кошиком."""


class PromoError(ValueError):
    """Промокод не можна застосувати."""


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Cart:
    def __init__(self):
        self._items = {}

    def add(self, dish_id, name, price, qty=1):
        if not isinstance(qty, int) or qty <= 0:
            raise CartError("Кількість має бути додатним цілим числом")
        price = money(price)
        if price <= 0:
            raise CartError("Ціна страви має бути більшою за нуль")
        old = self._items.get(dish_id, {"qty": 0})["qty"]
        self._items[dish_id] = {"name": name, "price": price, "qty": old + qty}

    def subtotal(self):
        return money(sum((i["price"] * i["qty"] for i in self._items.values()), Decimal("0")))

    def total_with_promo(self, code, today=None):
        """Сума до сплати після застосування промокоду."""
        today = today or date.today()
        key = (code or "").strip().upper()
        if key not in PROMO_CODES:
            raise PromoError("Промокод недійсний")
        kind, value, valid_until, min_order = PROMO_CODES[key]
        if today > valid_until:
            raise PromoError("Термін дії промокоду минув")
        subtotal = self.subtotal()
        if subtotal < min_order:
            raise PromoError(f"Промокод діє для замовлень від {min_order} грн")
        if kind == "percent":
            discount = subtotal * value / 100
        else:
            discount = value
        return max(money(subtotal - discount), Decimal("0.00"))
