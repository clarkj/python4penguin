#!/usr/bin/python
#
# @brief convert MidNite solar modbus registers for time to ISO860 date format.
#
# produce iso date from register values
# example ISO 8601 date format ISODate("2014-09-17T23:25:56.314Z")
# @see MidNite Solar MODBUS Network Spec. Rev C.4 --- Dec 9, 2013
# http://www.midnitesolar.com/pdfs/classic_register_map_Rev-C5-December-8-2013.pdf
# document later

import datetime

class MidniteTimeConv:

  def __init__(self):
    self.deviceTime = 0
    
  def setRegs(**refDict):
    CTime0r0 = refDict["CTime0r0"]
    CTime0r1 = refDict["CTime0r1"]
    CTime1r0 = refDict["CTime1r0"]
    CTime1r1 = refDict["CTime1r1"]
    CTime2 = refDict["CTime2"]
    #self.getTime()
  
  def getTime():
    #
    # | Register  | R/W Name| Conversion                     |                  Notes 
    # | 4214 4215 | R       | CTIME0 ([4215] << 16) + [4214] | (possibly atomic op) Consolidated Time Registers See Table 4214-1
    # Table 4214-1 Consolidated Time Registers CTime0r0 a/b
    # Name Value Description
    # BITS 5:0 0to59 Seconds Seconds value in the range of 0 to 59
    # BITS 7:6 RESERVED RESERVED
    secMask=0x3f
    # secShift=0
    # sec   = (CTime0r0 >> secShift) & secMask
    sec = CTime0r0 & secMask
    # BITS 13:8 0to59 Minutes value in the range of 0 to 59
    # BITS 15:14 RESERVED RESERVED
    minsMask=0x3f
    minsShift=8
    mins  = (CTime0r0 >> minsShift) & minsMask
    # BITS 20:16 0to23 Hours value in the range of 0 to 23
    # BITS 23:21 RESERVED RESERVED 
    hrsMask=0x0f
    hrsShift=0
    hrs  = CTime0r1 & hrsMask
    # BITS 36:24 0to6 Day Of Week Day of week value in the range of 0 to 6
    # BITS 31:27 RESERVED RESERVED
    dayOfWeekMask = 0x0f
    dayOfWeekShift = 0
    dayOfWeek  = CTime0r1 & dayOfWeekMask
    
    # Table 4216-1 Consolidated Time Registers 1  Ctime1 r0/r1
    #  Name Value Description
    # BITS 4:0 1to28,29,39,31 Day of month value in the range of 1 to 28, 29, 30, or 31(depending on the month and whether it is a leap year)
    # BITS 7:5 RESERVED RESERVED
    dayMask = 0x1f
    dayShift = 0
    day = CTime1r0 & dayMask
    
    # BITS 11:8 1to12 Month value in the range of 1 to 12
    # BITS 15:12 RESERVED RESERVED
    monthMask = 0x0f
    monthShift = 8
    month = (CTime1r0 >> monthShift) & monthMask
    
    # BITS 27:16 0 to 4095 Year value in the range of 0 to 4095
    # BITS 31:28 RESERVED RESERVED
    yearMask = 0x0fff
    yearShift = 0
    year = CTime1r1 & yearMask
    
    # Table 4218-1 ConsolidatedTimeRegister2(ReadOnlyfromClassic--Normally,MNGPwillClassictimefromitsbatterybackedRTC through file transfer)
    # Name Value Description
    # BITS 11:0 1to366* Day of year value in the range of 1 to 365 * (366 for leap years)
    # BITS 31:12 RESERVED RESERVED
     
    dayOfYearMask = 0x0fff
    dayOfYearShift = 0
    dayOfYear = CTime2 & dayOfYearMask
    
    #String values attempt to hand format BUT doesn't account for zero prefixes
    # tval  = "T"
    # zval  = "Z"
    # colon=":"
    # dash="-"
    # # example ISO860 date format ISODate("2014-09-17T23:25:56.314Z")
    # isoval = str(year)+dash+str(month)+dash+str(day)+tval
    # isoval += str(hr)+colon+str(mins)+colon+str(sec)+zval
    # print isoval

    # use library to proprly format ISO860 date
    d = datetime.datetime(year, month, day, hrs, mins, sec)
    format = "%Y-%m-%dT%H:%M:%SZ"

    today = datetime.datetime.today()
    print 'today ISO datetime default  :', today

    self.deviceTime = d.strftime(format)

    print 'ctime utc assume appended Z strptime iso-Z:', d.strftime(format)
    #print "assume utc time with appended Z"
    #print '{%Y-%m-%dT%H:%M:%SZ}'.format(d)
    #'{:%Y-%m-%d %H:%M:%S}'.format(d)
    # format = ":%Y-%m-%dT%H:%M:%S.0-07:00"
    # print "assume offset of PST but does not account for daylight savings time"
    # #print "{:%Y-%m-%dT%H:%M:%S.0-07:00}".format(d)
    # print  d.strftime(format)
    
    return self.deviceTime

  def setTestData():
    # SAMPLE DATA
    # example:
    # CTime0r1,1044  == 0x0414 # CTime0r0,13066 == 0x330A  
    # dayofweek=0x04 hr=0x14 min=0x33 sec=0x0A
    # 
    CTime0r0 = 13066
    CTime0r1 = 1044

    # CTime1r0,1556  == 0x614
    # CTime1r1,2016  == 0x800
    # year=0x800 month=0x6 day=0x14
    CTime1r0 = 1556
    CTime1r1 = 2016

    # CTime2a,463,0x1CF
    # dayofyear=0x1CF (463 days out of 365, seems odd since jan1)
    CTime2 = 463
    # 4 byte registers
    # CTime0r0/b 4214, 4215
    # CTime1r0/b 4216, 4217
    # Ctime2    4218
    #

