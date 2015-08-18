"""
 Cisco Nexus 9000 Switch On-Box script for configuring
 sparse-mode under all IP numbered interfaces.
"""
from cli import *

class OspfInterface(object):

   def __init__(self):
      """ No variables are required for this class. """
   
   def print_Banner(self):
      msg = '   _   _   _   _     _   _   _   _ '
      msg += '\n  / \\ / \\ / \\ / \\   / \\ / \\ / \\ / \\'
      msg += '\n ( O | S | P | F ) ( D | e | m | o )'
      msg += '\n  \\_/ \\_/ \\_/ \\_/   \\_/ \\_/ \\_/ \\_/'
      msg += '\n\nCisco Nexus 9000 Switch On-Box script'
      msg += '\nfor configuring OSPF interface attributes.'
      msg += '\nDeveloped By: OneCloud Consulting\n'
      msg += 'Please contact info@1-cloud.net for any queries.\n'
      print msg

   def print_Menu(self):
      print "-"*30 + "   Menu Options   " + "-"*31
      print "1) Configure 'ip router ospf 1 area 0.0.0.0' under all IP numbered interfaces."
      print "2) Remove 'ip router ospf 1 area 0.0.0.0' from all IP numbered interfaces."
      print "3) Configure 'ip router ospf cost 65535' under all IP numbered Ethernet interfaces."
      print "4) Remove 'ip router ospf cost 65535' from all IP numbered Ethernet interfaces."
      print "\nType any other key to exit menu."
      print "-"*79

   def configure_ospf_area(self):
      show_int_brief = []
      show_int_brief = cli('show ip int brief | inc Eth|Lo')

      interfaces = show_int_brief.split( )

      cli_commands = "conf ; router ospf 1"

      for i in xrange(0, len(interfaces) ,3):
         cli_commands += " ; interface " + str(interfaces[i])
         cli_commands += " ; ip router ospf 1 area 0.0.0.0"

      print "You are about to configure OSPF 1 (Area 0.0.0.0) under all IP numbered interfaces."

      confirm = raw_input("Are you sure? [y|n]")

      if confirm == "y":
         cli(cli_commands)
         result = cli('show ip ospf interface brief')
         print result
         print "OSPF process ID 1 (Area 0.0.0.0) enabled on all IP numbered interfaces!\n"
         cli('show ip ospf int brief')
         return
      else:
         print "You chose not to commit. Script aborted."
         return


   def remove_ospf_area(self):
      show_int_brief = []
      show_int_brief = cli('show ip int brief | inc Eth|Lo')

      interfaces = show_int_brief.split( )

      cli_commands = "conf"

      for i in xrange(0, len(interfaces) ,3):
         cli_commands += " ; interface " + str(interfaces[i])
         cli_commands += " ; no ip router ospf 1 area 0.0.0.0"

      print "You are about to remove OSPF process ID 1 (Area 0.0.0.0) from all IP numbered interfaces."

      confirm = raw_input("Are you sure? [y|n]")
      if confirm == "y":
         cli(cli_commands)
         print "\nOSPF process ID 1 (Area 0.0.0.0) removed from all IP numbered interfaces!\n"
         print "Type 'show ip ospf interface brief' to verify.\n"
         return
      else:
         print "You chose not to commit. Script aborted."
         return

   def configure_ospf_cost(self):
         show_int_brief = []
         show_int_brief = cli('show ip int brief | inc Eth')

         interfaces = show_int_brief.split( )

         cli_commands = "conf"

         for i in xrange(0, len(interfaces) ,3):
            cli_commands += " ; interface " + str(interfaces[i])
            cli_commands += " ; ip ospf cost 65535"

         print "You are about to configure 'ip ospf cost 65535' under all IP numbered Ethernet interfaces."

         confirm = raw_input("Are you sure? [y|n]")

         if confirm == "y":
            cli(cli_commands)
            result = cli('show ip ospf interface brief')
            print result
            print "'ip ospf cost 65535' configured on all IP numbered Ethernet interfaces!\n"
            return
         else:
            print "You chose not to commit. Script aborted."
            return

   def remove_ospf_cost(self):
            show_int_brief = []
            show_int_brief = cli('show ip int brief | inc Eth')

            interfaces = show_int_brief.split( )

            cli_commands = "conf"

            for i in xrange(0, len(interfaces) ,3):
               cli_commands += " ; interface " + str(interfaces[i])
               cli_commands += " ; no ip ospf cost 65535"

            print "You are about to remove 'ip ospf cost 65535' under all IP numbered Ethernet interfaces."

            confirm = raw_input("Are you sure? [y|n]")

            if confirm == "y":
               cli(cli_commands)
               result = cli('show ip ospf interface brief')
               print result
               print "'no ip ospf cost 65535' configured on all IP numbered Ethernet interfaces!\n"
               return
            else:
               print "You chose not to commit. Script aborted."
               return

if __name__ == '__main__':
   foo = OspfInterface()
   foo.print_Banner()
   foo.print_Menu()
   option = raw_input("\nSelect option [1-4]:")

   if option == "1":
      foo.configure_ospf_area()
   elif option == "2":
      foo.remove_ospf_area()
   elif option == "3":
      foo.configure_ospf_cost()
   elif option == "4":
      foo.remove_ospf_cost()
