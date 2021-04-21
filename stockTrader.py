from tradingFuncs import *

r = rStocks.robinhood

def wakeUpFreckle():
    while True:
        #FOR DEBUGGING ONLY
        #x = True
        #if x:
        #if marketOpenCheck(3, 10):
        if r.get_market_today_hours(get_markets())['is_open']:
            print('Market Open!')
            login(auth1,auth2)
            if len(stockMarketOpenPrice) == 0:
                for symbols in tempStockList:
                    try:
                        getMarketOpenPrices(symbols)
                    except:
                        pass
            else:
                stockMarketUpdatedPrice.clear()
                ownedStocks = r.build_holdings()

                for stockSymbols in stockMarketOpenPrice:
                    if stockMarketUpdatedPrice not in dontSellList:
                        getMarketUpdatedPrice(stockSymbols)
                        considerSelling(stockSymbols,ownedStocks)

        else:
            if len(stockMarketOpenPrice) > 0:
                stockMarketOpenPrice.clear()
            print('Market Closed')

def test():
    login(auth1,auth2)
    getMarket()

if __name__ == '__main__':
    #wakeUpFreckle()
    test()