import robin_stocks as rStocks
from robin_stocks.robinhood import *
import matplotlib.pyplot as plt
from authCreds import auth1, auth2, auth3
import pandas
import pyotp
import sys
import numpy
import openpyxl
import time
import datetime
import gspread
import yfinance
from oauth2client.service_account import ServiceAccountCredentials

tempStockList = ['JT','OBLN','MESO','MRO','PRTS','AR','HMLP','FLL',
                 'QFIN','REDU','RETA','GPRO','F','GNUS','NYMT',
                 'BFRA','NOK','MFA','KODK','CLVS','KOS','ALKS',
                 'SUHJY','BSQR','PSTG','CBAY','IBIO','TEVA','EBON',
                 'TSLA','MCRB','TRXC','CRBP','SRNE','AMC']
dayTradeList = []

stockMarketOpenPrice = {}
stockMarketUpdatedPrice = {}

def marketOpenCheck(marketOpenTime,marketCloseTime):
    #market opens 0330 and closes 1000 HST
    currentTime = datetime.datetime.now()
    dayOfWeek = datetime.datetime.today().weekday()
    if 0 <= dayOfWeek <= 4:
        if marketOpenTime <= currentTime.hour <= marketCloseTime:
            return True
        else:
            return False

    #add holiday exclusion func (black friday and christmas eve)

def login(username,password):
    totp = pyotp.TOTP(auth3).now()
    try:
        rStocks.login(username,password,mfa_code=totp)
        #print(totp) #FOR DEBUGGING ONLY
        #print('Successfully logged in!')
    except Exception as e:
        print('Log in failed...')
        if hasattr(e,'message'):
            print(e.message)
        else:
            print(e)
        sys.exit(0)

def displayStocks():
    myStocks = rStocks.build_holdings()
    myStocksDF = pandas.DataFrame(myStocks)
    print(myStocksDF)
    print(myStocks)
    #print(type(myStocks)) #myStocks is a dict, key = average_buy_price

def stockPriceAcceptable(price=float):
    userProfile = rStocks.build_user_profile()
    userCashVal = userProfile.get('cash')
    userCash = float(userCashVal)
    oneTwentieth = userCash / 20
    if float(price) < float(oneTwentieth):
        return True
    else:
        return False

def determineShareAmount(price=float):
    userProfile = rStocks.build_user_profile()
    userCashVal = userProfile.get('cash')
    userCash = float(userCashVal)
    fiftyPercent = userCash / 2
    shareAmountVal = float(fiftyPercent) / float(price)
    shareAmount = str(int(shareAmountVal))
    return shareAmount

def buyStock(stock,shareAmount):
    try:
        rStocks.order_buy_market(stock,shareAmount)
        print(str(shareAmount)+' shares of '+str(stock).upper()+' purchased!')
    except Exception as e:
        print('Log in failed...')
        if hasattr(e,'message'):
            print(e.message)
        else:
            print(e)
        pass

def sellStock(stock,shareAmount):
    try:
        rStocks.order_sell_market(stock,shareAmount)
        print(str(shareAmount)+' shares of '+str(stock).upper()+' sold!')
    except Exception as e:
        print('Log in failed...')
        if hasattr(e,'message'):
            print(e.message)
        else:
            print(e)
        pass

def getStockHistory(stock,interval,span,bounds):
    data = rStocks.stocks.get_stock_historicals(stock,interval,span,bounds)
    pdData = pandas.DataFrame(data)
    print(pdData)

'''
def getAllStockSymbols():

    allStockSymbols = []

    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('bats symbols (stocks)').sheet1

    listOfHashes = sheet.get_all_records()
    print(listOfHashes)
'''

def getABValue(ABvalue):
    if ABvalue == 'A':
        value = 'B'
        return value
    elif ABvalue == 'B':
        value = 'A'
        return value

    #for day trades, creating a constant loop between two lists

#=====================================================================================================
#if all of a sudden getting inexplicable errors when running wake up freckle check this first
# i added the [0] to end to make key val pairs return string:float instead of string:string
#======================================================================================================

def getMarketOpenPrices(symbol):
    openningPrice = get_latest_price(inputSymbols=symbol, priceType=None, includeExtendedHours=True)[0]
    stockMarketOpenPrice[symbol] = openningPrice

def getMarketUpdatedPrice(symbol):
    updatedPrice = get_latest_price(inputSymbols=symbol, priceType=None, includeExtendedHours=True)[0]
    stockMarketUpdatedPrice[symbol] = updatedPrice

