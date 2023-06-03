"""
 Cisco Nexus 9000 Switch On-Box script for cleaning
 repetitive switch configurations such as disabling
 features, removing IP addresses from all interfaces,
 and so on.
"""
from cli import *
import time

class Cleanup(object):

   def __init__(self):
      """ No variables are required for this class. """
   
   def print_Banner(self):
      msg = '\n   _   _   _   _   _   _   _'
      msg += '\n  / \\ / \\ / \\ / \\ / \\ / \\ / \\'
      msg += '\n ( C | l | e | a | n | u | p )'
      msg += '\n  \\_/ \\_/ \\_/ \\_/ \\_/ \\_/ \\_/'
      msg += '\n\nCisco Nexus 9000 Switch On-Box script'
      msg += '\nfor cleaning repetitive switch configurations.\n'
      msg += '\nDeveloped By: OneCloud Consulting\n'	
      msg += 'Please contact info@1-cloud.net for any queries.\n'
      print msg

   def print_Menu(self):
      print "-"*25 + "   Menu Options   " + "-"*25
      print "1) Remove all 'feature' CLI statements."
      print "2) Remove 'ip pim sparse-mode' from all interfaces."
      print "3) Remove IP addresses from all interfaces."
      print "4) Remove all configured Loopback interfaces."
      print "5) Remove all configured 'vrf context' except management."
      print "6) Remove descriptions from all interfaces."
      print "7) Run all of the above."
      print "\nType any other key to exit menu."
      print "-"*68

   def remove_Feature(self):
      # This function assumes all configured feature statements are comprised of 2 words.
      # In the case of 'feature nv overlay', 3 words are used.
      # To workaround this, explicitly remove 'feature nv overlay'.
      cli('conf ; no feature nv overlay')
      time.sleep(5)  # wait 5 seconds for above command to get removed

      #Now parse and iterate across output of 'show run | include feature'
      show_run_feature = []
      show_run_feature = cli('show run | inc feature')

      feature = show_run_feature.split( )

      cli_commands = "conf"

      for i in xrange(1, len(feature) ,2):
         cli_commands += " ; no feature " + feature[i]

      if len(feature) == 0:
         print "There are no features to remove."
      else:
         print "You are about to remove all 'feature' CLI statements."

         confirm = raw_input("Are you sure? [y|n]")
         if confirm == "y":
            cli(cli_commands)
            result = cli('show run | inc feature')
            print result
            print "All 'feature' CLI statements removed!\n"
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

      print "You are about to remove PIM sparse-mode under all interfaces."

      confirm = raw_input("Are you sure? [y|n]")

      if confirm == "y":
         cli(cli_commands)
         print "\nPIM successfully removed from all interfaces!\n"
         print "Type 'show ip pim interface brief' to verify.\n"
         return
      else:
         print "You chose not to commit. Script aborted."
         return

   def remove_Ipaddress(self):
         show_int_brief = []
         show_int_brief = cli('show ip int brief | inc Eth|Lo')

         interfaces = show_int_brief.split( )

         cli_commands = "conf"

         for i in xrange(0, len(interfaces) ,3):
            cli_commands += " ; interface " + str(interfaces[i])
            cli_commands += " ; no ip address"

         print "You are about to remove IP addresses from all interfaces."

         confirm = raw_input("Are you sure? [y|n]")

         if confirm == "y":
            cli(cli_commands)
            print "\nIP addresses successfully removed from all interfaces!\n"
            print "Type 'show ip interface brief' to verify.\n"
            return
         else:
            print "You chose not to commit. Script aborted."
            return

   def remove_Loopbacks(self):
            show_int_brief = []
            show_int_brief = cli('show int brief | inc Lo')

            interfaces = show_int_brief.split( )

            cli_commands = "conf"

            for i in xrange(0, len(interfaces) ,3):
               cli_commands += " ; no interface " + str(interfaces[i])

            print "You are about to remove all Loopback interfaces."

            confirm = raw_input("Are you sure? [y|n]")

            if confirm == "y":
               cli(cli_commands)
               print "\nAll Loopback interfaces removed!\n"
               print "Type 'show interface brief | inc Loopback' to verify.\n"
               return
            else:
               print "You chose not to commit. Script aborted."
               return

   def remove_Vrf_Contexts(self):
            show_run = []
            show_run = cli('show run | include context | exclude management')

            contexts = show_run.split( )

            cli_commands = "conf"

            for i in xrange(2, len(contexts) ,3):
               cli_commands += " ; no vrf context " + str(contexts[i])
            print "You are about to remove all vrf contexts (except management)."

            confirm = raw_input("Are you sure? [y|n]")

            if confirm == "y":
               cli(cli_commands)
               print "\nAll vrf contexts removed!\n"
               print "Type 'show run | inc context' to verify.\n"
               return
            else:
               print "You chose not to commit. Script aborted."
               return

   def remove_Interface_Descriptions(self):
               show_int_brief = []
               show_int_brief = cli('show int brief | json-pretty | inc interface | exc TABLE | exc ROW')
               interfaces = show_int_brief.replace(',', '')
               interfaces = interfaces.replace('"', '')

               interfaces = interfaces.split( )

               cli_commands = "conf"

               for i in xrange(1, len(interfaces) ,2):
                  cli_commands += " ; interface " + str(interfaces[i] + " ; no description")

               print "You are about to remove descriptions from all interfaces."

               confirm = raw_input("Are you sure? [y|n]")

               if confirm == "y":
                  cli(cli_commands)
                  print "\nRemoved descriptions from all interfaces!\n"
                  print "Type 'sh run | include description' to verify.\n"
                  return
               else:
                  print "You chose not to commit. Script aborted."
                  return

if __name__ == '__main__':
   foo = Cleanup()
   foo.print_Banner()
   foo.print_Menu()
   option = raw_input("\nSelect option [1-7]:")

   if option == "1":
      print "This may take some time..."
      foo.remove_Feature()
   elif option == "2":
      check = cli('show feature | inc pim')
      check_enabled = check.split()
      if check_enabled[2] == "disabled":
        print "There are no interfaces with 'ip pim sparse-mode' configured."
      elif check_enabled[2] == "enabled":
        foo.remove_Pim()
   elif option == "3":
      foo.remove_Ipaddress()
   elif option == "4":
      foo.remove_Loopbacks()
   elif option == "5":
      foo.remove_Vrf_Contexts()
   elif option == "6":
      foo.remove_Interface_Descriptions()
   elif option == "7":
      print "Checking configured features. This may take some time..."
      foo.remove_Feature()
      foo.remove_Ipaddress()
      foo.remove_Loopbacks()
      foo.remove_Pim()
      foo.remove_Vrf_Contexts()
