import serial
import time
import argparse
import csv
import sys

serial = None

def readlines_strip():
    line = serial.readlines()
    return [s.rstrip() for s in line]

def send_AT_command(command,delay=0):
    #sends the AT command, which is appended the\]n
    #returns the lines sent back, except in error cases
    
    serial.write(command + "\n")
    #the delay used for really long commands, like join or get time/
    time.sleep(delay)

    #answer may be many lines.  Use the custom readlines_strip command
    answer = readlines_strip()
    if not(len(answer) > 0):
        raise IOError("no answer")
    elif "ERROR" in answer:
        print("AT Command Error")
        raise(IOError("AT command error " + str(answer)))
    elif not(answer[-1] == "OK"):
        raise(IOError("Did not terminate with OK " + str(answer)))
    else:
        return answer

    #if the last element is not 'OK', or if one of the elements is 'ERROR', there was an error.
    #at which point we return -1

def get_time():
    #gets the time string over the radio from the Multitech, using the control sequence +++
    answer = send_AT_command("AT+send=+++",delay=3)
    #reply is always the second line sent back... since first is the command itself.
    return answer[1]

def setup_radio(ser):
    #one argument: the serial connection
    global serial
    serial = ser
    #first set of commands come direct from docu sheet given by Christine
    #get attention of the router
    send_AT_command("AT")

    #setup my networking info, so I can join the network
    send_AT_command("AT+ni=1,bconduit")
    send_AT_command("AT+nk=1,CO2Network2012")
    send_AT_command("AT+FSB=7")

    #this one I found.  Replies are put in ASCII, not hex.
    send_AT_command("AT+RXO=1")

    #up the packet size, at cost of spread factor
    send_AT_command("AT+TXDR=7")

    #now, join the network (with a long delay since it takes a while)
    send_AT_command("AT+join",delay=10)

    print("Radio Setup sucessful")

def send_data(data,delay=0):
    send_AT_command("AT+send="+str(data),delay=2)
