#!/usr/bin/python
# Name: modcache.py
# Author: Andrew Meares
# Date: 6/5/2013
# Description:
# Caches a selection of Modbus TCP registers from a device in a local file.
# tab = \t
import sys
import math
import csv
import time
import argparse
import datetime
import os.path
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer as ModbusFramer


#-------------------------------------------------------------------------------
# Settings
#-------------------------------------------------------------------------------
PROGRAM_DESCRIPTION = 'A utility for caching Modbus TCP holding registers.'
DEFAULT_PATH = 'midnite.csv'
DEFAULT_RPATH = 'mid.reg'
DEFAULT_FILTER_IN = 'mid.reg'
#DEFAULT_FILTER_IN = 'midniteFilter.reg'
DEFAULT_IP = '172.25.2.103'
# DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 502
DEFAULT_ADDRESS = 4100
DEFAULT_ADDRESS_OFFSET = 1
DEFAULT_COUNT = 1
DEFAULT_OUT_DIRECTORY = 'data'
#DEFAULT_OUT_DIRECTORY = '.'
LOG_NONE=0
LOG_INFO=1
LOG_DEBUG=2
LOG_LEVEL=LOG_INFO

#-------------------------------------------------------------------------------
# Arguments
#-------------------------------------------------------------------------------
class Arguments:
	def __init__(self):
		# setup the command line arguments
		self.parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
		# set default filterOut filename to be on the floor module MinModul minute boundary
		MinModulo = 5 # every 1/5 minutes is good for testing, maybe 1/15 or 1/hour is better
		formatMin = "%M"
		todayMin = datetime.datetime.today().strftime(formatMin)
		minFloor = (int(todayMin) / int(MinModulo)) * int(MinModulo)
		# print("minuteFloor ", minFloor, "minute ", todayMin)
		formatHr = "%Y-%m-%dT%H:"
		todayFloor = datetime.datetime.today().strftime(formatHr)
		todayFloor = todayFloor + str(minFloor) + ".csv"
		# add the arguments
		self.parser.add_argument('-c', '--cachefile', help='Cache path', type=str, default=DEFAULT_PATH)
		self.parser.add_argument('-r', '--registerfile', help='Register list path', type=str, default=DEFAULT_RPATH)
		self.parser.add_argument('-f', '--filterIn', help='Filter list path', type=str, default=DEFAULT_FILTER_IN)
		self.parser.add_argument('-o', '--filterOut', help='Output file name', type=str, default=todayFloor)
		self.parser.add_argument('-d', '--directory', help='Output file directory path', type=str, default=DEFAULT_OUT_DIRECTORY)
		self.parser.add_argument('-i','--ip', help='Modbus device IP address', type=str, default=DEFAULT_IP)
		self.parser.add_argument('-p','--port', help='Modbus device port', type=int, default=DEFAULT_PORT)
		# parse the command line arguments
		self.args = self.parser.parse_args()

	def get(self):
		return self.args

#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)
log.setLevel(logging.ERROR)

#-------------------------------------------------------------------------------
# ModbusDevice
#-------------------------------------------------------------------------------
class ModbusDevice:
	# ModbusDevice
	# i - IP address
	# p - Modbus port
	# f - framer
	# t - timeout
	#def __init__(self, i, p, f, t):
	def __init__(self, i, p):
		self.ip = i
		self.port = p
		self.framer = ModbusFramer
		self.timeout = 1
		self.rKeys = []
		self.rValues = []
		self.rAddress = []
		self.rIndex = []
		self.errors = []
		self.errFlag = False	# False = no errors, True = we had errors
		# Create the client
		try:
			if(LOG_LEVEL >= LOG_DEBUG):
			  print "modbus client"
			self.client = ModbusClient(self.ip, self.port)
			#self.client = ModbusClient(self.ip, self.port, self.framer, self.timeout)
			#self.client = ModbusClient(self.ip, self.port, timeout=10)
			if(LOG_LEVEL >= LOG_DEBUG):
				print "modbus client connect"
			rc = self.client.connect()
			if(rc == False):
				self.errFlag = True
				self.errors.append(str())
				print "modbus connect returned ", rc
			else:
				if(LOG_LEVEL >= LOG_DEBUG):
					print "modbus connect finished"
		except Exception, e:
			print "modbus device initialization exception ", e
			self.errors.append(str(e))
			self.errFlag = True

	# addRegisterBlock
	# Adds and retrieves a sequential group of holding registers
	# keys - list of key names (also determines # of registers to grab)
	# start - start address
	def addRegisterBlock(self, keys, start):
		# Gets a block of Modbus registers
		# Connects, gets the registers, and adds them to the list
		try:
			if(LOG_LEVEL >= LOG_DEBUG):
				print "read holding registers block"
			mr = self.client.read_holding_registers(start, len(keys))
			if(LOG_LEVEL >= LOG_DEBUG):
				print "read finished ", mr
		except Exception, e:
			print "read exception ", e
			self.errors.append(str(e))
			self.errFlag = True
			# save zeros
			self.rKeys.extend(keys)
			self.rValues.extend([0] * len(keys))
		else:
			self.rKeys.extend(keys)
			self.rValues.extend(mr.registers)

	def addRegisterAddress(self, values):
		self.rAddress.extend(values)
		return
	
	def addRegisterIndex(self, index):
		self.rIndex.extend(index)
		return
	
	# Returns list of indicies orderered by register value
	def getAddress(self):
		return self.rAddress
	
	# Returns list of indicies ordering each key,value from file
	def getIndex(self):
		return self.rIndex

	# Returns True if there was an error
	def getErrFlag(self):
		return self.errFlag

	# Returns a list of all the error strings
	def getErrors(self):
		return self.errors

	# Returns the keys added
	def getKeys(self):
		return self.rKeys

	# Returns the values retrieved, 0 if error
	def getValues(self):
		return self.rValues

	# Closes the connection
	def __del__(self):
		self.client.close()


