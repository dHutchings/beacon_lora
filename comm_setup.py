import serial
import time
import argparse
import csv


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
        raise(IOError("Did not terminate with OK " + str(answer)))
    else:
        return answer

    #if the last element is not 'OK', or if one of the elements is 'ERROR', there was an error.
    #at which point we return -1

def get_time(serial):
    #gets the time string over the radio from the Multitech, using the control sequence +++
    answer = send_AT_command(ser,"AT+send=+++",delay=3)
    #reply is always the second line sent back... since first is the command itself.
    return answer[1]

def setup_radio(serial):
    #first set of commands come direct from docu sheet given by Christine
    #get attention of the router
    send_AT_command(ser,"AT")

    #setup my networking info, so I can join the network
    send_AT_command(ser,"AT+ni=1,bconduit")
    send_AT_command(ser,"AT+nk=1,CO2Network2012")
    send_AT_command(ser,"AT+FSB=7")

    #this one I found.  Replies are put in ASCII, not hex.
    send_AT_command(ser,"AT+RXO=1")

    #up the packet size, at cost of spread factor
    send_AT_command(ser,"AT+TXDR=7")

    #now, join the network (with a long delay since it takes a while)
    send_AT_command(ser,"AT+join",delay=10)

    print("Radio Setup sucessful")




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Beacon LORA Project.  Python code for radio comms')
    parser.add_argument('--manual' , action='store_true',  default = False, help='Setup Radio, then exit, letting minicom use the Radio.  Defaults to false')
    parser.add_argument('--filename', default = None, help='Setup Radio, and then start transmitting data.')
    parser.add_argument('--port', type=str, help='The com port used for the mdot radio.')
    args = parser.parse_args()
    
    print(args)

    if args.port is None:
        raise UserWarning("Must have a com port...")
    if (args.manual is False) and (args.filename is None):
        raise UserWarning("Must have a datafile to transmit") 

    ser = serial.Serial(args.port,115200,timeout=1)
    setup_radio(ser)

    time.sleep(1)

    if not args.manual:
        #http://www.pythonforbeginners.com/csv/using-the-csv-module-in-python
        f = open(args.filename, 'r')
        reader = csv.reader(f)
        for row in reader:
            #each row is a list of values.  Have to glue them back together into a single string.
            data = ','.join(row)
            print(len(data))
            send_AT_command(ser,"AT+send="+str(data),delay=3)

            print(str(data))
        #transmit data here... or something.
        pass

    #I close the port here so a minicom can come through and get into it.  It will be correctly configured to immediately send using the 
    #AT_send= command.
    ser.close()


#print(get_time(ser))

#

