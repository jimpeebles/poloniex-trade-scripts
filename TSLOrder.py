import Polo27
import json
import time
from datetime import datetime

poloInstance = Polo27.poloniex("API_KEY", "API_SECRET")
originalCurrency = ''


def MarketTrailingStopLimit(pair, trailPercent, limitOffsetPercent):
    lastPrice = 0
    newPrice = 1
    orderID = 0
    originalCurrency = pair
    tradepair = 'BTC_' + str(pair)
    originalStop = 0.0
    stopCounter = 0
    increasedAmt = 0

    # Get market price + Volume
    orderBook = poloInstance.returnOrderBook(tradepair)
    marketPrice = orderBook['asks'][0][0]
    voluAtMarket = orderBook['asks'][0][1]
    print "Market Price: " + str(marketPrice)
    print "Volume at Price: " + str(voluAtMarket)
    time.sleep(.5)

    # get available BTC
    balances = poloInstance.returnBalances()
    btcBalance = balances['BTC']
    print "BTC Balance: " + str(btcBalance)
    time.sleep(.5)

    # Determine max amount that can be purchased
    amount = float(btcBalance) / float(marketPrice)
    print amount

    testAmount = amount / 20

    print voluAtMarket
    print testAmount

    if(testAmount < voluAtMarket):
        currentOrder = poloInstance.buy(tradepair, marketPrice, testAmount)
        time.sleep(1)
        orderID = currentOrder['orderNumber']
        resultingTrades = currentOrder['resultingTrades']
        amountBought = resultingTrades[0]['amount']
        print orderID
        print amountBought

        originalStop = float(marketPrice)*float(trailPercent)
        time.sleep(.5)
    else:
        print 'Not Enough Available For Purchase At This Price!'
        return

    # Loop to check price and adjust orders
    tradeFlag = 0
    newOrders = poloInstance.returnOrderBook(tradepair)
    stopPrice = float(trailPercent)*float(marketPrice)
    floorStopPrice = stopPrice
    time.sleep(.5)
    myPrice = float(marketPrice)

    while(tradeFlag == 0):
        try:
            newOrders = poloInstance.returnOrderBook(tradepair)
            newPrice = float(newOrders['bids'][0][0])
        except:
            print 'Server threw some garbage'
            time.sleep(1)
            pass
        if newPrice <= (myPrice*trailPercent):
            try:
                allbalances = poloInstance.returnBalances()
                currencyBalance = allbalances[originalCurrency]
                print(poloInstance.sell(tradepair, ((myPrice * trailPercent)
                                                    * float(limitOffsetPercent)), float(currencyBalance)))
                tradeFlag = 1
                print 'Sold!'
                raw_input('Press Any Key')
                return
            except:
                print 'Server threw some shit'
                time.sleep(1)
                pass
        else:
            if newPrice > myPrice:

                myPrice = newPrice
                stopCounter += 1

                print 'Original Stop: ' + str(originalStop)
                print 'New Stop: ' + str(myPrice*trailPercent)
                print 'Stop increased', stopCounter, 'times'
                print 'Total increase from original stop: ', (((myPrice*trailPercent)-originalStop)/originalStop)*100, '%'
                time.sleep(1)
            else:
                print 'Stop Not Adjusted -  ' + str(datetime.now())
                time.sleep(1)


# MarketTrailingStopLimit("NXC",.99,.995)
print 'Currency to trade: '
coinToTrade = raw_input()
print 'Stop percent (decimal): '
stopPercent = float(raw_input())
print 'Limit offset percent (decimal) '
limitOff = float(raw_input())
MarketTrailingStopLimit(coinToTrade, stopPercent, limitOff)

# vars - percent of avail btc to use in trade
