Nexus Data Broker as a Service Tips
===================================

 1) Copy the file in /etc/init.d/ folder with ndb name

 2) export the JAVA_HOME varible in the script

 3) Update the NDB_PATH varible with your ndb installed upto xnc/ folder

    for example: If I have runxnc which i want to run and availble under this path "/home/user/NDB/xnc"

    then in the ndb script update "NDB_PATH=/home/chandanvm/NDB3.1-83/xnc"

 4) Save the file and execute the NDB as a Service

 5) Below are the options availble for this

     start  -- starts the process

     stop   -- stops the process

     status -- displays whether the process is running or not

     restart -- stops and starts the process


 6) command used to for NDB as a Service.

     service ndb start/stop/status/restart
