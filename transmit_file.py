import comm_handler
import time
import sys
import serial
import csv
import os
global ser

def printv(string,verbose,alt_print=None):
    #If I am verbose, print the string.
    #Else, do nothing, unless there is an alt print (at which point, print it)

    if verbose:
        print string
    else:
        if alt_print is not None:
            print alt_print

def setup_mdots(port,attempts,verbose = True):
    #the bulletproofed setup of the mdots radio
    if port is None:
        raise UserWarning("Must have a com port...")

    setup= False
    setup_counts = attempts

    while (not setup) and (setup_counts > 0)  :
        setup_counts = setup_counts - 1
        try:
            ser = serial.Serial(port,115200,timeout=1)
            comm_handler.setup_radio(ser)
            setup = True
        except IOError,e:
            printv("Transmission Failed...",verbose)
            printv(e,verbose)
            time.sleep(1)
        except OSError,e:
            printv("Resource unavailable?  Try again",verbose)
            printv(e,verbose)
            time.sleep(1)
        except:
            printv("Other kind of error... neeed to exit",verbose)
            e = sys.exc_info()[0]
            printv(e,verbose)
            try:
                ser.close()
            except:
                e = sys.exc_info()[0]
            printv("",verbose,alt_print=0)
            sys.exit()

    if(setup_counts == 0):
        printv("Attemps to setup Exhausted.  Exiting",verbose,alt_print=0)
        try:
            ser.close()
        except:
            printv("Can't close serial port",verbose)
        return 0

    return 1


def set_time(attempts=999,verbose= True):
    #function that sets the system time to whatever the multitech router thinks it is.
    global ser
    done = False
    setup_attempts = attempts

    while (not done) and (setup_attempts > 0):
        setup_attempts = setup_attempts - 1
        try:
            date_str = comm_handler.get_time()
            date_str = date_str[:-15] #trim off the  GMT+0000 (UTC)
            date_str = "'" + date_str + " UTC'" #and format it the way linux likes it.
            os.system("sudo date -s %s" % date_str) #and run the command with sudo.  As long as visudo has been done, this should run without error
            done = True
        except e:
            printv(e,verbose)


def transmit_file(file_name,attempts=999,verbose= True):
    global ser

    if file is None:
        raise UserWarning("Must have a datafile to transmit") 

    start_time = time.time()
    #now, start transmitting the .csv file
    f = open(args.filename, 'r')
    reader = csv.reader(f)
    
    for row in reader:
        #each row is a list of values.  Have to glue them back together into a single string.
        data = ','.join(row)
        
        sent = False
        send_counts = attempts

        while (not sent) and (send_counts > 0):              
            send_counts = send_counts -1
            try:
                comm_handler.send_data(data,delay=2)
                sent = True
            except IOError,e:
                printv("transmission failed... try again",verbose)
                printv(e,verbose)
                time.sleep(1)
            except OSError,e:
                printv("Resource unavailable?  Try again",verbose)
                printv(e,verbose)
                time.sleep(1)

            except:
                printv("Other kind of error... neeed to exit",verbose,alt_print=0)
                try:
                    ser.close()
                except:
                    printv("Can't close serial port",verbose)
                sys.exit()

            if(send_counts == 0):
                printv("Attemps to send data exhausted. Exiting",verbose,alt_print=0)
                try:
                    ser.close()
                except:
                    printv("Can't close serial port",verbose)



    data_transmit = (time.time() - start_time)/60.0
    #print("Time to setup radio was " + str(radio_setup) + " sec")
    printv("Time to transmit was " + str(data_transmit) + " min",verbose)

    #I close the port here so a minicom can come through and get into it.  It will be correctly configured to immediately send using the 
    #AT_send= command.
    ser.close()
    
    printv("Success!",verbose,alt_print=1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Beacon LORA Project.  Python code for radio comms.  Returns 1 for successfully transmitted file, 0 for failure')
    parser.add_argument('--manual' , action='store_true',  default = False, help='Setup Radio, then exit, letting minicom use the Radio.  Defaults to false')
    parser.add_argument('--filename', default = None, help='Setup Radio, and then start transmitting data.')
    parser.add_argument('--port', type=str, help='The com port used for the mdot radio.')
    parser.add_argument('--attempts', type=int, default=999, help ="The number of times to attempt transmission before giving up.  Default is 999")
    parser.add_argument('--no_prints', action='store_true', default = False, help='No helpful error messages.  Only prints 1 (success) or 0 (faliure)')
    args = parser.parse_args()

    result = setup_mdots(args.port,args.attempts,verbose=args.no_prints)

    if (not args.manual) and (result is 1):
        set_time(args.attempts,verbose=args.no_prints)
        transmit_file(args.filename,attempts=args.attempts,verbose=args.no_prints)