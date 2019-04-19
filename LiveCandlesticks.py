import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.animation as animation
from matplotlib.finance import _candlestick
import matplotlib
import pylab
import urllib2
import Polo27
import json

matplotlib.rcParams.update({'font.size': 9})


def rviFunc(closes, opens, highs, lows, volumes, n=10):

    num = movingaverage(closes,n)-movingaverage(opens,n)
    den = movingaverage(highs,n)-movingaverage(lows,n)
    try:
      rvi = num/den
    except Exception, e:
        print str('Probably a zero in the denominator. Fix this you dipshit')

    rviSig = movingaverage(rvi,4)
    
    return rvi, rviSig

def rsiFunc(prices, n=14):
    deltas=np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n  
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n-1)+upval)/n
        down = (down*(n-1)+downval)/n
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)     
    return rsi
    

def movingaverage(values,window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values, weights, 'valid')
    return smas

def ExpMovingAverage(values,window):
    weights = np.exp(np.linspace(-1.,0.,window))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

def computeMACD(x, slow=26, fast=12):
    '''
    macd line = 12ema - 26ema
    signal line = 9ema of the macd line
    histogram = macd line - signal line
    '''
    emaslow = ExpMovingAverage(x, slow)
    emafast = ExpMovingAverage(x, fast)
    return emaslow, emafast, emafast - emaslow


