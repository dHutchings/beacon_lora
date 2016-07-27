import transmit_file


#the folder containing all the data... can have subfolders.
data_directory = "../"
#a list of all files that have been successfuly transmitted
transmission_log = "../transmit_log.txt"

#this will need to be identified somehow, currently, it's hardcoded.
port_name = "/dev/ttyACM1"

if [ ! -e $transmission_log ]; then
	#the transmission long doesn't exist... let's make one.
	touch $transmission_log

fi

for file in $(find $data_directory -name "*.csv"); do
	echo $file
	#check if this data is in the transmission file.
	#http://stackoverflow.com/questions/4749330/how-to-test-if-string-exists-in-file-with-bash-shell
	if ! grep -Fxq "$transmission_log" "$file";
	#if I haven't transmitted theis file yet (aka it's not in the transmission log)
	then
		#transmit the data... blocking untill success achieved.
		success=$(sudo python comm_setup.py --filename "$file" --port "$port_name")

		if [ $success == 1]; then		
			#them add the filename to the log file.
			echo "$file" >> "$transmission_log"
		fi
	fi
done