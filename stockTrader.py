from tradingFuncs import *

def wakeUpFreckle():
    #ABvalue = 'B' #for day trades, creating two list loop
    while True:
        #FOR DEBUGGING ONLY
        #x = 1
        #if x == 1:
        if marketOpenCheck(3, 10):
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
                ownedStocks = rStocks.build_holdings()

                for stockSymbols in stockMarketOpenPrice:
                    getMarketUpdatedPrice(stockSymbols)
                    considerSelling(stockSymbols,ownedStocks)

        else:
            stockMarketOpenPrice.clear()
            #getAllStockSymbols()

if __name__ == '__main__':
    wakeUpFreckle()