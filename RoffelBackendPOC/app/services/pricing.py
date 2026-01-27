from sqlalchemy.orm import Session
from typing import Optional

from app.models.serviceorder_item import ServiceOrderItem
from app.models.customer import Customer
from app.models.customer import CustomerPriceRule


def format_currency(value: Optional[float]) -> str:
    """
    Format float to European currency string.
    """
    if value is None:
        return ""
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_price_for_item(item: ServiceOrderItem, price_type: str) -> Optional[float]:
    """
    Returns the correct price field for a ServiceOrderItem
    based on the given price_type.
    """
    price_map = {
        "LIST": item.list_price,
        "BRUTO": item.price_bruto,
        "WVK": item.price_wvk,
        "EDMAC": item.price_edmac,
        "PURCHASE": item.price_purchase,
    }
    return price_map.get(price_type)


def determine_price_type_for_customer(
    db: Session,
    customer_id: int,
    order_total: float,
    default_price_type: Optional[str],
) -> str:
    """
    Determine the correct price_type based on:
    - customer price rules
    - order total
    - fallback to customer's default price_type
    """

    rules = (
        db.query(CustomerPriceRule)
        .filter(CustomerPriceRule.customer_id == customer_id)
        .order_by(CustomerPriceRule.min_amount.asc())
        .all()
    )

    selected = default_price_type

    for rule in rules:
        if order_total >= rule.min_amount:
            selected = rule.price_type

    return selected or default_price_type or "BRUTO"


def calculate_order_totals(
    db: Session,
    order,
):
    """
    Calculate pricing for a service order.
    Returns:
    - final price_type
    - total amount
    - per-item pricing breakdown
    """

    items = (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )

    customer = (
        db.query(Customer)
        .filter(Customer.name == order.customer.name)
        .first()
    )

    if not customer:
        raise ValueError("Customer not found for serviceorder")

    # Step 1: base total for price-rule selection
    base_total = 0.0
    for item in items:
        price = get_price_for_item(item, customer.price_type or "BRUTO")
        if price:
            base_total += price * (item.qty or 0)

    # Step 2: determine final price type
    final_price_type = determine_price_type_for_customer(
        db=db,
        customer_id=customer.id,
        order_total=base_total,
        default_price_type=customer.price_type,
    )

    # Step 3: calculate final totals
    final_total = 0.0
    priced_items = []

    for item in items:
        qty = item.qty or 0
        price_each = get_price_for_item(item, final_price_type) or 0.0
        line_total = qty * price_each

        final_total += line_total

        priced_items.append({
            "part_no": item.part_no,
            "description": item.description,
            "qty": qty,
            "price_each": price_each,
            "line_total": line_total,
        })

    return {
        "price_type": final_price_type,
        "total": round(final_total, 2),
        "items": priced_items,
    }
