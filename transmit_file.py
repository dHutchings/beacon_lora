import comm_handler
import time
import sys
import serial

global ser

def setup_mdots(port,attempts):
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
            print("transmission failed...")
            print(e)
            time.sleep(1)
        except OSError,e:
            print("Resource unavailable?  Try again")
            print(e)
            time.sleep(1)
        except:
            print("Other kind of error... neeed to exit")
            e = sys.exc_info()[0]
            print(e)
            try:
                ser.close()
            except:
                e = sys.exc_info()[0]
                return 0
            sys.exit()

    if(setup_counts == 0):
        print("Attemps to setup Exhausted.  Exiting")
        try:
            ser.close()
        except:
            print("Can't close serial port")
        return 0

    return 1

def transmit_file(file_name,attempts=999):
    global ser

    if file is None:
        raise UserWarning("Must have a datafile to transmit") 

    start_time = time.time()
    success = setup_mdots(file_name,attempts)
    if success == 0:
        #faliure
        return 0
    
    time.sleep(1)

    radio_setup = (time.time() - start_time)
    print("Time to setup radio was " + str(radio_setup) + " sec")



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
                print("transmission failed... try again")
                print(e)
                time.sleep(1)
            except OSError,e:
                print("Resource unavailable?  Try again")
                print(e)
                time.sleep(1)

            except:
                print("Other kind of error... neeed to exit")
                ser.close()
                sys.exit()

            if(send_counts == 0):
                print("Attemps to send data exhausted. Exiting")
                try:
                    ser.close()
                except:
                    print("Can't close serial port")
                return 0


        print(time.time() - old_time)
        old_time = time.time()

    data_transmit = (time.time() - start_time)/60.0
    #print("Time to setup radio was " + str(radio_setup) + " sec")
    print("Time to transmit was " + str(data_transmit) + " min")

    #I close the port here so a minicom can come through and get into it.  It will be correctly configured to immediately send using the 
    #AT_send= command.
    ser.close()
    return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Beacon LORA Project.  Python code for radio comms.  Returns 1 for successfully transmitted file, 0 for failure')
    parser.add_argument('--manual' , action='store_true',  default = False, help='Setup Radio, then exit, letting minicom use the Radio.  Defaults to false')
    parser.add_argument('--filename', default = None, help='Setup Radio, and then start transmitting data.')
    parser.add_argument('--port', type=str, help='The com port used for the mdot radio.')
    parser.add_argument('--attempts', type=int, default=999, help ="The number of times to attempt transmission before giving up.  Default is 999")
    args = parser.parse_args()

    result = setup_mdots(args.port,args.attempts)

    if (not args.manual) and (result is 1):
        transmit_file(filename,args.attempts)