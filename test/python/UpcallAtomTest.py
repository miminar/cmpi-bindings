#!/usr/bin/env python

import pywbem
from lib import wbem_connection
import unittest
import optparse
import os
import time
from socket import getfqdn

conn = None

#This test requires the usage of elementtree

_g_opts = None
_g_args = None

################################################################################
class UpcallAtomTest(unittest.TestCase):

    global conn



    # start indication support methods
    def _createFilter(self,
                      ch, query='select * from CIM_ProcessIndication',
                      ns='root/interop',
                      querylang='WQL',
                      src_ns='root/cimv2',
                      in_name=None):
        name = in_name or 'cimfilter%s'%time.time()
        filterinst=pywbem.CIMInstance('CIM_IndicationFilter')
        filterinst['CreationClassName']='CIM_IndicationFilter'
        filterinst['SystemCreationClassName']='CIM_ComputerSystem'
        filterinst['SystemName']=getfqdn()
        filterinst['Name']=name
        filterinst['Query']=query
        filterinst['QueryLanguage']=querylang
        filterinst['SourceNamespace']=src_ns
        cop = pywbem.CIMInstanceName('CIM_IndicationFilter')
        cop.keybindings = { 'CreationClassName':'CIM_IndicationFilter',
                            'SystemClassName':'CIM_ComputerSystem',
                            'SystemName':getfqdn(),
                            'Name':name }
        cop.namespace=ns
        filterinst.path = cop
        filtercop = ch.CreateInstance(filterinst)
        return filtercop

    def _createDest(self,
                    ch, destination='http://localhost:5988',
                    ns='root/interop',
                    in_name=None):
        name = in_name or 'cimlistener%s'%time.time()
        destinst=pywbem.CIMInstance('CIM_ListenerDestinationCIMXML')
        destinst['CreationClassName']='CIM_ListenerDestinationCIMXML'
        destinst['SystemCreationClassName']='CIM_ComputerSystem'
        destinst['SystemName']=getfqdn()
        destinst['Name']=name
        destinst['Destination']=destination
        cop = pywbem.CIMInstanceName('CIM_ListenerDestinationCIMXML')
        cop.keybindings = { 'CreationClassName':'CIM_ListenerDestinationCIMXML',
                            'SystemClassName':'CIM_ComputerSystem',
                            'SystemName':getfqdn(),
                            'Name':name }
        cop.namespace=ns
        destinst.path = cop
        destcop = ch.CreateInstance(destinst)
        return destcop

    def _createSubscription(self, ch, ns='root/interop'):
        replace_ns = ch.default_namespace
        ch.default_namespace=ns
        indfilter=self._createFilter(ch)
        indhandler=self._createDest(ch)
        subinst=pywbem.CIMInstance('CIM_IndicationSubscription')
        subinst['Filter']=indfilter
        subinst['Handler']=indhandler
        cop = pywbem.CIMInstanceName('CIM_IndicationSubscription')
        cop.keybindings = { 'Filter':indfilter,
                            'Handler':indhandler }
        cop.namespace=ns
        subinst.path = cop
        subcop = ch.CreateInstance(subinst)
        ch.default_namespace=replace_ns
        return subcop


    def _deleteSubscription(self, ch, subcop):
        indfilter = subcop['Filter']
        indhandler= subcop['Handler']
        ch.DeleteInstance(subcop)
        ch.DeleteInstance(indfilter)
        ch.DeleteInstance(indhandler)

    # end indication support methods



    def setUp(self):
        unittest.TestCase.setUp(self)
        self.conn = conn
        self.conn.debug = True
        self._verbose = _g_opts.verbose
        self._dbgPrint()


    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def _dbgPrint(self, msg=''):
        if self._verbose:
            if len(msg):
                print('\t -- %s --' % msg)
            else:
                print('')
        
    def test_a_upcalls_all(self):
        rv,outs = self.conn.InvokeMethod('test_all_upcalls', 'Test_UpcallAtom')
        self.assertEquals(rv, 'Success!')
        self.assertFalse(outs)

    def test_b_indications(self):
        numrcv = 0
        self.subcop = self._createSubscription(self.conn)
        num_to_send = pywbem.Uint16(7)
        self.conn.InvokeMethod('reset_indication_count', 'Test_UpcallAtom')
        countsent,outs = self.conn.InvokeMethod('send_indications', 'Test_UpcallAtom', num_to_send=num_to_send)
        numsent,outs = self.conn.InvokeMethod('get_indication_send_count', 'Test_UpcallAtom')
        self._deleteSubscription(self.conn, self.subcop)
        if (countsent != numsent):
            self.fail("send_indications NumSent(%d) doesn't match get_indication_send_count NumSent(%d)"%(countsent, numsent));
        if (numrcv != numsent):
            self.fail("number received(%d) doesn't match number sent(%d)"%(numrcv,numsent));


def get_unit_test():
    return UpcallAtomTest


if __name__ == '__main__':
    parser = optparse.OptionParser()
    wbem_connection.getWBEMConnParserOptions(parser)
    parser.add_option('--verbose', '', action='store_true', default=False,
            help='Show verbose output')
    parser.add_option('--op', '', action='store_true', default=False,
            help='Use OpenPegasus UDS Connection')
    parser.add_option('--level',
            '-l',
            action='store',
            type='int',
            dest='dbglevel',
            help='Indicate the level of debugging statements to display (default=2)',
            default=2)
    _g_opts, _g_args = parser.parse_args()
    
    if _g_opts.op:
        conn = pywbem.PegasusUDSConnection()
    else:
        conn = wbem_connection.WBEMConnFromOptions(parser)
    
    suite = unittest.makeSuite(UpcallAtomTest)
    unittest.TextTestRunner(verbosity=_g_opts.dbglevel).run(suite)

