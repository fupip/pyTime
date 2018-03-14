# encoding:UTF-8
import regex as re
# import re
import gzip
import binascii
from cStringIO import StringIO
import stringPreHandling
from datetime import datetime
import TimeUnit


class TimeNormalizer(object):

    #  ------------------------------------------------------------------------
    def __init__(self, preferFuture=True):
        self.timeBase = ""
        self.oldTimeBase = ""
        self.patterns = None
        self.target = ""
        self.timeToken = []
        self.isPreferFuture = True
        self.cleanText = ""
        self.isPreferFuture = preferFuture
        self.readModel()

    #  ------------------------------------------------------------------------
    def parse(self, target, timebase=None):
        self.target = target
        if timebase:
            self.timeBase = timebase
            self.oldTimeBase = timebase
        else:
            datetime.now().strftime("%Y-%m-%d")
            self.timeBase = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.oldTimeBase = self.timeBase

        self.preHandling()

        timeToken = self.TimeEx(self.target, timebase)

        return timeToken

    #  ------------------------------------------------------------------------
    #  待匹配字符串的清理空白符和语气助词以及大写数字转化的预处理
    def preHandling(self):
        self.target = stringPreHandling.delKeyword(self.target, u"\s+")
        self.target = stringPreHandling.delKeyword(self.target, u"[的]+")
        self.target = stringPreHandling.numberTranslator(self.target)

    #  ------------------------------------------------------------------------

    def TimeEx(self, text, timebase):

        startline = -1
        endline = -1
        temp = [""] * 100
        rpointer = 0
        Time_Result = None
        match = self.patterns.search(text)
        i = 0
        offset = 0
        try:
            while match:
                i = i + 1
                startline = match.start()
                if endline == startline + offset:
                    rpointer = rpointer - 1
                    temp[rpointer] = temp[rpointer] + match.group()
                else:
                    temp[rpointer] = match.group()
                endline = match.end()
                offset = endline
                rpointer += 1

                text = text[endline:]
                match = self.patterns.search(text)
        except Exception, ex:
            print ex
            print rpointer
        if rpointer > 0:
            rpointer -= 1
            rpointer += 1
        Time_Result = [None] * rpointer

        contextTp = [-1, -1, -1, -1, -1, -1]
        for j in range(rpointer):
            Time_Result[j] = TimeUnit.TimeUnit(temp[j], self, contextTp)
            contextTp = Time_Result[j].timepoint

        Time_Result = TimeNormalizer.filterTimeUnit(Time_Result)

        self.cleanText = self.target
        for tr in Time_Result:
            self.cleanText = self.cleanText.replace(tr.Time_Expression, "")

        return Time_Result

    @staticmethod
    def filterTimeUnit(timeUnits):
        if timeUnits == None or len(timeUnits) < 1:
            return timeUnits
        tlist = []
        # TODO
        for t in timeUnits:
            if t.getTime().strftime("%Y-%m-%d-%H-%M-%S") != "1970-01-01-00-00-00":
                tlist.append(t)

        return tlist

    #  ------------------------------------------------------------------------

    def getTimeBase(self):
        return self.timeBase

    def getOldTimeBase(self):
        return self.oldTimeBase

    def setTimeBase(self, t):
        self.timeBase = t

    def resetTimeBase(self):
        self.timeBase = self.oldTimeBase

    def setisPreferFuture(self, future):
        self.isPreferFuture = future

    def getTimeUnit(self):
        return self.timeToken

    def readModel(self):
        rfile = "rule.txt"
        line = ""
        try:
            with open(rfile, "r+") as f:
                line = f.readline().decode("utf8")
                self.patterns = re.compile(line)
        except Exception, ex:
            print ex


if __name__ == "__main__":
    # g = gzip.open("TimeExp.m", 'rb')
    # f = open("TimeExp.txt", 'wb')
    # content = g.read()

    # print type(content)
    # f.write(content)
    # g.close()
    # f.close()

    text = u"下午1点到场"
    # text =u"我在  13:30到场"
    # text = u"我在2015年6月8日下午5点23分开始吃饭"
    # text = u"我在明天下午五点23分"

    # text = u"我没什么事"
    # text = u"我在上周3吃饭"

    text = u"提醒我周日参加蜀山杯与庐阳青年队的比赛，13:30到场。"
    # text = u"2015年6月8日下午3点提醒我开经理级会议"
    # text = u"晚上继续给老大吃药，双金10ml，日3次，头孢克肟半片，日2次。"
    # text = u"提醒我明天不用早上起了"
    # text = u"早上5点半：懒猪，该跑步了"
    text = u"每月周三下午5点提醒我开会"
    text = u"12月第二个周五"
    normalizer = TimeNormalizer()
    tunits = normalizer.parse(text)
    print normalizer.target
    print normalizer.cleanText
    print "----------------------------------------"
    for tunit in tunits:
        print tunit.Time_Expression
        print tunit.getTime()
        print tunit.getTimeSpan()