def getPercentageChange(originalValue,updatedValue):
    change = float(updatedValue) - float(originalValue)
    percentChange = round(float(change) / float(originalValue) * 100,2)
    return percentChange

def considerBuying(symbol):
    pass
    #hardest
    #params will be based on trends from the past 1 month? can try around and change if needed

def considerSelling(symbol,ownedStocks):
    if symbol in ownedStocks:
        stock = ownedStocks.get(symbol)
        avgBuyPrice = stock.get('average_buy_price')
        quantity = stock.get('quantity')
        updatedPrice = stockMarketUpdatedPrice.get(symbol)
        percentChange = getPercentageChange(avgBuyPrice, updatedPrice[0])
        if percentChange >= 10:
            #sellStock(symbol,quantity)
            print(symbol+' has seen a '+str(percentChange)+'% increase!')
            print('SELL!')
    else:
        print('not real stock')
        pass
    #meduim hard
    #straight forward, if it reaches 10% gain, sell it (unless daytrade of course)

def considerDayTrade(symbol):
    currentPrice = get_latest_price(inputSymbols=symbol, priceType=None, includeExtendedHours=True)[0]
    #30 minute data... can adjust if needed!
    thirtyMinuteAgoPriceList = rStocks.stocks.get_stock_historicals(symbol, '10minute', 'day')
    thirtyMinuteAgoMark = len(thirtyMinuteAgoPriceList) - 3
    thirtyMinuteAgoPriceItem = thirtyMinuteAgoPriceList[thirtyMinuteAgoMark]
    thirtyMinuteAgoPriceVal = thirtyMinuteAgoPriceItem.get('open_price')
    thirtyMinuteAgoPrice = float(thirtyMinuteAgoPriceVal)
    percentChange = getPercentageChange(thirtyMinuteAgoPrice,currentPrice)
    if percentChange >= 5 and stockPriceAcceptable(currentPrice):
        shareAmount = determineShareAmount(currentPrice)
        #buyStock(symbol,shareAmount) #ADD FOR REAL THING
        print('DAY TRADE ACTIVATED!')
        print('FAKE PURCHASE:',shareAmount,'of',symbol,'at',currentPrice)
        dayTradeList.append(symbol)
    #check to see if 5% increase in short time (30 minutes? maybe 45 minutes?), sell as soon as drops 5% from peak

    #WILL IMPLEMENT DAY TRADES LAST

def considerSellingDayTrade(symbol):
    pass

def dayTradeActiveStatus(dayTradeList):
    if len(dayTradeList) > 0:
        return True
    else:
        return False

    pass
    #considerDayTrade will add that stock to the list (use for loop when running), so this func will check if the list
    #has anything in it, then will give a bool value according.

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

                #DEBUGGING ZONE

                #print(ownedStocks)

                #END DEBUGGING ZONE

                for stockSymbols in stockMarketOpenPrice:
                    getMarketUpdatedPrice(stockSymbols)

                #rearrange this
                for stockSymbols in stockMarketOpenPrice:
                    if not dayTradeActiveStatus(dayTradeList):
                        if stockSymbols in ownedStocks:
                            considerSelling(stockSymbols,ownedStocks)
                        else:
                            considerDayTrade(stockSymbols)
                            if not dayTradeActiveStatus(dayTradeList):
                                pass
                                #considerBuying(stockSymbols)
                    elif dayTradeActiveStatus(dayTradeList):
                        pass
                        #regular trading routine here

                '''
                for stockSymbols in stockMarketOpenPrice:
                    value = stockMarketOpenPrice.get(stockSymbols)
                    value2 = stockMarketUpdatedPrice.get(stockSymbols)
                    percentChange = getPercentageChange(value[0],value2[0])
                    if 10 < percentChange >= 5:
                        print('5 percent increase detected for: ', stockSymbols)
                        #buy
                    elif 10 < percentChange <= -5:
                        print('5 percent decrease detected for: ', stockSymbols)
                        #hold
                    elif percentChange >= 10:
                        print('BIG MOVE for: ', stockSymbols)
                        #sell
                    elif percentChange <= -10:
                        print('BIG DROP for: ', stockSymbols)
                        #hold
                    else:
                        print('No significant changes detected for: ',stockSymbols)
                        #hold
                '''

                    #break #FOR DEBUGGING ONLY

        else:
            stockMarketOpenPrice.clear()
            #getAllStockSymbols()

        if not dayTradeActiveStatus(dayTradeList):
            time.sleep(900) #15 mins
        elif dayTradeActiveStatus(dayTradeList):
            time.sleep(300) #5 mins

        #time.sleep(5) #FOR DEBUGGING ONLY

