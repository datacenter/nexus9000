"""
 Cisco Nexus 9000 Switch On-Box script for configuring
 sparse-mode under all IP numbered interfaces.
"""
from cli import *

class Pim(object):

   def __init__(self):
      """ No variables are required for this class. """
   
   def print_Banner(self):
      msg = '\n   _   _   _     _   _   _   _'
      msg += '\n  / \\ / \\ / \\   / \\ / \\ / \\ / \\'
      msg += '\n ( P | I | M ) ( D | e | m | o )'
      msg += '\n  \\_/ \\_/ \\_/   \\_/ \\_/ \\_/ \\_/'
      msg += '\n\nCisco Nexus 9000 Switch On-Box script'
      msg += '\nfor configuring sparse-mode under all IP numbered interfaces.\n'	
      msg += '\nDeveloped By: OneCloud Consulting\n'	
      msg += 'Please contact info@1-cloud.net for any queries.\n'
      print msg

   def print_Menu(self):
      print "-"*25 + "   Menu Options   " + "-"*25
      print "1) Configure 'ip pim sparse-mode' under all IP numbered interfaces."
      print "2) Remove 'ip pim sparse-mode' from all IP numbered interfaces."
      print "\nType any other key to exit menu."
      print "-"*68

   def configure_Pim(self):
      show_int_brief = []
      show_int_brief = cli('show ip int brief | inc Eth|Lo')

      interfaces = show_int_brief.split( )

      cli_commands = "conf"

      for i in xrange(0, len(interfaces) ,3):
         cli_commands += " ; interface " + str(interfaces[i])
         cli_commands += " ; ip pim sparse-mode"

      print "You are about to configure PIM sparse-mode under all IP numbered interfaces."

      confirm = raw_input("Are you sure? [y|n]")
      if confirm == "y":
         cli(cli_commands)
         result = cli('show ip pim interface brief')
         print result
         print "PIM successfully enabled on all IP numbered interfaces!\n"
         return
      else:
         print "You chose not to commit. Script aborted."
         return

   def remove_Pim(self):
      show_int_brief = []
      show_int_brief = cli('show ip int brief | inc Eth|Lo')

      interfaces = show_int_brief.split( )

      cli_commands = "conf"

      for i in xrange(0, len(interfaces) ,3):
         cli_commands += " ; interface " + str(interfaces[i])
         cli_commands += " ; no ip pim sparse-mode"

      print "You are about to remove PIM sparse-mode under all IP numbered interfaces."

      confirm = raw_input("Are you sure? [y|n]")

      if confirm == "y":
         cli(cli_commands)
         print "\nPIM successfully removed from all IP numbered interfaces!\n"
         print "Type 'show ip pim interface brief' to verify.\n"
         return
      else:
         print "You chose not to commit. Script aborted."
         return

if __name__ == '__main__':
   foo = Pim()
   foo.print_Banner()
   foo.print_Menu()
   option = raw_input("\nSelect option [1-2]:")

   if option == "1":
      foo.configure_Pim()
   elif option == "2":
      foo.remove_Pim()
