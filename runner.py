#from coinspot import CoinSpot

from coinspot import CoinSpot

cs = CoinSpot("59c5c58c9cf4916fe50fbd58e5c931e3",
              "FL9BD12TYHFU1ADUVDXZB7P4C9964YEY9XG3JWUVDV0E48JHNYQGL76KK1FREL7ZDY3LPAKKL1QWVK8K")

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
