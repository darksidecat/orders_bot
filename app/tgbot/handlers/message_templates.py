from aiogram.utils.text_decorations import html_decoration as fmt

from app.domain.order import dto


def format_order_message(order: dto.Order):
    result = fmt.quote(
        f"Id: {str(order.id)}\n"
        f"Created at: {order.created_at}\n"
        f"Creator: {order.creator.name}\n"
        f"Market: {order.recipient_market.name}\n"
        f"Comments: {order.commentary}\n\n"
        f"Status: {order.confirmed.value} {order.confirmed_icon}\n"
        f"Goods:\n"
    )
    for line in order.order_lines:
        result += fmt.quote(
            f"  Name: {line.goods.name} {line.goods.sku}\n"
            f"  Quantity: {line.quantity}\n\n"
        )
    result = result
    return result
