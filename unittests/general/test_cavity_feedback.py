# coding: utf8
# Copyright 2014-2017 CERN. This software is distributed under the
# terms of the GNU General Public Licence version 3 (GPL Version 3), 
# copied verbatim in the file LICENCE.md.
# In applying this licence, CERN does not waive the privileges and immunities 
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
# Project website: http://blond.web.cern.ch/

"""
Unittest for llrf.filters

:Authors: **Helga Timko**
"""

import unittest
import numpy as np
from input_parameters.general_parameters import GeneralParameters
from input_parameters.rf_parameters import RFSectionParameters
from beams.beams import Beam
from beams.distributions import bigaussian
from beams.slices import Slices
from llrf.signal_processing import rf_beam_current, low_pass_filter


class TestBeamCurrent(unittest.TestCase):
    
    def test(self):
        
        # Set up SPS conditions
        GeneralParams = GeneralParameters(1000, 2*np.pi*1100.009, 1/18**2, 
                                          25.92e9)
        RFParams = RFSectionParameters(GeneralParams, 1, 4620, 4.5e6, 0)
        Bunch = Beam(GeneralParams, 1e5, 1e11)
        bigaussian(GeneralParams, RFParams, Bunch, 3.2e-9/4, seed = 1234, 
                   reinsertion = True) 
        Profile = Slices(RFParams, Bunch, 100, cut_left=-1.e-9, cut_right=6.e-9)
        Profile.track()
        self.assertEqual(len(Bunch.dt), np.sum(Profile.n_macroparticles), "In" +
            " TestBeamCurrent: particle number mismatch in Beam vs Slices")
        
        # RF current calculation
        rf_current = rf_beam_current(Profile, 2*np.pi*200.222e6, 
                                     GeneralParams.t_rev[0])
        Iref_real = np.array([  0.0000000000e+00,   0.0000000000e+00,   
            0.0000000000e+00,
            0.0000000000e+00,   9.0438676025e-09,   9.9359978093e-09,
            5.3755622803e-09,   1.1482930667e-08,   6.0628723354e-09,
            0.0000000000e+00,   2.6250395127e-08,   2.0211136119e-08,
            6.8592802201e-09,   1.3856712019e-08,   0.0000000000e+00,
            0.0000000000e+00,   8.8573644421e-08,   1.0669769855e-07,
            1.4238782165e-07,   2.3034654366e-07,   2.9653714394e-07,
            4.6955500653e-07,   6.7155032677e-07,   7.6501561884e-07,
            1.0194783598e-06,   9.8297902177e-07,   1.0560564716e-06,
            1.1632312435e-06,   1.1131740675e-06,   9.3810433402e-07,
            7.3997350098e-07,   3.4125471892e-07,  -2.3625407839e-07,
           -9.9799354925e-07,  -1.9785197154e-06,  -3.2132605419e-06,
           -4.5198169248e-06,  -6.0172433574e-06,  -8.0659811627e-06,
           -9.8890551549e-06,  -1.2093384500e-05,  -1.4013140843e-05,
           -1.6211970354e-05,  -1.7804697439e-05,  -2.0319459333e-05,
           -2.2481908936e-05,  -2.3008637792e-05,  -2.3501688342e-05,
           -2.5084710761e-05,  -2.5550379522e-05,  -2.5389912452e-05,
           -2.4049934156e-05,  -2.3891673889e-05,  -2.3592196203e-05,
           -2.1367228944e-05,  -1.9760379598e-05,  -1.7893780886e-05,
           -1.5911056037e-05,  -1.4029166736e-05,  -1.1495063984e-05,
           -9.5441211884e-06,  -7.8300813209e-06,  -6.0007932150e-06,
           -4.3829937907e-06,  -3.1519904370e-06,  -1.9260764179e-06,
           -9.2976214265e-07,  -1.9190881444e-07,   3.8801368283e-07,
            7.5507257533e-07,   9.7572255591e-07,   1.2189501463e-06,
            1.1428957328e-06,   1.0796967577e-06,   1.0474575162e-06,
            9.0639007504e-07,   6.7910687034e-07,   5.2901279375e-07,
            4.6072091928e-07,   2.9779008559e-07,   2.1864144681e-07,
            1.6872913505e-07,   8.6865633885e-08,   5.4580613043e-08,
            4.1461840900e-08,   0.0000000000e+00,   2.0774516390e-08,
            6.8515279683e-09,   2.6900472647e-08,   2.6186356186e-08,
            1.2634648428e-08,   1.8117301361e-08,   1.1428147971e-08,
            1.0689527495e-08,   0.0000000000e+00,   4.4850615158e-09,
            4.0013321686e-09,   3.4865927095e-09,   0.0000000000e+00,
            2.3802496803e-09])
        I_real = np.around(rf_current.real, 9) # round
        Iref_real = np.around(Iref_real, 9) 
        self.assertSequenceEqual(I_real.tolist(), Iref_real.tolist(),
            msg="In TestBeamCurrent, mismatch in real part of RF current")
        
        Iref_imag = np.array([ -2.3960929877e-05,  -2.3082578447e-05,  
            -2.2025338258e-05,
            -2.0797402868e-05,  -1.9408285846e-05,  -1.7868758707e-05,
            -1.6190751428e-05,  -1.4387263116e-05,  -1.2472277450e-05,
            -1.0460631089e-05,  -8.3679099957e-06,  -6.2103458198e-06,
            -4.0046508147e-06,  -1.7679179505e-06,   4.8251581211e-07,
             2.7292103636e-06,   4.9547227971e-06,   7.1418304869e-06,
             9.2735272855e-06,   1.1333044858e-05,   1.3304479582e-05,
             1.5170727836e-05,   1.6915653858e-05,   1.8528718353e-05,
             1.9981525287e-05,   2.1291925054e-05,   2.2414717190e-05,
             2.3325878934e-05,   2.4045895651e-05,   2.4570558708e-05,
             2.4782849873e-05,   2.4765381506e-05,   2.4547043000e-05,
             2.4026068813e-05,   2.3214576703e-05,   2.2086707170e-05,
             2.0913440699e-05,   1.9493835027e-05,   1.7438434134e-05,
             1.5657598682e-05,   1.3455322897e-05,   1.1555158217e-05,
             9.3567110314e-06,   7.7558695840e-06,   5.2461314550e-06,
             3.0065070683e-06,   2.5481342737e-06,   1.8593221864e-06,
             4.8210185525e-07,   0.0000000000e+00,  -1.3258257791e-07,
            -1.0874989235e-06,  -1.6230320864e-06,  -1.9279552737e-06,
            -4.1888161878e-06,  -5.8068941005e-06,  -7.6767968300e-06,
            -9.6601267108e-06,  -1.1529836597e-05,  -1.4075453546e-05,
            -1.6016064557e-05,  -1.7685722456e-05,  -1.9483957490e-05,
            -2.1050502455e-05,  -2.2114381185e-05,  -2.3223746540e-05,
            -2.4078614299e-05,  -2.4492879271e-05,  -2.4741314179e-05,
            -2.4785471471e-05,  -2.4523050236e-05,  -2.3954536897e-05,
            -2.3265283854e-05,  -2.2328145741e-05,  -2.1187621134e-05,
            -1.9879483509e-05,  -1.8409491149e-05,  -1.6785633119e-05,
            -1.5027034588e-05,  -1.3151872752e-05,  -1.1172968079e-05,
            -9.1070393600e-06,  -6.9704356659e-06,  -4.7796596785e-06,
            -2.5518172242e-06,  -3.0419378995e-07,   1.9457898723e-06,
             4.1806948988e-06,   6.3831956564e-06,   8.5362292994e-06,
             1.0623112320e-05,   1.2627660677e-05,   1.4534349974e-05,
             1.6328396501e-05,   1.7995901478e-05,   1.9523936044e-05,
             2.0900661805e-05,   2.2115408548e-05,   2.3158762902e-05,
             2.4022636372e-05])
        I_imag = np.around(rf_current.imag, 9) # round
        Iref_imag = np.around(Iref_imag, 9)
        self.assertSequenceEqual(I_imag.tolist(), Iref_imag.tolist(),
            msg="In TestBeamCurrent, mismatch in imaginary part of RF current")
        
        
        # Apply a low-pass filter on the current
        filtered_1 = low_pass_filter(rf_current.real, 20.e6)
        filtered_2 = low_pass_filter(rf_current.imag, 20.e6)
        ref_filt1 = np.array([ -9.4646042539e-12,  -7.9596801534e-10,
            -2.6993572787e-10,
             2.3790828610e-09,   6.4007063190e-09,   9.5444302650e-09,
             9.6957462918e-09,   6.9944771120e-09,   5.0040512366e-09,
             8.2427583408e-09,   1.6487066238e-08,   2.2178930587e-08,
             1.6497620890e-08,   1.9878201568e-09,  -2.4862807497e-09,
             2.0862096916e-08,   6.6115473293e-08,   1.1218114710e-07,
             1.5428441607e-07,   2.1264254596e-07,   3.1213935713e-07,
             4.6339212948e-07,   6.5039440158e-07,   8.2602190806e-07,
             9.4532001396e-07,   1.0161170159e-06,   1.0795840334e-06,
             1.1306004256e-06,   1.1081141333e-06,   9.7040873320e-07,
             7.1863437325e-07,   3.3833950889e-07,  -2.2273124358e-07,
            -1.0035204008e-06,  -1.9962696992e-06,  -3.1751183137e-06,
            -4.5326227784e-06,  -6.0940850385e-06,  -7.9138578879e-06,
            -9.9867317826e-06,  -1.2114906338e-05,  -1.4055138779e-05,
            -1.5925650405e-05,  -1.8096693885e-05,  -2.0418813156e-05,
            -2.2142865862e-05,  -2.3038234657e-05,  -2.3822481250e-05,
            -2.4891969829e-05,  -2.5543384520e-05,  -2.5196086909e-05,
            -2.4415522211e-05,  -2.3869116251e-05,  -2.3182951665e-05,
            -2.1723128723e-05,  -1.9724625363e-05,  -1.7805112266e-05,
            -1.5981218737e-05,  -1.3906226012e-05,  -1.1635865568e-05,
            -9.5381189596e-06,  -7.7236624815e-06,  -6.0416822483e-06,
            -4.4575806261e-06,  -3.0779237834e-06,  -1.9274519396e-06,
            -9.5699993457e-07,  -1.7840768971e-07,   3.7780452612e-07,
             7.5625231388e-07,   1.0158886027e-06,   1.1538975409e-06,
             1.1677937652e-06,   1.1105424636e-06,   1.0216131672e-06,
             8.8605026541e-07,   7.0783694846e-07,   5.4147914020e-07,
             4.1956457226e-07,   3.2130062098e-07,   2.2762751268e-07,
             1.4923020411e-07,   9.5683463322e-08,   5.8942895620e-08,
             3.0515695233e-08,   1.2444834300e-08,   8.9413517889e-09,
             1.6154761941e-08,   2.3261993674e-08,   2.3057968490e-08,
             1.8354179928e-08,   1.4938991667e-08,   1.2506841004e-08,
             8.1230022648e-09,   3.7428821201e-09,   2.8368110506e-09,
             3.6536247240e-09,   2.8429736524e-09,   1.6640835314e-09,
             2.3960087967e-09])
        filt1 = np.around(filtered_1, 9) # round
        ref_filt1 = np.around(ref_filt1, 9) 
        self.assertSequenceEqual(filt1.tolist(), ref_filt1.tolist(),
            msg="In TestBeamCurrent, mismatch in real part of filtered" +
            " current")
        ref_filt2 = np.array([ -2.3961144862e-05,  -2.3068407495e-05,  
            -2.2032568730e-05,
            -2.0802458598e-05,  -1.9404207722e-05,  -1.7866343620e-05,
            -1.6192939401e-05,  -1.4388516250e-05,  -1.2471102058e-05,
            -1.0459964180e-05,  -8.3685646433e-06,  -6.2107099849e-06,
            -4.0042450035e-06,  -1.7676996231e-06,   4.8218744608e-07,
             2.7290419327e-06,   4.9551219666e-06,   7.1420058616e-06,
             9.2728887439e-06,   1.1332859672e-05,   1.3305420952e-05,
             1.5171248711e-05,   1.6914336182e-05,   1.8525140588e-05,
             1.9990629510e-05,   2.1288892657e-05,   2.2404376728e-05,
             2.3333676470e-05,   2.4060094164e-05,   2.4547733183e-05,
             2.4783020998e-05,   2.4784143135e-05,   2.4543470924e-05,
             2.4015588683e-05,   2.3195086592e-05,   2.2142265138e-05,
             2.0894179164e-05,   1.9403605847e-05,   1.7604999364e-05,
             1.5547279411e-05,   1.3450755357e-05,   1.1514926892e-05,
             9.6155586912e-06,   7.4602176979e-06,   5.1882582741e-06,
             3.3959529160e-06,   2.3390150679e-06,   1.6107373489e-06,
             8.1970725869e-07,   4.9574017721e-08,  -5.0107215472e-07,
            -8.8678653087e-07,  -1.3888059170e-06,  -2.3581144073e-06,
            -3.9324581897e-06,  -5.8357304826e-06,  -7.7131994109e-06,
            -9.5914420238e-06,  -1.1688033367e-05,  -1.3925285523e-05,
            -1.6001824767e-05,  -1.7809857958e-05,  -1.9449209937e-05,
            -2.0944801711e-05,  -2.2217459434e-05,  -2.3234358261e-05,
            -2.4006442153e-05,  -2.4521569102e-05,  -2.4770210047e-05,
            -2.4763227399e-05,  -2.4502155576e-05,  -2.3989667325e-05,
            -2.3253205954e-05,  -2.2319555159e-05,  -2.1193939853e-05,
            -1.9882490857e-05,  -1.8406104238e-05,  -1.6784533423e-05,
            -1.5028913419e-05,  -1.3152066696e-05,  -1.1172221789e-05,
            -9.1068513261e-06,  -6.9708276191e-06,  -4.7798498172e-06,
            -2.5515575522e-06,  -3.0395993303e-07,   1.9455614191e-06,
             4.1803191674e-06,   6.3834898780e-06,   8.5369039702e-06,
             1.0622627615e-05,   1.2626405366e-05,   1.4535230436e-05,
             1.6330762083e-05,   1.7994201124e-05,   1.9519512997e-05,
             2.0904357024e-05,   2.2123296300e-05,   2.3147162195e-05,
             2.4021639034e-05])
        filt2 = np.around(filtered_2, 9) # round
        ref_filt2 = np.around(ref_filt2, 9) 
        self.assertSequenceEqual(filt2.tolist(), ref_filt2.tolist(),
            msg="In TestBeamCurrent, mismatch in imaginary part of filtered" +
            " current")


       
if __name__ == '__main__':

    unittest.main()


