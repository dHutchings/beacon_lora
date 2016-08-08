#!/bin/bash

#script that transmits all the data...

#First, make sure that more than one of this script isn't running at the same time.  
#Thanks to: http://bencane.com/2015/09/22/preventing-duplicate-cron-job-executions/  for the implimentation of this part.
PIDFILE="/home/doug/Desktop/beacon_lora/transmit_data.pid"


if [ -f $PIDFILE ] #if there is a PID file
then
	#get the PID currently in the PID file.
	PID=$(cat $PIDFILE)
	ps -p $PID > /dev/null 2>&1
	if [ $? -eq 0 ]
	then
		echo "Process already running"
		exit 1
	else
		# Process not found assume not running.
		#it prossibly crashed, (or was ctrl-c'd), and it didn't remove the PID file.
		echo $$ > $PIDFILE
		if [ $? -ne 0 ]
		then
			echo "Could not create PID file"
			exit 1
		fi
	fi
else
	#ok, there is no other PID file... that means for sure that no other process is running
	echo $$ > $PIDFILE
	#load my PID into the PID file
	if [ $? -ne 0 ] #if the exit code on that command (finding out my PID) is an error
	then
		echo "Could not create PID file"
		exit 1
	fi
fi

#ok, now I can get on to the buisness of transmitting my data.



#the folder containing all the data... can have subfolders.
data_directory="/home/doug/Desktop/beacon_lora/2016_06"
#a list of all files that have been successfuly transmitted
transmission_log="/home/doug/Desktop/beacon_lora/transmit_log.txt"

#this port name will always be guranteed, thanks to udev rules.
port_name="/dev/radio"

if [ ! -e $transmission_log ]; then
	#the transmission long doesn't exist... let's make one.
	touch $transmission_log

fi

echo "Transmiting..."

for file in $(find $data_directory -name "*.csv"); do
	echo $file
	#check if this data is in the transmission file.
	#http://stackoverflow.com/questions/4749330/how-to-test-if-string-exists-in-file-with-bash-shell
	if ! grep -Fxq "$transmission_log" "$file";
	#if I haven't transmitted theis file yet (aka it's not in the transmission log)
	then
		#ok, i haven't transmitted it yet... 
		#but I can't transmit files that are still under construction.
		#each complete file is 719, 720, or 721 lines if it's complete.
		length=$(wc -l $file | cut -f1 -d" ") #length of the file, in lines.  Use the cut command to remove the unneeded text	
		if [ $length -ge 719 ]; 
		then
			#transmit the data... blocking untill success achieved.
			#don't need sudo thanks to udev rules setting the permissions to be 0666.
			success=$(python transmit_file.py --filename "$file" --port "$port_name" --attempts 1 --no_prints)
			echo $success
			if [ $success == 1 ]; then		
				#them add the filename to the log file.
				echo "$file" >> "$transmission_log"
			fi
		fi
	fi
done


#remove the PIDFILE, because we're done.
rm $PIDFILE