def graphData(stock,MA1,MA2,period,numdays):
    fig.clf()
    candleWidth = .05
    try:
        try:
            print 'pulling data on',stock

            now = time.time()
            then = time.time() - (numdays*86400)
            
            elPeriod = 0
            if period == 5:
                elPeriod = 300
                candleWidth = .001
            elif period == 15:
                elPeriod = 900
                candleWidth = .005
            elif period == 30:
                elPeriod = 1800
                candleWidth = .01
            elif period == 2:
                elPeriod = 7200
                candleWidth = .03
            elif period == 4:
                elPeriod = 14400
                candleWidth = .07
            elif period == 24:
                elPeriod = 86400
                candleWidth = .5
            else:
                elPeriod = 86400
                candleWidth = .5
                
            urlToVisit='https://poloniex.com/public?command=returnChartData&currencyPair=BTC_'+stock+'&start='+str(int(then))+'&end=9999999999&period='+str(elPeriod)

            stockFile = []
            try:
                sourceCode = urllib2.urlopen(urlToVisit)
                json_object = json.loads(sourceCode.read())
                for d in json_object:

                    fixedDate = str(datetime.datetime.fromtimestamp(int(d['date'])).strftime('%Y-%m-%d %H:%M:%S'))
                    tclose = d['close']
                    thigh = d['high']
                    tlow = d['low']
                    topen = d['open']
                    tvolume = d['volume']
                    try:
                        theAppendLine = '{0},{1},{2},{3},{4},{5},'.format(fixedDate,tclose,thigh,tlow,topen,tvolume)

                        stockFile.append(theAppendLine)
                    except Exception, e:
                        print str(e)

            except Exception, e:
                print str(e,'failed to organize data')

        except Exception, e:
            print str(e,'failed to pull price data')

        date, closep, highp, lowp, openp, volume = np.loadtxt(stockFile,delimiter=',',unpack=True,usecols=range(6),
                                                              converters={0:mdates.strpdate2num('%Y-%m-%d %H:%M:%S')})

        x = 0
        y = len(date)
        candleAr = []

        while x < y:
            appendLine = date[x],openp[x],closep[x],highp[x],lowp[x],volume[x]
            candleAr.append(appendLine)
            x +=1
        
        Av1 = movingaverage(closep,MA1)
        Av2 = movingaverage(closep,MA2)

        SP = len(date[MA2-1:])

        label1=str(MA1)+' SMA'
        label2=str(MA2)+' SMA'


        
        ax1 = plt.subplot2grid((7,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
        _candlestick(ax1, candleAr[-SP:], width=candleWidth, colorup='#53c156', colordown='#ff1717')

        ax1.plot(date[-SP:],Av1[-SP:],'#e1edf9',label=label1,linewidth=1.5)
        ax1.plot(date[-SP:],Av2[-SP:],'#4ee6fd',label=label2,linewidth=1.5)
        
        ax1.grid(True, color='w')
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax1.yaxis.label.set_color('w')
        ax1.spines['bottom'].set_color('#5998ff')
        ax1.spines['top'].set_color('#5998ff')
        ax1.spines['left'].set_color('#5998ff')
        ax1.spines['right'].set_color('#5998ff')
        ax1.tick_params(axis='y', colors='w')
        ax1.tick_params(axis='x', colors='w')
        plt.ylabel('Stock Price and Volume')
        
        
        
        maLeg = plt.legend(loc=9,ncol=2, prop={'size':7}, fancybox=True, borderaxespad=0.)
        maLeg.get_frame().set_alpha(0.4)
        textEd = pylab.gca().get_legend().get_texts()
        pylab.setp(textEd[0:5],color='w')

        ax0 = plt.subplot2grid((7,4), (0,0),sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')

        rsi = rsiFunc(closep)
        rsiCol = '#c1f9f7'
        posCol = '#386d13' 
        negCol = '#8f2020'
        ax0.plot(date[-SP:],rsi[-SP:],rsiCol,linewidth=1.5)
        ax0.axhline(70,color=negCol)
        ax0.axhline(30,color=posCol)
        ax0.fill_between(date[-SP:],rsi[-SP:],70, where=(rsi[-SP:]>=70),facecolor=negCol, edgecolor=negCol)
        ax0.fill_between(date[-SP:],rsi[-SP:],30, where=(rsi[-SP:]<=30),facecolor=posCol, edgecolor=posCol)
        ax0.set_ylim(0,100)

        ax0.spines['bottom'].set_color('#5998ff')
        ax0.spines['top'].set_color('#5998ff')
        ax0.spines['left'].set_color('#5998ff')
        ax0.spines['right'].set_color('#5998ff')
        ax0.text(0.015,0.95, 'RSI (14)', va='top', color='w', transform=ax0.transAxes)
        ax0.tick_params(axis='y', colors='w')
        ax0.tick_params(axis='x', colors='w')
        ax0.set_yticks([30,70])

        volumeMin = 0

        ax1v = ax1.twinx()
        ax1v.fill_between(date[-SP:],volumeMin,volume[-SP:],facecolor='#00ffe8',alpha=.5)
        ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ax1v.spines['bottom'].set_color('#5998ff')
        ax1v.spines['top'].set_color('#5998ff')
        ax1v.spines['left'].set_color('#5998ff')
        ax1v.spines['right'].set_color('#5998ff')
        ax1v.set_ylim(0,2*volume.max())

        ax2 = plt.subplot2grid((7,4),(5,0),sharex=ax1, rowspan=1, colspan = 4, axisbg = '#07000d')
        fillcolor = '#00ffe8'
        nslow = 26
        nfast = 12
        nema = 9

        emaslow, emafast, macd = computeMACD(closep)
        ema9 = ExpMovingAverage(macd, nema)

        ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
        ax2.plot(date[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
        ax2.fill_between(date[-SP:],macd[-SP:]-ema9[-SP:],0,alpha=0.5,facecolor=fillcolor,edgecolor=fillcolor)
        ax2.text(0.015,0.95, 'MACD 12,26,9', va='top', color='w', transform=ax2.transAxes)

        ax2.spines['bottom'].set_color('#5998ff')
        ax2.spines['top'].set_color('#5998ff')
        ax2.spines['left'].set_color('#5998ff')
        ax2.spines['right'].set_color('#5998ff')
        ax2.tick_params(axis='y', colors='w')
        ax2.tick_params(axis='x', colors='w')
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5,prune='upper'))
        plt.ylabel('MACD',color='w')

        ax3 = plt.subplot2grid((7,4), (6,0),sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        rvi, rviSig = rviFunc(closep,openp,highp,lowp,volume)
        rviCol = '#c1f9f7'
        ax3.plot(date[-SP:],rvi[-SP:],rviCol,linewidth=1.5)
        ax3.plot(date[-SP:],rviSig[-SP:],'#5998ff',linewidth=1.5)

        ax3.spines['bottom'].set_color('#5998ff')
        ax3.spines['top'].set_color('#5998ff')
        ax3.spines['left'].set_color('#5998ff')
        ax3.spines['right'].set_color('#5998ff')
        ax3.text(0.015,0.95, 'RVI (10)', va='top', color='w', transform=ax3.transAxes)
        ax3.tick_params(axis='y', colors='w')
        ax3.tick_params(axis='x', colors='w')

        for label in ax3.xaxis.get_ticklabels():
            label.set_rotation(45)
 

        plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)

        plt.suptitle(stock,color='w')

        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)

    except Exception, e:
        print 'failed main loop',str(e)

fig = plt.figure(facecolor='#07000d')

def animate(i):
    graphData(stockToUse,5,50,tperiod,tdays)
    
while True:
    stockToUse = raw_input('Coin to chart: ')
    tperiod = int(raw_input('Period (5 min, 15 min, 30 min, 2hr, 4hr, 24hr): '))
    tdays = int(raw_input('Days of data: '))
    ani = animation.FuncAnimation(fig, animate, interval=3000)
    plt.show()