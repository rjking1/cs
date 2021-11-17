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

balances = cs.my_balances()["balance"]
print("balances coins")
for coin in balances:
    print(coin, balances[coin])

print("my buy orders price/$total")
# should be none
buy_orders = cs.my_orders()["buyorders"]
for order in buy_orders:
    print(order["coin"], order["rate"], order["total"])

print("my sell orders price/$total")
sell_orders = cs.my_orders()["sellorders"]
for order in sell_orders:
    print(order["coin"], order["rate"], order["total"])

print("latest")
latest_prices = cs.latest()["prices"]
for latest_price in latest_prices:
    if latest_price in balances or latest_price == "powr":
        coin = latest_prices[latest_price]
        print(latest_price, " bid ", coin["bid"], "ask", coin["ask"], "last", coin["last"])

print("--------------------------")

aud_avail = balances["aud"]
if aud_avail < MIN_TRADE_AUD:
    print("insufficient balance to submit any buy orders", aud_avail)
    quit()

# run thru all possible coins to consider buying
for ucoin in BUY_CODES:
    coin = ucoin.lower()
    if not buying_coin(ucoin, buy_orders):
        rate = round((float(latest_prices[coin]["last"]) * 0.1 + float(latest_prices[coin]["bid"]) * 0.9), 6)
        amt = min(aud_avail, MAX_TRADE_AUD) / rate * 0.999  # 0.999 to reduce slightly so as not to exceed avail bal when rounding
        amt = round(amt, 6)

        #cs.my_buy(ucoin, amt, rate)
        print("created buy order for", ucoin, "amount:", amt, "rate", rate)
        
        # check if the buy was completed -- if it is still in the buy orders then nobody bought it so cancel it
        # else if completed/bought - then create sell order
        sleep(15)
        buy_orders = cs.my_orders()["buyorders"]
        #print(buy_orders)
        if buying_coin(coin, buy_orders):
            #cancel_coin(coin, buy_orders)
            print("cancelled buy order for", ucoin, "as not completed")
        else:
            # need to reduce sell amount as rounding can affect things
            # and increase sell rate to compensate
            amt = round(amt * 0.999, 6)
            sell_rate = rate * SELL_ABOVE_BUY
            sell_rate = round(sell_rate * 1.001001, 6)
            sleep(0.5)
            #cs.my_sell(ucoin, amt, sell_rate)
            sleep(0.5)
            print("created sell order for", ucoin, "amount:", amt, "rate", sell_rate)
        
            aud_avail -= amt * rate
            if aud_avail < MIN_TRADE_AUD:
                print("available balance low -- exiting", aud_avail)
                quit()
