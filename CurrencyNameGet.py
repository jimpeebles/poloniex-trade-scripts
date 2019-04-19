import urllib2
import json


def getCurrList():

    urlToVisit = 'https://poloniex.com/public?command=returnTicker'

    curFile = []
    try:
        sourceCode = urllib2.urlopen(urlToVisit)
        json_object = json.loads(sourceCode.read())
        for d in json_object:
            splitted = d.split("_")
            if splitted[0] == 'BTC':
                curFile.append(str(splitted[1]))
        return curFile

    except Exception, e:
        print str(e, 'failed to organize data')


getCurrList()
