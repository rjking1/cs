from coinspot import CoinSpot
from config import *
from time import sleep
import random


def buying_coin(coin, buy_orders):
    for buys in buy_orders:
        already_buying_coin = buys["coin"]
        if coin.upper() == already_buying_coin.upper():
            return True
    return False


def cancel_coin(coin, buy_orders):
    for order in buy_orders:
        if order["coin"].upper() == coin.upper():
            cs.my_buy_cancel(order["_id"])


cs = CoinSpot(KEY, SECRET)

print("--- Latest prices ---")
latest_prices = cs.latest()["prices"]
for latest_price in latest_prices:
    if latest_price.upper() in BUY_CODES:
        coin = latest_prices[latest_price]
        print(latest_price, " bid ", coin["bid"],
              "ask", coin["ask"], "last", coin["last"])

balances = cs.my_balances()["balance"]
print("--- Coin balances and approx value using last ---")
tot = 0.0
for coin in balances:
    if coin != 'aud':
        subtot = round(balances[coin] * float(latest_prices[coin]["last"]), 2)
    else:
        subtot = 0
    tot += subtot
    print(coin, balances[coin], subtot if coin != 'aud' else '')
print('Approx Total', tot)

aud_avail = balances["aud"]

if aud_avail < MIN_TRADE_AUD:
    print("*** Insufficient balance to submit any buy orders", aud_avail)
    quit()

print("--- My buy orders price/$total ---")
# should be none
buy_orders = cs.my_orders()["buyorders"]
for order in buy_orders:
    print(order["coin"], order["rate"], order["total"])
    aud_avail -= order["total"]

print("--- My sell orders price/$total ---")
sell_orders = cs.my_orders()["sellorders"]
for order in sell_orders:
    print(order["coin"], order["rate"], order["total"])

print("--------------------------")

# run thru all possible coins and add a buy order if we have funds
buys_added = {}
random.shuffle(BUY_CODES)
for ucoin in BUY_CODES:
    coin = ucoin.lower()

    rate = round(float(latest_prices[coin]["bid"]) * 0.9
                 + float(latest_prices[coin]["ask"]) * 0.1, 6)
    # 0.999 to reduce slightly so as not to exceed avail bal when rounding
    amt = round(min(aud_avail, MAX_TRADE_AUD) / rate * 0.999, 6)

    if PRODUCTION:
        cs.my_buy(ucoin, amt, rate)
    buys_added[ucoin] = {"amt": amt, "rate": rate}
    print("### created buy order for", ucoin, "amount:", amt, "rate", rate)

    aud_avail -= amt * rate
    if aud_avail < MIN_TRADE_AUD:
        break

# print(buys_added)
if PRODUCTION:
    sleep(30)

# check if the buy orders were completed -- if buy order exists then nobody bought it so cancel it
buy_orders = cs.my_orders()["buyorders"]
# print(buy_orders)
for ucoin in buys_added:
    coin = ucoin.lower()
    if buying_coin(coin, buy_orders):
        if PRODUCTION:
            cancel_coin(coin, buy_orders)
        print("*** cancelled buy order for", ucoin, "as not completed")
    else:
        # else completed=bought so create sell order
        # get buy order details for coin
        amt = buys_added[ucoin]["amt"]
        rate = buys_added[ucoin]["rate"]
        # reduce sell amount slightly to allow for fee???
        amt = round(amt * 0.99, 6)
        sell_rate = round(rate * SELL_ABOVE_BUY, 6)
        if PRODUCTION:
            cs.my_sell(ucoin, amt, sell_rate)
        print("### created sell order for", ucoin,
              "amount:", amt, "rate", sell_rate)
