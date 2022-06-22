import csv
import io

from app.domain.order.dto.order import Order


# function that get list of orders and save them to csv file in memory as bytes
def export_orders_to_csv(orders: list[Order]) -> bytes:
    # create csv writer
    output = io.StringIO()
    csv_writer = csv.writer(
        output,
        delimiter="\t",
        quotechar='"',
        quoting=csv.QUOTE_ALL,
        lineterminator="\r\n",
    )
    # write header
    csv_writer.writerow(
        [
            "id",
            "creator_id",
            "creator_name",
            "recipient_market_id",
            "recipient_market_name",
            "goods_name",
            "goods_sku",
            "quantity",
            "commentary",
            "created_at",
            "confirmed",
        ]
    )
    # write orders
    for order in orders:
        for line in order.order_lines:
            csv_writer.writerow(
                [
                    order.id,
                    order.creator.id,
                    order.creator.name,
                    order.recipient_market.id,
                    order.recipient_market.name,
                    line.goods.name,
                    line.goods.sku,
                    line.quantity,
                    order.commentary,
                    order.created_at,
                    order.confirmed,
                ]
            )
    # return bytes
    return output.getvalue().encode("utf-16")
