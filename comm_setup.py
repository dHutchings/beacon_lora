import serial

ser = serial.Serial('/dev/ttyACM1',115200,timeout=1)


#first set of commands come direct from docu sheet given by Christine
ser.write("AT\n\r")
print(ser.readlines())

ser.write("AT+FSB=7\n\r")
print(ser.readlines())

ser.write("AT+ni=1,bconduit\n\r")
print(ser.readlines())

ser.write("AT+nk=1,CO2Network2012\n\r")
print(ser.readlines())


#this one I found.  Replies are put in ASCII, not hex.
ser.write("AT+RXO=1\n\r")
print(ser.readlines())

#and now join
ser.write("AT+join\n\r")
print(ser.readlines())

#I close the port here so a minicom can come through and get into it.  It will be correctly configured to immediately send using the 
#AT_send= command.
ser.close()