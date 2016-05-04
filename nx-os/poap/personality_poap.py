#!/bin/env python
#md5sum="7ea194839b9f042d6f2f8509dba6a24b"
# The above is the (embedded) md5sum of this file taken without this line, 
# can be # created this way: 
# f=personality_poap.py ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i "s/^#md5sum=.*/#md5sum=\"$(md5sum $f.md5 | sed 's/ .*//')\"/" $f ; rm $f.md5
#
# This way this script's integrity can be checked in case you do not trust
# tftp's ip checksum. This integrity check is done by /isan/bin/poap.bin).
# The integrity of the files downloaded later (images, config) is checked 
# by downloading the corresponding file with the .md5 extension and is
# done by this script itself.

from poap.personality import POAPPersonality
import os

# Location to download system image files, checksums, etc.
download_path = "/var/lib/tftpboot" 
# The path to the personality tarball used for restoration
personality_tarball = "/var/lib/tftpboot/foo.tar"
# The protocol to use to download images/config
protocol = "scp" 
# The username to download images, the personality tarball, and the 
# patches and RPMs during restoration
username = "root" 
# The password for the above username
password = "passwd9000"
# The hostname or IP address of the file server
server = "2.1.1.1" 

# The VRF to use for downloading and restoration
vrf = "default"
if os.environ.has_key('POAP_VRF'):
    vrf = os.environ['POAP_VRF']
 
# Initialize housekeeping stuff (logs, temp dirs, etc.)
p = POAPPersonality(download_path, personality_tarball, protocol, username, password, server, vrf)

p.get_personality()
p.apply_personality()

sys.exit(0)