# Function definition for 
def getDeviceTime( df ):
	"Function uses dictionary to create device time based on register values"
	CTime0r0 = dr["CTime0r0"]
	CTime0r1 = dr["CTime0r1"]
	CTime1r0 = dr["CTime1r0"]
	CTime1r1 = dr["CTime1r1"]
	CTime2 = dr["CTime2"]
	print "device Current Time registers ", hex(CTime0r0), hex(CTime0r1), hex(CTime1r0), hex(CTime1r1), hex(CTime2)
	format = "%Y-%m-%dT%H:%M:%S"
	now = datetime.datetime.utcnow().strftime(format) + str("Z") # make sure charge controller set to GMT
	deviceTime="CTimeFixMe-" + now
	print deviceTime
	return deviceTime;


from midniteTimeConv import MidniteTimeConv

 # Function definition for
def getDeviceTime( df ): 
	"Function uses dictionary to create device time based on register values"
	mConv = MidniteTimeConv()
	mConv.setRegs(**df)
	deviceTime = mConv.getDeviceTime()

#      CTime0r0 = dr["CTime0r0"]
#      CTime0r1 = dr["CTime0r1"]
#      CTime1r0 = dr["CTime1r0"]
#      CTime1r1 = dr["CTime1r1"]
 #     CTime2 = dr["CTime2"]
#      print "device Current Time registers ", hex(CTime0r0), hex(CTime0r1), hex(CTime1r0), hex(CTime1r1), hex(CTime2)
#      format = "%Y-%m-%dT%H:%M:%S"
#      now = datetime.datetime.utcnow().strftime(format) + str("Z") # make sure charge controller set to GMT
#      deviceTime="CTimeFixMe-" + now
	print deviceTime
	return deviceTime;
       





#-------------------------------------------------------------------------------
# Main Program
#-------------------------------------------------------------------------------
cmdArgs = Arguments()
args = cmdArgs.get()

try:
	# try to open the register file
	rfile = open(args.registerfile, "r")
except Exception, e:
	print "open for read failed register file ", args.registerfile, str(e)
	exit(1)

try:
	# try to open the cache file
	ofile  = open(args.cachefile, "w")
except Exception, e:
	print "open for write failed cache file " , args.cachefile, str(e)
	exit(1)

filter = True
filterIn = True
filterOut = True

filterFileOutExists = False

try:
	# try to open the register filter input file
	filterFileIn = open(args.filterIn, "r")
except Exception, e:
	print "open for read failed filter file ", args.filterIn, str(e)
	filterIn = False
	filter = False

fullFileNameWithPath = args.directory + "/" + args.filterOut
if(filterIn):
	try:
		# if the file exists note that to avoid repeating headers
		if(os.path.isfile(fullFileNameWithPath)):
			filterFileOutExists = True
		# try to open the register filer output file
		## add code to verify directory exists and is writeable,
		### if not, create a writeable directory so that file write works,
		### if error, exit and tell why couldn't create output (because directory isn't writeable)
		# filterFileOut = open(args.filterOut, "a") # append to end of file
		filterFileOut = open(fullFileNameWithPath, "a") #append to end of file
	except Exception, e:
		print "open for write failed filter file ", fullFileNameWithPath, str(e)
		filterOut = False	
		filter = False

