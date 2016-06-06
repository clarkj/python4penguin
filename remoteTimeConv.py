#!/usr/bin/python
#
# @brief convert MidNite solar modbus registers for time to ISO860 date format.
#
# produce iso date from register values
# example ISO 8601 date format ISODate("2014-09-17T23:25:56.314Z")
# @see MidNite Solar MODBUS Network Spec. Rev C.4 --- Dec 9, 2013
# http://www.midnitesolar.com/pdfs/classic_register_map_Rev-C5-December-8-2013.pdf
# method1: explictly pass in values with setValue(val0r0,val0r1,val1r0,val1r1,val2)
# method2: 
# methodx: Does not work - can not seem to inherit global values from caller
# assume a reference dictionary named df with registered mapped
# with specific name,value pairs
#  dictionary name "df" accessable as a global
#  pairs
#    CTime0r0 = df["CTime0r0"]
#    CTime0r1 = df["CTime0r1"]
#    CTime1r0 = df["CTime1r0"]
#    CTime1r1 = df["CTime1r1"]
#    CTime2 = df["CTime2"]
#
import datetime

class MidniteTimeConv:

  def __init__(self):
    """Define and interpret registers as a time string in UTC"""
    # global df
    self.deviceTime = 0
    self.CTime0r0 = 0x0
    self.CTime0r1 = 0x0
    self.CTime1r0 = 0x0
    self.CTime1r1 = 0x0
    self.CTime2   = 0x0
    self.format = "%Y-%m-%dT%H:%M:%SZ"

  def setTimeValues(self,val0r0, val0r1, val1r0, val1r1, val2):
    """set values of the five registers denoting time on the midnite device"""
    self.CTime0r0 = val0r0
    self.CTime0r1 = val0r1
    self.CTime1r0 = val1r0
    self.CTime1r1 = val1r1
    self.CTime2   = val2

  def setTimeRegDictionary(self):
    """non-operational set registers from global dictionary the midnite device"""
    # assume dictionary external with name df
    # global df
    # nonlocal df # error
    self.CTime0r0 = df["CTime0r0"]
    self.CTime0r1 = df["CTime0r1"]
    self.CTime1r0 = df["CTime1r0"]
    self.CTime1r1 = df["CTime1r1"]
    self.CTime2   = df["CTime2"]
  
  def getDeviceTime(self):
    """get time string from pre-defined register values"""
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
    sec = self.CTime0r0 & secMask
    # BITS 13:8 0to59 Minutes value in the range of 0 to 59
    # BITS 15:14 RESERVED RESERVED
    minsMask=0x3f
    minsShift=8
    mins  = (self.CTime0r0 >> minsShift) & minsMask
    # BITS 20:16 0to23 Hours value in the range of 0 to 23
    # BITS 23:21 RESERVED RESERVED 
    hrsMask=0x0f
    hrsShift=0
    hrs  = self.CTime0r1 & hrsMask
    # BITS 36:24 0to6 Day Of Week Day of week value in the range of 0 to 6
    # BITS 31:27 RESERVED RESERVED
    dayOfWeekMask = 0x0f
    dayOfWeekShift = 0
    dayOfWeek  = self.CTime0r1 & dayOfWeekMask
    
    # Table 4216-1 Consolidated Time Registers 1  Ctime1 r0/r1
    #  Name Value Description
    # BITS 4:0 1to28,29,39,31 Day of month value in the range of 1 to 28, 29, 30, or 31(depending on the month and whether it is a leap year)
    # BITS 7:5 RESERVED RESERVED
    dayMask = 0x1f
    dayShift = 0
    day = self.CTime1r0 & dayMask
    
    # BITS 11:8 1to12 Month value in the range of 1 to 12
    # BITS 15:12 RESERVED RESERVED
    monthMask = 0x0f
    monthShift = 8
    month = (self.CTime1r0 >> monthShift) & monthMask
    
    # BITS 27:16 0 to 4095 Year value in the range of 0 to 4095
    # BITS 31:28 RESERVED RESERVED
    yearMask = 0x0fff
    yearShift = 0
    year = self.CTime1r1 & yearMask
    
    # Table 4218-1 ConsolidatedTimeRegister2(ReadOnlyfromClassic--Normally,MNGPwillClassictimefromitsbatterybackedRTC through file transfer)
    # Name Value Description
    # BITS 11:0 1to366* Day of year value in the range of 1 to 365 * (366 for leap years)
    # BITS 31:12 RESERVED RESERVED
     
    dayOfYearMask = 0x0fff
    dayOfYearShift = 0
    dayOfYear = self.CTime2 & dayOfYearMask
    

    try:
      # use library to proprly format ISO860 date
      d = datetime.datetime(year, month, day, hrs, mins, sec)
      self.deviceTime = d.strftime(self.format)
      print 'success converting register time', d.strftime(self.format)
    except ValueError as err:
      print 'register value result in invalid data', err
      #String values attempt to hand format BUT doesn't account for zero prefixes
      tval  = "T"
      zval  = "Z"
      colon=":"
      dash="-"
      # # example ISO860 date format ISODate("2014-09-17T23:25:56.314Z")
      isoval = str(year).zfill(4)+dash+str(month).zfill(2)+dash+str(day).zfill(2)+tval
      isoval += str(hrs).zfill(2)+colon+str(mins).zfill(2)+colon+str(sec).zfill(2)+zval
      self.deviceTime = isoval
      print 'invalid register values found', isoval

    print 'return time derived from CTime registers assuming utc clock ', self.deviceTime
    # print 'register ctime utc assume appended Z strptime iso-Z:', d.strftime(self.format)
    #print "assume utc time with appended Z"
    #print '{%Y-%m-%dT%H:%M:%SZ}'.format(d)
    #'{:%Y-%m-%d %H:%M:%S}'.format(d)
    # format = ":%Y-%m-%dT%H:%M:%S.0-07:00"
    # print "assume offset of PST but does not account for daylight savings time"
    # #print "{:%Y-%m-%dT%H:%M:%S.0-07:00}".format(d)
    # print  d.strftime(format)
    
    return self.deviceTime

  def getTimeNow(self):
    """use time of day to over ridedevice time"""
    today = datetime.datetime.today()
    self.deviceTime = today.strftime(self.format)
    print 'today ISO datetime default  :', today
    return self.deviceTime

  def setTimeTestRegisters(self):
    """set fixed test time registers"""
    # SAMPLE DATA
    # example:
    # CTime0r1,1044  == 0x0414 # CTime0r0,13066 == 0x330A  
    # dayofweek=0x04 hr=0x14 min=0x33 sec=0x0A
    # 
    self.CTime0r0 = 13066
    self.CTime0r1 = 1044

    # CTime1r0,1556  == 0x614
    # CTime1r1,2016  == 0x800
    # year=0x800 month=0x6 day=0x14
    self.CTime1r0 = 1556
    self.CTime1r1 = 2016

    # CTime2a,463,0x1CF
    # dayofyear=0x1CF (463 days out of 365, seems odd since jan1)
    self.CTime2 = 463
    # 4 byte registers
    # CTime0r0/b 4214, 4215
    # CTime1r0/b 4216, 4217
    # Ctime2    4218
    #

