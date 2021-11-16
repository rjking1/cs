#from coinspot import CoinSpot

from coinspot import CoinSpot
from config import KEY, SECRET

cs = CoinSpot(KEY, SECRET)

bal = cs.my_balances()
print("balances")
for b in bal["balance"]:
    print(b, bal["balance"][b])

print("my orders")
orders = cs.my_orders()
print(orders)

print("latest")
latest = cs.latest()
#print(latest)
for p in latest["prices"]:
    if p in bal["balance"]:
        pp = latest["prices"][p]
        print(p, " bid ", pp["bid"], "ask", pp["ask"], "last", pp["last"])
