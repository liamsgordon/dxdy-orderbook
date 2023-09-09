import websocket
import csv
from functools import partial
import json


def print_stats(prices):
    print("Best bid price:", prices['b_px'])
    print("Best ask price:", prices['a_px'])
    print("Bid size of the best bid price:", prices['b_size'])
    print("Ask size of the best ask price:", prices['a_size'])

    if prices['b_px']is not None and prices['a_px'] is not None:
        spread = prices['a_px'] - prices['b_px']
        print("Spread:", spread)
    print()


def best_prices_order_book(bids, asks, prices):
    for bid in bids:
        bid_price = float(bid['price'])
        bid_size = float(bid['size'])
        if bid_size != float(0):
            if prices['b_px'] is None or bid_price > prices['b_px']:
                    prices['b_px'] = bid_price 
                    prices['b_size'] = bid_size

    for ask in asks:
        ask_price = float(ask['price'])
        ask_size = float(ask['size'])
        if ask_size != float(0):
            if prices['a_px'] is None or ask_price < prices['a_px']: 
                    prices['a_px'] = ask_price 
                    prices['a_size'] = ask_size

    return prices


def update_order_book_rows(new_data, old_data):
    for new_dict in new_data:
        price_check = None
        for i, dictionary in enumerate(old_data):
            if float(dictionary["price"]) == float(new_dict["price"]) and int(dictionary["offset"]) < int(new_dict["offset"]):
                # Remove the old dictionary.
                old_data[i] = new_dict
                price_check = True
                break
        if not price_check:
            old_data.append(new_dict)
    
    return old_data


def update_order_flow(bids, asks, offset):
    offset = int(offset)
    new_asks, new_bids = [], []
    old_bids, old_asks = get_bids(), get_asks()

    for bid in bids:
        new_bids.append({'price': float(bid[0]), 'offset': offset, 'size': float(bid[1])})
    bids = update_order_book_rows(new_bids, old_bids)

    for ask in asks:
        new_asks.append({'price': float(ask[0]), 'offset': offset, 'size': float(ask[1])})
    asks = update_order_book_rows(new_asks, old_asks)

    return bids, asks


def remove_bad_orders(bids, asks, prices):
    new_bids, new_asks = [], []
    for row in bids:
        if prices['a_px'] is not None and float(row['price']) < float(prices['a_px']):
            new_bids.append(row)
    for row in asks:
        if prices['b_px'] is not None and float(row['price']) > float(prices['b_px']):
            new_asks.append(row)
    return new_bids, new_asks


def load_csv(bids, asks):

    field_names = ['price', 'offset', 'size']
    with open('order_book_bids.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names)
        writer.writerows(bids)

    with open('order_book_asks.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names)
        writer.writerows(asks)


def load_best_price(best_prices):
    field_names = ['b_px', 'b_size', 'a_px', 'a_size']
    with open('order_book_best_price.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names)
        writer.writerows([best_prices])


def on_message(ws, message):
    data = json.loads(message)
    contents = data.get('contents')
    best_prices = get_best_prices()

    if contents:
        bids = contents.get('bids')
        asks = contents.get('asks')
        offset = contents.get('offset')

        if not offset:
            best_prices = best_prices_order_book(bids, asks, best_prices)
            load_best_price(best_prices)
            print_stats(best_prices) 
        else:
            new_prices =  {'b_px': None, 'b_size': None, 'a_px': None, 'a_size': None}
            bids, asks = update_order_flow(bids, asks, offset)
            new_prices = best_prices_order_book(bids, asks, new_prices)
            new_prices_floats = [float(i) for j, i in new_prices.items()]
            best_prices_floats = [float(i) for j, i in best_prices.items()]
            if new_prices_floats != best_prices_floats:
                print_stats(new_prices) 
                bids, asks = remove_bad_orders(bids, asks, new_prices)
                load_best_price(new_prices)

        load_csv(bids, asks)


def get_bids():
    reader = csv.reader(open('order_book_bids.csv', newline=''), delimiter=',', quotechar='"')
    bids = [{'price': row[0], 'offset': row[1], 'size': row[2]} for row in reader]
    return bids


def get_asks():
    reader = csv.reader(open('order_book_asks.csv', newline=''), delimiter=',', quotechar='"')
    asks = [{'price': row[0], 'offset': row[1], 'size': row[2]} for row in reader]
    return asks


def get_best_prices():
    reader = csv.reader(open('order_book_best_price.csv', newline=''), delimiter=',', quotechar='"')
    price = [{'b_px': row[0], 'b_size': row[1], 'a_px': row[2], 'a_size': row[3]} for row in reader]
    if price:
        return price[0]
    return {'b_px': None, 'b_size': None, 'a_px': None, 'a_size': None}


def truncate_csv():
    f = open("order_book_bids.csv", "w")
    f.truncate()
    f = open("order_book_asks.csv", "w")
    f.truncate()
    f = open("order_book_best_price.csv", "w")
    f.truncate()
    f.close()


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    truncate_csv()
    print("### closed ###")


if __name__ == "__main__":

    ws = websocket.WebSocketApp(
        "wss://api.dydx.exchange/v3/ws",
        on_message=partial(on_message),
        on_error=on_error,
        on_close=on_close
    )

    # Subscription message
    subscription_message = {
        "type": "subscribe",
        "channel": "v3_orderbook",
        "id": "ETH-USD",
        "includeOffsets": True
    }

    ws.on_open = lambda _: ws.send(json.dumps(subscription_message))

    ws.run_forever()
