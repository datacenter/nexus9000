Steps to deploy the service startup script
==========================================

1. Edit the following lines in the ndb script.
   a) JAVA_HOME  - Find the location of java and update the line
	  for example:JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre

   b) NDB_PATH - Update the location of the NDB
      for example: If the NDB is extracted under /home/user, then update path as /home/user/xnc 

2. Copy the script under /etc/init.d/ 

3. Start/stop the NDB using the below command.
      service ndb start/stop/status/restart
  
  The options:-

     start   -- Starts the process.

     stop    -- Stops the process.

     status  -- Displays whether the process is running or not and its process id.

     restart -- Stops and starts the process.
