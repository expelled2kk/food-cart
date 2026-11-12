"""Модульні тести для FOOD-18 «Застосування промокоду»."""
from datetime import date
from decimal import Decimal

import pytest

from cart import Cart, CartError, PromoError

TODAY = date(2026, 11, 12)


@pytest.fixture
def cart():
    c = Cart()
    c.add("p1", "Піца Маргарита", 189)
    c.add("s1", "Борщ", 95, qty=2)      # разом 379 грн
    return c


def test_subtotal(cart):
    assert cart.subtotal() == Decimal("379.00")


def test_percent_promo(cart):
    """Критерій 1: відсоткова знижка 10 %."""
    assert cart.total_with_promo("SMAKOTA10", TODAY) == Decimal("341.10")


def test_fixed_promo(cart):
    """Критерій 1: фіксована знижка 50 грн."""
    assert cart.total_with_promo("WELCOME50", TODAY) == Decimal("329.00")


def test_code_is_case_insensitive(cart):
    assert cart.total_with_promo("  smakota10 ", TODAY) == Decimal("341.10")


def test_unknown_code(cart):
    """Критерій 2: недійсний промокод."""
    with pytest.raises(PromoError, match="недійсний"):
        cart.total_with_promo("FREEFOOD", TODAY)


def test_expired_code(cart):
    """Критерій 2: прострочений промокод (діяв до 31.10.2026)."""
    with pytest.raises(PromoError, match="минув"):
        cart.total_with_promo("AUTUMN15", TODAY)


def test_last_valid_day(cart):
    """Граничний випадок: останній день дії ще працює."""
    assert cart.total_with_promo("WELCOME50", date(2026, 11, 30)) == Decimal("329.00")


def test_min_order_not_reached():
    """Критерій 3: сума менша за мінімальну."""
    c = Cart()
    c.add("s1", "Борщ", 95)
    with pytest.raises(PromoError, match="від 200"):
        c.total_with_promo("SMAKOTA10", TODAY)


def test_total_never_negative(monkeypatch):
    """Критерій 4: знижка більша за суму не робить її від’ємною."""
    import cart as cart_module
    monkeypatch.setitem(cart_module.PROMO_CODES, "BIG", ("fixed", Decimal("1000"), date(2027, 1, 1), Decimal("0")))
    c = Cart()
    c.add("d1", "Компот", 40)
    assert c.total_with_promo("BIG", TODAY) == Decimal("0.00")


@pytest.mark.parametrize("qty", [0, -1, 1.5])
def test_invalid_quantity(qty):
    with pytest.raises(CartError):
        Cart().add("s1", "Борщ", 95, qty=qty)


def test_empty_code(cart):
    with pytest.raises(PromoError):
        cart.total_with_promo("", TODAY)
