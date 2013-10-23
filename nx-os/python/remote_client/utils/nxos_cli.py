# Copyright (C) 2013 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#      http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 

import copy
import datetime
import re
import sys
import socket
import nxos_utils

#import _cisco
from cisco.history import History

#this import does not work from this package
import xml.etree.ElementTree as xml

def _exec_cli(cliop):
    # capture, document command output, and rethrow exceptions from cli
    print nxos_utils.cli_ex(cliop)


def _get_cli_output(s):
    return nxos_utils.cli_ex(s)
    #if s.find('\n') < 0:
    #    return _get_status_from_prompt(_exec_cli(s))
    #return _get_merged_cli_output(s)


def _get_merged_cli_output(ml):
    so = [0, '']
    for s in ml.split('\n'):
        _merge(so, _get_status_from_prompt(_exec_cli(s)))
    return (so[0], so[1])


_op_prmpt_re = None

def _get_op_prompt_pat():
    global _op_prmpt_re
    if _op_prmpt_re is None:
        #prompt = _cisco.cli_prompt() or '__python__'
        prompt = '__python__'
        _op_prmpt_re = re.compile(prompt)
    return _op_prmpt_re


def _get_status_from_prompt(cliop):
    op, stat = _get_op_prompt_pat().split(cliop)
    return (eval(stat), op.replace('\r', ''))


def _merge(dst, new):
    dst[0] += new[0]
    dst[1] += new[1]


def cfg_if(port, desc=None, vlan=None,
           state=None, mode=None, allowedVlan=None,
           channelGroup=None):
    '''This function is deprecated, please use the Interface class.'''
    raise DeprecationWarning, 'This function is deprecated, please use the '\
            'Interface class.'    


def nxcli(str="", do_print=False):
    #import pdb; pdb.set_trace()
    o, s = '', str.strip()
    if s:
        o = _get_cli_output(s)
        st = 0
    if st:
        raise SyntaxError, 'Error running cli (VSH returned %d)\n%s\n%s' % (st, s, o)
    else:
        if do_print:
            print o
    return st, o



def show_queues(type=None):
    if type:
        if type in ['system', 'global']:
            return nxos_utils.cli_ex('show platform software qd info %s' % type)
    else:
        return nxos_utils.cli_ex('show platform software qd info interface %s' % type)
    return nxos_utils.cli_ex('show platform software qd info global')


def show_run(intf=None):
    if intf:
        return nxos_utils.cli_ex('show run int %s' % intf)
    return nxos_utils.cli_ex('show run')


