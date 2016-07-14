import serial
import time
def readlines_strip(serial):
	line = ser.readlines()
	return [s.rstrip() for s in line]

def send_AT_command(serial,command,delay=0):
	#sends the AT command, which is appended the\]n
	#returns the lines sent back, except in error cases
	
	serial.write(command + "\n")
	#the delay used for really long commands, like join or get time/
	time.sleep(delay)

	#answer may be many lines.  Use the custom readlines_strip command
	answer = readlines_strip(ser)
	if not(len(answer) > 0):
		raise IOError("no answer")
	elif "ERROR" in answer:
		print("AT command ERROR")
		raise(IOError("AT COMMAND ERROR " + str(answer)))
	elif not(answer[-1] == "OK"):
		raise(IOError("Did not terminate with OK ") + str(answer))
	else:
		return answer

	#if the last element is not 'OK', or if one of the elements is 'ERROR', there was an error.
	#at which point we return -1

ser = serial.Serial('/dev/ttyACM1',115200,timeout=1)

#first set of commands come direct from docu sheet given by Christine
#get attention of the router
send_AT_command(ser,"AT")
#setup my networking info, so I can join the network
send_AT_command(ser,"AT+ni=1,bconduit")
send_AT_command(ser,"AT+nk=1,CO2Network2012")

#this one I found.  Replies are put in ASCII, not hex.
send_AT_command(ser,"AT+RXO=1")

#now, join the network (with a long delay since it takes a while)
send_AT_command(ser,"AT+join",delay=10)

#I close the port here so a minicom can come through and get into it.  It will be correctly configured to immediately send using the 
#AT_send= command.
ser.close()