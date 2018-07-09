import numpy
from plugins.SemiF47 import viol_check, PU 

import unittest

class SemiF47PluginTests(unittest.TestCase):

    ## code to check the functionality of viol_check in plugins.SemiF47

    #VRMS values. each data point in the array is 200 sample times long

    values_lvl_5=numpy.random.uniform((0.5-0.05)*PU,
                                      (0.5+0.05)*PU, 13)
    
    values_lvl_7=numpy.random.uniform((0.7-0.05)*PU,
                                      (0.7+0.05)*PU, 41)
    
    values_lvl_8=numpy.random.uniform((0.8-0.05)*PU,
                                      (0.8+0.05)*PU, 59)
    
    values_lvl_5_1=numpy.random.uniform((0.5-0.05)*PU,
                                      (0.5+0.05)*PU, 11)
    
    values_lvl_7_1=numpy.random.uniform((0.7-0.05)*PU,
                                      (0.7+0.05)*PU, 62)
    
    values_other=numpy.random.uniform(105,PU+1.0,20)
    values_other_1=numpy.random.uniform(105,PU+1.0,30)
    
    vol=numpy.concatenate((values_other,values_lvl_8,values_lvl_5_1,
                           values_lvl_7,values_lvl_5,
                           values_other_1,values_lvl_7_1))
    def test_SemiF47_level_0_5(self):
        """
        If the voltage is at 0.5 x PU (PU=120) for >=200 ms then an error
        with time indices of the array 
        """
        self.assertEqual(viol_check(self.vol,5), [[131, 143]])
    
    def test_SemiF47_level_0_7(self):
        """
        If the voltage is at 0.7 x PU (PU=120) for >=500 ms then an error
        with time indices of the array 
        """
        self.assertEqual(viol_check(self.vol,7), [[90, 130], [174, 235]])
        
    def test_SemiF47_level_0_8(self):
                self.assertEqual(viol_check(self.vol,8), [])

