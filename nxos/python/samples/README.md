Nexus 9000 Sample Python Scripts
------------------------

These scripts are intended to show very simple examples of what can be done with Python on the Nexus 9000 standalone switch.  Python on the Nexus 9000 standalone switch is very similar to python on just about any other Linux based system except it has some extra packages and modules to interact with NX-OS.

In addition to interact with NX-OS commands, you must import the cli module into the global name space in order to get access to the cli(), clip() and clid() functions, for example:

```python
from cli import *
clip('show version')
```

The cli functions work differently on the Nexus 9000 than they do on other NX-OS platforms.  When you execute a cli command using them, the context in which that cli command executes in is created and then destroyed for the life of the command.  So if you are doing commands that build state, go into command submodes (configuration for example) or otherwise build on top of eachother, you will need to execute the commands in a single cli function call and separate them with a space semicolon (' ;').  For example:

```python
from cli import *
cli('configure terminal ;interface loopback 231 ;ip address 10.10.10.1/24 ;shutdown')
```

The Nexus 9000 allows you to run Python scripts in many different ways:

- source scriptname : assuming the script is in bootflash:///scripts and has the proper shebang of #!/usr/bin/env python
- python scriptname : from the NX-OS commandline and Bash
- run bash python scriptname : assuming the bash shell feature is enabled and the user has permission to run bash
- run bash and then python scriptname
- run the script from an EEM policy action
- run the script from the scheduler
- run the script as a NX-OS command modifier, i.e. show version | source scriptname args