# Create the CSV writer
writer = csv.writer(ofile)
# Create the register file reader
regReader = csv.reader(rfile)

if(filter == True):
	# Create the display filter file
	filterReader = csv.reader(filterFileIn)
	df = dict()
	dfout = dict()
	format = "%Y-%m-%dT%H:%M:%S.%f"
	now = datetime.datetime.utcnow().strftime(format)[:-3] + str("Z")
	# today = datetime.datetime.today().strftime(format)
	print "current utc time to millisecond precision", now
	#add feild based on ms time application acquired modbus data and wrote to file

	df["_id"] = "_id"
	dfout["_id"] = int(time.time()) # don't multiply, changes notion of precision * 10
	
	df["dateOnPi"] = "dateOnPi"
	dfout["dateOnPi"] = now
	
	for row in filterReader:
		df[row[0]] = row[1]
		
		

# add default time
# dr["CTimeID"] = "CTimeID"
#deviceTime = "none"
#df["CTimeID"] = "CTimeID"
#dfout["CTimeID"] = deviceTime
#dr["CTimeID"] = deviceTime

# Create to the Modbus device
device = ModbusDevice(args.ip, args.port)

# Read the register file
# Figure out which registers to grab and what their names are
regCount = 0
blockStart = 0
blockKeys = []
blockAddress = []
blockIndex = []
for row in regReader:
	if (regCount==0):
		# get first item, default length of 1
		blockKeys.append(row[0])
		blockAddress.append(row[1])
		blockIndex.append(regCount)
		blockStart = int(row[1])-DEFAULT_ADDRESS_OFFSET
		regCount = regCount + 1
                # print "hi",str(row[0])," ", str(row[1]), " ", regCount
	else:
		# if the next item is adjacent, add it to the block
		if (int(row[1])-DEFAULT_ADDRESS_OFFSET == blockStart+len(blockKeys)):
			blockKeys.append(row[0])
			blockAddress.append(row[1])
			blockIndex.append(regCount)
			regCount = regCount + 1
                        # print "hi2",str(row[0])," ", str(row[1]), " ", regCount
		else:
			# The next item is not adjacent so handle the block
			device.addRegisterBlock(blockKeys, blockStart)
			device.addRegisterAddress(blockAddress)
			device.addRegisterIndex(blockIndex)
			blockKeys = []
			blockAddress = []
			blockIndex = []
			blockKeys.append(row[0])
			blockAddress.append(row[1])
			blockIndex.append(regCount)
			blockStart = int(row[1])-DEFAULT_ADDRESS_OFFSET
			regCount = regCount + 1
			# print "hi3",str(row[0])," ", str(row[1]), " ", regCount

device.addRegisterBlock(blockKeys, blockStart)
device.addRegisterAddress(blockAddress)
device.addRegisterIndex(blockIndex)

# Turn it into a dictionary
# dr = dict(zip(device.getKeys(),device.getValues()))
dr = dict(zip(device.getKeys(),device.getValues()))
dv = dict(zip(device.getAddress(), device.getKeys()))
di = dict(zip(device.getIndex(), device.getKeys()))

# Put in the timestamp
dr["Time"] = time.time()

## need a routine to get "deviceTime" from CTime registers and call field "_id" for data uniqueness
#dfout["Time"] = time.time()
#df["Time"] = "Time"

#deviceTime = getDeviceTime(dr)
#print "device time ", deviceTime

if (filter == True):
	# dr["CTimeID"] = "CTimeID"
# 	df["CTimeID"] = "CTimeID"
# 	dfout["CTimeID"] = deviceTime
# 	dr["CTimeID"] = deviceTime
 	filterWriter = csv.DictWriter(filterFileOut, df.keys())



# Put in the Success value
if (device.getErrFlag()):
	dr["Status"] = "Error"
else:
	dr["Status"] = "Success"

# Write to the CSV file
for k,v in sorted(dr.items()):
	writer.writerow([k, v])
	if(filter == True):
		if(k in df):
			dfout[k] = v
			
if(filter):	
	# if the filter file did not exist, thus was just created, write a header
	if(filterFileOutExists == False):
		filterWriter.writerow(dict((fn,fn) for fn in dfout.keys()))
	filterWriter.writerow(dfout)

# Close the CSV file
ofile.close()
rfile.close()
if(filterIn):
	filterFileIn.close()
if(filterOut):
	filterFileOut.close()
