import syslog
import sys
import pprint
import socket
from Insieme.Logger import as Logger 

def sampleDevice_logger( f ):
    def wrapper( *args ):
        Logger.log(Logger.INFO,"%s%s" % (f.__name__, args)) 
        f( *args )
    return wrapper

#
# Infra API
#
@sampleDevice_logger
def deviceValidate( device, version ):
    pass

@sampleDevice_logger
def deviceModify( device, interfaces, configuration):
    pass 

@sampleDevice_logger
def deviceAudit( device, interfaces, configuration ):
    pass

@sampleDevice_logger
def deviceHealth( device ):
    pass 

@sampleDevice_logger
def clusterModify( device, configuration ):
    pass

@sampleDevice_logger
def clusterAudit( device, configuration ):
    pass

#
# FunctionGroup API
#
@sampleDevice_logger
def serviceModify( device,
                   configuration ):
    ''' 
    (0, '', 4447): {
          'state': 1,                                                                                                                    
          'transaction': 10000,                                                                                                          
          'value': {
              (1, '', 4384): {
                  'state': 1,                                                                                          
                  'transaction': 10000,                                                                                
                  'value': {
                       (3, 'SLB', 'Node2'): {
                              'state': 1,                                                          
                              'transaction': 10000,                                                
                              'value': {
                                   (2, '', 'inside'): {
                                       'state': 1,                            
                                       'transaction': 10000,                  
                                       'value': {
                                            (9, '', 'ADCCluster1_inside_7697'): {
                                                 'state': 2,                          
                                                 'target': 'ADCCluster1_inside_7697',                                                 
                                                 'transaction': 10000
                                             }
                                        }
                                    },                                                                                                                  
                                    (2, '', 'outside'): {
                                        'state': 1,                           
                                        'transaction': 10000,                 
                                        'value': {
                                            (9, '', 'ADCCluster1_outside_4625'): {
                                                'state': 2,                                             
                                                'target': 'ADCCluster1_outside_4625',                                           
                                                'transaction': 10000
                                            }
                                         }
                                    },                                                                                                              
                                    (4, 'VServer', 'VServer'): {
                                          'connector': '',              
                                          'state': 1,                    
                                          'transaction': 10000,          
                                          'value': {
                                             (5, 'port', 'port'): {
                                                  'connector': '',                                             
                                                  'state': 1,
                                                  'transaction': 10000,                                                    
                                                  'value': '800000'
                                              }
                                           }
                                    }
                               }
                         }
                     }
                 },                                                                                                                          
                (4, 'Network', 'Network'): {
                      'connector': u'',                                                                        
                      'state': 1,                                                                              
                      'transaction': 10000,                                                                    
                      'value': {
                          (4, 'subnetip', 'subnetip'): {
                            'connector': '',                                
                            'state': 1,                                      
                            'transaction': 10000,                            
                            'value': {
                                (5, 'subnetipaddress', 'subnetipaddress'): {
                                    'connector': '',                                                                                                     
                                    'state': 1,                                                                                                         
                                    'transaction': 10000,                                                                                              
                                    'value': ''
                                 }
                              }
                           },                                                                               
                       }
                  }
             }
        }
    # 
    # Example of returning multiple faults 
    #
    (1) The parameter value for subnetipaddress is invalid. Script can raise a fault on this param

    subnetipaddressInstance = [(0, '', 4447), (4, 'Network', 'Network'), (4, 'subnetip', 'subnetip'), (5, 'subnetipaddress', 'subnetipaddress')]
    subnetipaddressFault = "Invalid subnet IP address"
   
    (2) The VServer folder under SLB has invalid port number 

    slbPortInstance = [(0, '', 4447), (1, '', 4384), (3, 'SLB', 'Node2'), (4, 'VServer', 'VServer'), (5, 'port', 'port')]
    slbPortFault = "Invalid SLB Vserver Port value - Acceptable range 1 - 65535"

    #
    # Example of reporting Servicehealth along with ServiceModify
    #
    slbInstance =[(0, '', 4447), (1, '', 4384), (3, 'SLB', 'Node2')]
    slbInstanceHealth = 0

    returnValue =  { 
        'status': True, 
        'faults': [
                    (subnetipaddressInstance, subnetipaddressFault), 
                    (slbPortIntance, slbPortFault)
                  ],
        'health': [
                    (slbInstance, slbInstanceHealth),
                  ] 
    }
    return returnValue 

    '''
    pass

def serviceAudit( device,
                  configuration ):
    pass

#
# EndPoint/Network API
#
@sampleDevice_logger
def attachEndpoint( device,
                    configuration,
                    connector,
                    ep ):
    pass
 
@sampleDevice_logger
def detachEndpoint( device,
                    configuration,
                    connector,
                    ep ):
    pass

@sampleDevice_logger
def attachNetwork( device,
                   connectivity,
                   configuration,
                   connector,
                   nw ):
    pass

@sampleDevice_logger
def detachNetwork( device,
                   connectivity,
                   configuration,
                   connector,
                   nw ):
    pass

@sampleDevice_logger
def serviceHealth( device,
                   name,
                   connectivity,
                   configuration ):
    pass

@sampleDevice_logger
def serviceCounters( device,
                     name,
                     connectivity,
                     configuration,
                     connector ):
    pass


