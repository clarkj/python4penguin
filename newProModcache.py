#!/usr/bin/python
# Name: modcache.py
# Author: Andrew Meares
# Date: 6/5/2013
# Description:
# Caches a selection of Modbus TCP registers from a device in a local file.
# tab = \t
import sys
import csv
import time
import argparse
from pymodbus.client.sync import ModbusTcpClient as ModbusClient


#-------------------------------------------------------------------------------
# Settings
#-------------------------------------------------------------------------------
PROGRAM_DESCRIPTION = 'A utility for caching Modbus TCP holding registers.'
DEFAULT_PATH = 'cache.csv'
DEFAULT_RPATH = 'midnite.reg'
#DEFAULT_IP = '192.168.1.100'
DEFAULT_IP = '10.10.10.21'
DEFAULT_PORT = 502
DEFAULT_ADDRESS = 4100
DEFAULT_COUNT = 1


#-------------------------------------------------------------------------------
# Arguments
#-------------------------------------------------------------------------------
class Arguments:
	def __init__(self):
		# setup the command line arguments
		self.parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
		# add the arguments
		self.parser.add_argument('-c', '--cachefile', help='Cache path', type=str, default=DEFAULT_PATH)
		self.parser.add_argument('-r', '--registerfile', help='Register list path', type=str, default=DEFAULT_RPATH)
		self.parser.add_argument('-i','--ip', help='Modbus device IP address', type=str, default=DEFAULT_IP)
		self.parser.add_argument('-p','--port', help='Modbus device port', type=int, default=DEFAULT_PORT)
		# parse the command line arguments
		self.args = self.parser.parse_args()
		
	def get(self):
		return self.args


#-------------------------------------------------------------------------------
# ModbusDevice
#-------------------------------------------------------------------------------
class ModbusDevice:	
	# ModbusDevice
	# i - IP address
	# p - Modbus port
	def __init__(self, i, p):
		self.ip = i
		self.port = p
		self.rKeys = []
		self.rValues = []
		self.errors = []
		self.errFlag = False	# False = no errors, True = we had errors
		# Create the client
		try:
			self.client = ModbusClient(self.ip, self.port)
		except Exception, e:
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
			mr = self.client.read_holding_registers(start, len(keys))
		except Exception, e:
			self.errors.append(str(e))
			self.errFlag = True
			# save zeros
			self.rKeys.extend(keys)
			self.rValues.extend([0] * len(keys))			
		else:
			self.rKeys.extend(keys)
			self.rValues.extend(mr.registers)
	
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




#-------------------------------------------------------------------------------
# Main Program
#-------------------------------------------------------------------------------
cmdArgs = Arguments()
args = cmdArgs.get()
        
try:
	# try to open the register file
	rfile = open(args.registerfile, "r")
except Exception, e:
	print str(e)
	exit(1)

try:
	# try to open the cache file
	ofile  = open(args.cachefile, "w")
except Exception, e:
	print str(e)
	exit(1)

# Create the CSV writer
writer = csv.writer(ofile)
# Create the register file reader
regReader = csv.reader(rfile)

# Create to the Modbus device
device = ModbusDevice(args.ip, args.port)


# Read the register file
# Figure out which registers to grab and what their names are
regCount = 0
blockStart = 0
blockKeys = []
#blockRegs = []
#blockIndex = []
for row in regReader:
	if (regCount==0):
		# get first item, default length of 1
		blockKeys.append(row[0])
#                blockRegs.append(row[1])
#                blockIndex.append(regCount)
		blockStart = int(row[1])-1
		regCount = regCount + 1
                # print "hi",str(row[0])," ", str(row[1]), " ", regCount
	else:
		# if the next item is adjacent, add it to the block
		if (int(row[1])-1 == blockStart+len(blockKeys)):
			blockKeys.append(row[0])
#                blockRegs.append(row[1])
#                blockIndex.append(regCount)
			regCount = regCount + 1
                        # print "hi2",str(row[0])," ", str(row[1]), " ", regCount
		else:
		
	# The next item is not adjacent so handle the block
			device.addRegisterBlock(blockKeys, blockStart)
			blockKeys = []
#blockRegs = []
#blockIndex = []
			blockKeys.append(row[0])
#                blockRegs.append(row[1])
#                blockIndex.append(regCount)
			blockStart = int(row[1])-1
			regCount = regCount + 1
                        # print "hi3",str(row[0])," ", str(row[1]), " ", regCount
			
device.addRegisterBlock(blockKeys, blockStart)

# Turn it into a dictionary
# dr = dict(zip(device.getKeys(),device.getValues()))
dr = dict(zip(device.getKeys(),device.getValues()))

# Put in the timestamp
dr["Time"] = time.time()

# Put in the Success value
if (device.getErrFlag()):
	dr["Status"] = "Error"
else:
	dr["Status"] = "Success"
	
# Write to the CSV file
for k,v in sorted(dr.items()):
	writer.writerow([k, v])

# Close the CSV file
ofile.close()
rfile.close()
