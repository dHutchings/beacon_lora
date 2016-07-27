import comm_handler
import time
import sys
import serial

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

def transmit_file(file_name,attempts=999,verbose= True):
    global ser

    if file is None:
        raise UserWarning("Must have a datafile to transmit") 

    start_time = time.time()
    success = setup_mdots(file_name,attempts)
    if success == 0:
        #faliure
        printv("",verbose,alt_print=0)
    
    time.sleep(1)

    radio_setup = (time.time() - start_time)
    printv("Time to setup radio was " + str(radio_setup) + " sec",verbose)



    start_time = time.time()
    old_time = time.time()
    #now, start transmitting the .csv file
    f = open(args.filename, 'r')
    reader = csv.reader(f)
    for row in reader:
        #each row is a list of values.  Have to glue them back together into a single string.
        data = ','.join(row)
        
        sent = False
        sent_counts = args.attemps

        while (not sent) and (send_counts > 0):              
            try:
                #send_AT_command(ser,"AT+send="+str(data),delay=2)
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


        #print(time.time() - old_time)
        #old_time = time.time()

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
    parser.add_argument('--no_prints', action='store_false', default = True, help='No helpful error messages.  Only prints 1 (success) or 0 (faliure)')
    args = parser.parse_args()

    result = setup_mdots(args.port,args.attempts,verbose=args.no_prints)

    if (not args.manual) and (result is 1):
        transmit_file(filename,args.attempts)