Steps to deploy the service startup script
==========================================
1. How to get a file from git hub
   a) Download git to clone repository
      i)  sudo apt-get install git
      ii) git --version ( check for the version after successfull installation)
   b) move to "nexusdatabroker/serviceScripts/ubuntu" directory, copy ndb script to "/etc/init.d" directory.
   c) Change the permissions to 755 with this command "chmod 755 ndb"

2. Edit the following lines in the ndb script.
   a) JAVA_HOME  - Find the location of java and update the line
	  for example:JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre

   b) NDB_PATH - Update the location of the NDB
      for example: If the NDB is extracted under /home/user, then update path as /home/user/xnc 

3. Run with the following command to make ndb as a service even after crash/reboot
    a) Update-rc ndb enable

4. Start/stop the NDB using the below command.
      service ndb start/stop/status/restart
  
  The options:-

     start   -- Starts the process.

     stop    -- Stops the process.

     status  -- Displays whether the process is running or not and its process id.

     restart -- Stops and starts the process.