class NXCLI(object):
    '''
        Generic NXCLI base class with useful utils
    '''
    
    def __init__(self, command="", do_print=True):
        self.command = command
        self.do_print = do_print
        self._run()

    def _run(self):
        self.status, self.raw_output = nxcli(self.command, self.do_print)
        if not self.status:
            self.processed_output = str(self.raw_output).split('\n')
            self.timestamp = datetime.datetime.now()
            History().add_command(copy.copy(self))
            self.parse_specific()

    #Returns the command output as a list. Each line is one element in the list

    def _get_indent_pat (self):
        try:
            return self._indent_pat
        except AttributeError:
            self._indent_pat = re.compile ('^\s*')
            return self._indent_pat

    def _get_indent_cnt (self, s):
        m = self._get_indent_pat ().search (s)
        return len (m.group ())

    def _get_indent_level (self, indent_stack, line):
        cur = self._get_indent_cnt (line)
        last = indent_stack[-1]
        delta = 0
        if last == cur:
            return delta
        elif last < cur:
            indent_stack.append (cur)
            return delta + 1
        else:
            while last > cur:
                indent_stack.pop()
                last = indent_stack[-1]
                delta -= 1
            if last == cur:
                return delta
        raise IndentationError, '%d space frond after %d' % (cur, last)

    def key_map (self, key):
        k = key.strip ()
        try:
            return self._key_map[k]
        except:
            return k.replace (' ', '_')

    def _numval (self, v):
        s = v.strip ()
        try:
            return int (s)
        except ValueError:
            return s

    @staticmethod
    def _run_cfg (cmds):
        o,e,s = nxos_utils.runVshCmdEx('configure terminal ; %s' % cmds)
        if s == 0:
            return True
        else:
            return False

    @staticmethod
    def _read_arg(arg, arg_name, format, arg_type_dict):
        from cisco.bgp import BGPSession
        '''
            Read in an argument for a NXCLI configuration command.

            Keyword arguments:
            arg -- the argument to read in
            arg_name -- the name of the argument used in the calling function
            format -- a string representing the format of the NXCLI configuration
                command using '%' where the arg goes. e.g. 'cli-command %'
            arg_type_dict -- a dictionary where the keys are possible types that 
                the argument can take and the values are a string representing 
                any checks that need to be done for that argument type.
                e.g. {int: 'x < 100', str: 'x.startswith('interface ')'}
            
            Returns:
                A string representation of the arg if it passed the checks.
                None if the argument did not pass the checks.
            
            Examples:

            Read in a string with no validation:
            arg = NXCLI._read_arg(name, 'name', 'name %', {str:None})

            Read in an integer with a boundary condition:
            arg = NXCLI._read_arg(id, 'id', 'switch-id %', {int: 'id < 10'})
            
            Read in an ipaddress as a 32 bit quantity or a string:
            arg = NXCLI._read_arg(hostname, 'hostname', 'hostname %',
                    {int: 'hostname >= 1 and hostname <= 4294967295', 
                        str:'socket.inet_aton(hostname)'})

        '''
        for arg_type in arg_type_dict.keys():
            if type(arg) == arg_type:
                if arg_type_dict[arg_type] is not None:
                    check = re.sub('\\b' + arg_name + '\\b', 'arg', 
                            arg_type_dict[arg_type])
                    try: 
                        ret = eval(check)
                    except socket.error: 
                        raise ValueError, ('%s not valid ip address, got %s' % 
                                (arg_name, str(arg)))
                    else: 
                        if not ret:
                            raise ValueError, ('%s not valid, acceptable '
                                    'values: %s' % (arg_name, 
                                        arg_type_dict[arg_type]))
                if arg_type in (int, long):
                    format = format.replace('%', '%d', 1)
                    return format % arg
                elif arg_type is str:
                    format = format.replace('%', '%s', 1)
                    return format % arg
                elif arg_type is bool:
                    return format
        raise ValueError, ('%s not valid, got %s(%s)' % 
                (arg_name, str(arg), str(type(arg))))

        
    @staticmethod
    def _read_arg_from_dict(args, arg_name, format, arg_type_dict, 
            raise_error_if_not_present=False):
        if args.has_key(arg_name):
            return NXCLI._read_arg(args[arg_name], arg_name, format, arg_type_dict)
        elif raise_error_if_not_present:
            raise AttributeError, 'Expected argument %s not present' % arg_name
        else:
            return ""

    @staticmethod
    def _add_no_if_present(cmd, args):
        if args.has_key('no') and cmd != "":
            return 'no ' + cmd
        else:
            return cmd

    def get_xml_dom_from_cli_output (self, text):
        # sanitize the XML removing [possible] junk before and after
        o = re.sub('.*<\?xml', '<?xml',
            re.sub('</nf:rpc-reply>.*', '</nf:rpc-reply>',
            re.sub('[\n\r]', '', text)))
        # parse the XML tree
        elements = xml.fromstring(o)
        return elements

    def key_value_xml_parser (self, element):
        if element.text:
            k, v = re.sub('{[^{}]*}', '', element.tag), element.text.strip()
            return self.key_map (k), self._numval (v)

    def key_value_colon_parser (self, line):
        k, v = line.split (':')
        return self.key_map (k), self._numval (v)

    def get_output(self):
        return self.processed_output

    def rerun(self):
        self._run()

    def get_command(self):
        return self.command

    def get_status(self):
        return self.status

    def parse_specific(self):
        pass

    def get_raw_output(self):
        return self.raw_output

    def get_timestamp(self):
        return self.timestamp


