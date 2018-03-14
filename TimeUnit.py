# encoding: UTF-8
import re
import calendar
from datetime import datetime, timedelta
import TimeNormalizer
import sys
import dateutil.relativedelta
reload(sys)
sys.setdefaultencoding("utf-8")


def Enum(**enums):
    return type('Enum', (), enums)
RangeTime = Enum(day_break=3, early_moring=8, morning=10,
                 noon=12, afternoon=15, night=18, latenight=20, midnight=23)


class TimeUnit(object):



    def __init__(self, exp_time, tn,contextTp=None):

        self.Time_Norm = ''
        self.time_full = []
        self.time_origin = []
        self.timevalue = datetime(1970,1,1,0,0,0)
        self.isAllDayTime = True
        self.isFirstTimeSolveContext = True
        self.timepoint = [-1, -1, -1, -1, -1, -1]
        self.timeorigin = [-1, -1, -1, -1, -1, -1]
        self.weekdone=False

        self.Time_Expression = exp_time
        self.normalizer = tn
        if contextTp:
            self.timeorigin=contextTp
        self.Time_Normalization()

    def getTime(self):
        return self.timevalue

    #  年-规范化方法
    #  该方法识别时间表达式单元的年字段
    def norm_setyear(self):
        rule = ur"[0-9]{2}(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            
            self.timepoint[0] = int(match.group())
            if self.timepoint[0] >= 0 and self.timepoint[0] < 100:
                if self.timepoint[0] < 30:
                    self.timepoint[0] = self.timepoint[0] + 2000
                else:
                    self.timepoint[0] = self.timepoint[0] + 1900
        rule = ur"[0-9]?[0-9]{3}(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            self.timepoint[0] = int(match.group())

    #  ------------------------------------------------------------------------
    #  月-规范化方法
    #  该方法识别时间表达式单元的月字段
    
    def norm_setmonth(self):
        rule = ur"((10)|(11)|(12)|([1-9]))(?=月)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)

        if match:
            self.timepoint[1] = int(match.group())
            self.preferFuture(1)


    #  ------------------------------------------------------------------------
    # 月-日 兼容模糊写法
    # 该方法识别时间表达式单元的月、日字段
    def norm_setmonth_fuzzyday(self):
        rule = ur"((10)|(11)|(12)|([1-9]))(月|\.|\-)([0-3][0-9]|[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            matchStr = match.group()
            rule=ur"(月|\.|\-)"
            p = re.compile(rule)
            m = p.search(matchStr)
            if m:
                splitIndex = m.start()

                month = matchStr[0:splitIndex]
                day = matchStr[splitIndex + 1:]

                self.timepoint[1] = int(month)
                self.timepoint[2] = int(day)
                self.preferFuture(1)
     
    #  ------------------------------------------------------------------------
    #  某月第几个星期几方法
    def norm_setweek(self):
        
        y=self.timepoint[0]
        m=self.timepoint[1]

        if y==-1:
            y=datetime.now().year
        
        if m==-1:
            m=datetime.now().month
     

        rule = ur"第(\d)个(星期|周)(\d)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            n=int(match.group(1))
            wd=int(match.group(3))
            self.setweek(y,m,n,wd)
        
        rule = ur"第(\d)个(星期|周)末"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            n=int(match.group(1))
            self.setweek(y,m,n,5)
        
        rule = ur"倒数第(\d)个(星期|周)(\d)"
        pattern = re.compile(rule)

        match = pattern.search(self.Time_Expression)
        if match:
            n=int(match.group(1))
            wd=int(match.group(3))
            self.setweek(y,m,n,wd,True)

        rule = ur"倒数第(\d)个(星期|周)(\d)"
        pattern = re.compile(rule)

        match = pattern.search(self.Time_Expression)
        if match:
            n=int(match.group(1))
            wd=int(match.group(3))
            self.setweek(y,m,n,wd,True)

        rule = ur"最后1个(星期|周)(\d)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            n=1
            wd=int(match.group(2))
            self.setweek(y,m,n,wd,True)
        
        rule = ur"最后1个周末"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            n=1
            self.setweek(y,m,n,5,True)

    
    def setweek(self,y,m,n,wd,reverse=False):
        dt=datetime(year=y,month=m,day=1)
        x =0
        dlist=[]

        for i in range(31):
            if dt.month!=m:
                break

            if dt.weekday()==wd-1:
                dlist.append(dt.day)
            dt=dt+timedelta(days=1)
        if len(dlist)<n:
            return
            
        if not reverse :
            d=dlist[n-1]
        else:
            d=dlist[n*(-1)]
        self.timepoint[2]=d
        self.weekdone=True

    #  ------------------------------------------------------------------------
    # 日-规范化方法

    def norm_setday(self):
        rule = ur"((?<!\d))([0-3][0-9]|[1-9])(?=(日|号))"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)

        if match:
            
            self.timepoint[2] = int(match.group())
            self.preferFuture(2)
    #  ------------------------------------------------------------------------
    #  时-规范化方法

    def norm_sethour(self):
        
        rule = ur"(?<!(周|期))([0-2]?[0-9])(?=(点|时))"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            self.timepoint[3] = int(match.group())
            self.preferFuture(3)

        rule = ur"凌晨"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.day_break
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"早上|早晨|早间|晨间|今早|明早"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.early_morning
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"上午"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.morning
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"(中午)|(午间)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] >= 0 and self.timepoint[3] <= 10:
                self.timepoint[3] += 12
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.noon
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"(下午)|(午后)|(pm)|(PM)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:

            if self.timepoint[3] >= 0 and self.timepoint[3] <= 11:
                self.timepoint[3] += 12
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.afternoon
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"晚上|夜间|夜里|今晚|明晚"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] >= 1 and self.timepoint[3] <= 11:
                self.timepoint[3] += 12
            elif self.timepoint[3] == 12:
                self.timepoint[3] = 0
            elif self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.night
            self.preferFuture(3)
            self.isAllDayTime = False
    #  ------------------------------------------------------------------------
    #  分-规范化方法
    def norm_setminute(self):
        rule = ur"([0-5]?[0-9](?=分(?!钟)))|((?<=((?<!小)[点时]))[0-5]?[0-9](?!刻))"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        
        if match:
            if match.group() != "":
                self.timepoint[4] = int(match.group())
                self.preferFuture(4)
                self.isAllDayTime = False
        

        rule = ur"(?<=[点时])[1一]刻(?!钟)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            self.timepoint[4] = 15
            self.preferFuture(4)
            self.isAllDayTime = False

        rule = ur"(?<=[点时])半"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            self.timepoint[4] = 30
            self.preferFuture(4)
            self.isAllDayTime = False

        rule = ur"(?<=[点时])[3三]刻(?!钟)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            self.timepoint[4] = 45
            self.preferFuture(4)
            self.isAllDayTime = False

    #  ------------------------------------------------------------------------
    #  秒-规范化方法
    def norm_setsecond(self):
        rule = ur"([0-5]?[0-9](?=秒))|((?<=分)[0-5]?[0-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            self.timepoint[5] = int(match.group())
            isAllDayTime = False

    #  ------------------------------------------------------------------------
    #  特殊形式的规范化方法
    def norm_setTotal(self):
        rule = ur"(?<!(周|期))([0-2]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)

        if match:
            tmptarget = match.group()
            tmpparser = tmptarget.split(":")
            self.timepoint[3] = int(tmpparser[0])
            self.timepoint[4] = int(tmpparser[1])
            self.timepoint[5] = int(tmpparser[2])
            self.preferFuture(3)
            self.isAllDayTime = False
        else:
            rule = ur"(?<!(周|期))([0-2]?[0-9]):[0-5]?[0-9]"
            pattern = re.compile(rule)
            match = pattern.search(self.Time_Expression)
            if match:
                tmpparser = match.group().split(":")
                self.timepoint[3] = int(tmpparser[0])
                self.timepoint[4] = int(tmpparser[1])
                self.preferFuture(3)
                self.isAllDayTime = False

        rule = ur"(中午)|(午间)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] >= 0 and self.timepoint[3] <= 10:
                self.timepoint[3] += 12
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.noon
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"(下午)|(午后)|(pm)|(PM)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] >= 0 and self.timepoint[3] <= 11:
                self.timepoint[3] += 12
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.afternoon
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"晚"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            if self.timepoint[3] >= 1 and self.timepoint[3] <= 11:
                self.timepoint[3] += 12
            elif self.timepoint[3] == 12:
                self.timepoint[3] = 0
            if self.timepoint[3] == -1:
                self.timepoint[3] = RangeTime.night
            self.preferFuture(3)
            self.isAllDayTime = False

        rule = ur"[0-9]?[0-9]?[0-9]{2}-((10)|(11)|(12)|([1-9]))-((?<!\d))([0-3][0-9]|[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            tmpparser = match.group().split("-")
            self.timepoint[0] = int(tmpparser[0])
            self.timepoint[1] = int(tmpparser[1])
            self.timepoint[2] = int(tmpparser[2])

        rule = ur"((10)|(11)|(12)|([1-9]))/((?<!\d))([0-3][0-9]|[1-9])/[0-9]?[0-9]?[0-9]{2}"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            tmpparser = match.group().split("/")
            self.timepoint[0] = int(tmpparser[0])
            self.timepoint[1] = int(tmpparser[1])
            self.timepoint[2] = int(tmpparser[2])

        rule = ur"[0-9]?[0-9]?[0-9]{2}\.((10)|(11)|(12)|([1-9]))\.((?<!\d))([0-3][0-9]|[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            tmpparser = match.group().split("\.")
            self.timepoint[0] = int(tmpparser[0])
            self.timepoint[1] = int(tmpparser[1])
            self.timepoint[2] = int(tmpparser[2])

    #  ------------------------------------------------------------------------
    #  设置以上文时间为基准的时间偏移计算
    def norm_setBaseRelated(self):

        time_grid = self.normalizer.getTimeBase().split("-")
        
        ini = []
        for t in time_grid:
            n=0
            ini.append(int(t))

        dt = datetime(ini[0], ini[1], ini[2], ini[3], ini[4], ini[5])

        flag = [False, False, False]

        rule = ur"\d+(?=天[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            day = int(match.group())
            dt = dt + timedelta(days=day * -1)

        rule = ur"\d+(?=天[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            day = int(match.group())
            dt = dt + timedelta(days=day)

        rule = ur"\d+(?=(个)?月[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[1] = True
            month = int(match.group())
            dt=dt+dateutil.relativedelta.relativedelta(months=month)

        rule = ur"\d+(?=(个)?月[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[1] = True
            month = int(match.group())
            dt=dt+dateutil.relativedelta.relativedelta(months=month)

        rule = ur"\d+(?=年[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            year = int(match.group())
            dt = datetime(dt.year-year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

        rule = ur"\d+(?=年[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            year = int(self.Time_Expression)
            dt = datetime(dt.year+year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

        dtstr = dt.strftime("%Y-%m-%d-%H-%M-%S")
        time_fin = dtstr.split("-")

        if flag[0] or flag[1] or flag[2]:
            self.timepoint[0] = int(time_fin[0])

        if flag[1] or flag[2]:
            self.timepoint[1] = int(time_fin[1])

        if flag[2]:
            self.timepoint[2] = int(time_fin[2])


    #  ------------------------------------------------------------------------
    #  设置当前时间相关的时间表达式
    def norm_setCurRelated(self):
        time_grid = self.normalizer.getOldTimeBase().split("-")
        ini = []
        for t in time_grid:
            ini.append(int(t))

        dt = datetime(ini[0], ini[1], ini[2], ini[3], ini[4], ini[5])
        flag = [False, False, False]

        rule = ur"前年"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            dt = dt + dateutil.relativedelta.relativedelta(years=-2)

        rule = ur"去年"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            dt=dt+dateutil.relativedelta.relativedelta(years=-1)

        rule = ur"今年"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            dt=dt+dateutil.relativedelta.relativedelta(years=0)

        rule = ur"明年"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            dt=dt+dateutil.relativedelta.relativedelta(years=1)

        rule = ur"后年"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[0] = True
            dt=dt+dateutil.relativedelta.relativedelta(years=2)

        rule = ur"上(个)?月"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[1] = True
            dt=dt+dateutil.relativedelta.relativedelta(months=-1)

        rule = ur"(本|这个)月"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[1] = True
            dt=dt+dateutil.relativedelta.relativedelta(months=0)

        rule = ur"下(个)?月"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[1] = True
            dt=dt+dateutil.relativedelta.relativedelta(months=1)

        rule = ur"大前天"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=-3)

        rule = ur"(?<!大)前天"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=-2)

        rule = ur"昨"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=-1)

        rule = ur"今(?!年)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=0)

        rule = ur"明(?!年)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=1)

        rule = ur"(?<!大)后天"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=2)

        rule = ur"大后天"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            dt = dt + timedelta(days=3)

        rule = ur"((?<=(上上周))|(?<=(上上星期)))[1-7]?"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            weekday = 1
            try:
                weekday = int(match.group())
            except:
                weekday = 1
            pweekday = weekday-1
            dtweekday=dt.weekday()
            dt=dt+timedelta(days=(pweekday-dtweekday)-14)

        rule = ur"(?<!上上周)(?<!上上星期)((?<=上周)|(?<=上星期))[1-7]?"
        pattern=re.compile(rule)
        match=pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            weekday = 1
            try:
                weekday = int(match.group())
            except:
                weekday = 1
            pweekday = weekday-1
            dtweekday=dt.weekday()
            dt=dt+timedelta(days=(pweekday-dtweekday)-7)

        rule = ur"(?<!下下周)(?<!下下星期)((?<=下周)|(?<=下星期))[1-7]?"
        pattern=re.compile(rule)
        match=pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            weekday = 1
            try:
                weekday = int(match.group())
            except:
                weekday = 1
            pweekday = weekday-1
            dtweekday=dt.weekday()
            dt=dt+timedelta(days=(pweekday-dtweekday)+7)

        rule = ur"((?<=(下下周))|(?<=(下下星期)))[1-7]?"
        pattern=re.compile(rule)
        match=pattern.search(self.Time_Expression)
        if match:
            flag[2] = True
            weekday = 1
            try:
                weekday = int(match.group())
            except:
                weekday = 1
            pweekday = weekday-1
            dtweekday=dt.weekday()
            dt=dt+timedelta(days=(pweekday-dtweekday)+14)    

        if not self.weekdone:
            rule = ur"(?<!上周)(?<!上星期)(?<!个周)(?<!个星期)((?<=周)|(?<=星期))[1-7]?"
            pattern=re.compile(rule)
            match=pattern.search(self.Time_Expression)
            if match:

                flag[2] = True
                print flag[2]
                weekday = 1
                try:
                    weekday = int(match.group())
                except:
                    weekday = 1
                pweekday = weekday-1
                dtweekday=dt.weekday()
                dt=dt+timedelta(days=(pweekday-dtweekday))
                self.preferFutureWeek(pweekday,dt) 
          
        dtstr = dt.strftime("%Y-%m-%d-%H-%M-%S")
        time_fin = dtstr.split("-")


        if flag[0] or flag[1] or flag[2]:
            self.timepoint[0] = int(time_fin[0])

        if flag[1] or flag[2]:
            self.timepoint[1] = int(time_fin[1])

        if flag[2]:
            self.timepoint[2] = int(time_fin[2])

    #  ------------------------------------------------------------------------
    def modifyTimeBase(self):
    	time_grid=self.normalizer.getTimeBase().split("-")
    	s=""
    	if self.timepoint[0]!=-1:
    		s=s+str(self.timepoint[0])
    	else:
    		s=s+time_grid[0]
    	for i in range(6)[1:]:
    		s+="-"
    		if self.timepoint[i]!=-1:
    			s=s+str(self.timepoint[i])
    		else:
    			s=s+time_grid[i]
        self.normalizer.setTimeBase(s)
    			
    #  ------------------------------------------------------------------------
    def getTimeSpan(self):
        timespan=0
        spantype=0 # 0 无 1 小时 2 天  3 周 4 月 5年

        rule = ur"(每|隔)年"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=1
            spantype=5

        rule = ur"(?<=(每|隔))\d+(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=int(match.group())
            spantype=5

        rule = ur"(每|隔|每个)月"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=1
            spantype=4

        rule = ur"(?<=(每|隔))\d+(?=(月|个月))"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=int(match.group())
            spantype=4

        rule = ur"(每|隔|每个)周"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=1
            spantype=3

        rule = ur"(?<=(每|隔))\d+(?=(周|个周))"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=int(match.group())
            spantype=3

        rule = ur"(每|隔)天"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=1
            spantype=2

        rule = ur"(?<=(每|隔))\d+(?=天)"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=int(match.group())
            spantype=2

        rule = ur"(每|隔|每个)小时"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=1
            spantype=1

        rule = ur"(?<=(每|隔))\d+(?=(小时|个小时))"
        pattern = re.compile(rule)
        match = pattern.search(self.Time_Expression)
        if match:
            timespan=int(match.group())
            spantype=1
        return spantype,timespan




    #  ------------------------------------------------------------------------
    #  时间表达式规范化的入口

    def Time_Normalization(self):

        self.norm_setyear()

        self.norm_setmonth()

        self.norm_setday()





        self.norm_setmonth_fuzzyday()

        self.norm_setBaseRelated()

        self.norm_setCurRelated()
        self.norm_setweek()
        self.norm_sethour()
        self.norm_setminute()
        self.norm_setsecond()
        self.norm_setTotal()
        self.modifyTimeBase()

        # print "Time Normalization",self.Time_Expression

        self.timeorigin=self.timepoint[:]
        time_grid=self.normalizer.getTimeBase().split("-")
        tunitpointer=5

        while tunitpointer>=0 and self.timepoint[tunitpointer]<0:
            tunitpointer-=1
        
        for i in range(tunitpointer):
            if self.timepoint[i]<0:
                self.timepoint[i]=int(time_grid[i])

        result_tmp=["","","","","",""]
        result_tmp[0]=str(self.timepoint[0])

        if self.timepoint[0]>=10 and self.timepoint[0]<100:
            result_tmp[0]="19"+str(self.timepoint[0])

        if self.timepoint[0]>0 and self.timepoint<10:
            result_tmp[0]="200"+str(self.timepoint[0])

        for i in range(6)[1:]:
            result_tmp[i]=str(self.timepoint[i])

        
        
        self.Time_Norm=""
        year=0
        month=1
        day=1
        hour=0
        minute=0
        second=0
        if int(result_tmp[0])!=-1:
            year=int(result_tmp[0])
            self.Time_Norm+=result_tmp[0]+u"年"
            if int(result_tmp[1])!=-1:

                self.Time_Norm+=result_tmp[1]+u"月"
                month=int(result_tmp[1])
                if int(result_tmp[2])!=-1:
                    self.Time_Norm+=result_tmp[2]+u"日"
                    day=int(result_tmp[2])
                    if int(result_tmp[3])!=-1:
                        self.Time_Norm+=result_tmp[3]+u"时"
                        hour=int(result_tmp[3])
                        if int(result_tmp[4])!=-1:
                            self.Time_Norm+=result_tmp[4]+u"分"
                            minute=int(result_tmp[4])
                            if int(result_tmp[5])!=-1:
                                self.Time_Norm+=result_tmp[5]+u"秒"
                                second=int(result_tmp[5])
        if year>0:
            self.timevalue=datetime(year,month,day,hour,minute,second)
        
        # print "Time Normal:",self.Time_Norm
     
    #  ------------------------------------------------------------------------
    def getIsAllDayTime(self):
        return self.isAllDayTime

    def setIsAllDayTime(self,AllDayTime):
        self.isAllDayTime=AllDayTime

    #  ------------------------------------------------------------------------
    #  checkTimeIndex timepoint 时间数组的下标
    def preferFuture(self, checkTimeIndex):
        # 1.检查被检查的时间级别之前，是否没有更高级的已经确定的时间，如果有，则不进行处理
        for i in range(checkTimeIndex):
            if self.timepoint[i]!=-1:
                return
        # 2.根据上下文补充时间
        self.checkContextTime(checkTimeIndex)

        # 3.根据上下文补充时间后再次检查被检查的时间级别之前，是否没有更高级的已经确定的时间，如果有，则不进行倾向处理.*/
        for i in range(checkTimeIndex):
            if self.timepoint[i]!=-1:
                return
        # 4. 确认用户选项
        if not self.normalizer.isPreferFuture:
            return

        # 5. 获取当前时间，如果识别到的时间小于当前时间，则将其上的所有级别时间设置为当前时间，并且其上一级的时间步长+1*/
        timetemp=None
        
        if self.normalizer.getTimeBase():
            baseTime=self.normalizer.getTimeBase()
            timetemp=datetime.strptime(baseTime,"%Y-%m-%d-%H-%M-%S")
            timeint=[int(x) for x in baseTime.split('-')]
        
        if timetemp:
            curTime=timeint[checkTimeIndex]

            if curTime<=self.timepoint[checkTimeIndex]:
                return
            addTimeUnit=checkTimeIndex-1

            if addTimeUnit==0:
                timetemp=timetemp+dateutil.relativedelta.relativedelta(years=1)

            if addTimeUnit==1:
                timetemp=timetemp+dateutil.relativedelta.relativedelta(months=1)
            
            if addTimeUnit==2:
                timetemp=timetemp+timedelta(days=1)
            
            if addTimeUnit==3:
                timetemp=timetemp+timedelta(hours=1)

            if addTimeUnit==4:
                timetemp=timetemp+timedelta(minutes=1)

            if addTimeUnit==5:
                timetemp=timetemp+timedelta(seconds=1)
            
            timeint=[int(x) for x in timetemp.strftime("%Y-%m-%d-%H-%M-%S").split('-')]
            
            for i in range(checkTimeIndex):
                self.timepoint[i]=timeint[i]


    #  ------------------------------------------------------------------------
    def preferFutureWeek(self,week,dt):
        if not self.normalizer.isPreferFuture:
            return 
        checkTimeIndex=2
        for i in range(checkTimeIndex):
            if self.timepoint[i]!=-1:
                return

        curdate=None
        if self.normalizer.getTimeBase():
            baseTime=self.normalizer.getTimeBase()
            curdate=datetime.strptime(baseTime,"%Y-%m-%d-%H-%M-%S")
        if curdate:
            curweekday=curdate.weekday()
            if curweekday<week:
                return
            dt=dt+timedelta(days=7)




    #  ------------------------------------------------------------------------
    #  根据上下文时间补充时间信息
    def checkContextTime(self,checkTimeIndex):
        for i in range(checkTimeIndex):
            # print type(self.timepoint),type(self.timeorigin)
            if self.timepoint[i]==-1 and self.timeorigin[i]!=-1:
                self.timepoint[i]=self.timeorigin[i]

        if self.isFirstTimeSolveContext and checkTimeIndex==3 and self.timeorigin[checkTimeIndex]>=12 and self.timepoint[checkTimeIndex]<12:
            self.timepoint[checkTimeIndex]+=12
        
        self.isFirstTimeSolveContext=False



    #  ------------------------------------------------------------------------
if __name__ == '__main__':
    test = u"你上上周4去哪"
    # rule = ur"(?<!(周|期))([0-2]?[0-9])(?=(点|时))"
    # rule = ur"(?<=(上上(周|期)))[1-7]?"
    # rule = ur"((?<=(上上周))|(?<=(上上星期)))[1-7]?"
    

    # rule=ur"((?<!上)(上周|上星期))[1-7]?"
    # rule =ur"(?<=((?<!上)上(周|期)))[1-7]?"
    
    rule =ur"((?<!上)((?<=上周)|(?<=上星期)))[1-7]?"
    rule= ur"(?<!上上周)(?<!上上星期)((?<=上周)|(?<=上星期))[1-7]?"

    rule = ur"(?<=((?<!(上|下))(周|星期)))[1-7]?"
    rule = ur"(?<!上周)(?<!上星期)((?<=周)|(?<=星期))[1-7]?"
    pattern = re.compile(rule)
    match=pattern.search(test)
    if match:
        print match.group()
