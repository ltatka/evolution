import unittest
import analyzeReactions as ar

class UnitTest(unittest.TestCase):

    astr = '''
            var S0
            var S1
            var S2
            S0 + S0 -> S0; k0*S0*S0
            S0 -> S0+S1; k1*S0
            S2 + S0 -> S0; k2*S2*S0
            S1 -> S1+S1; k3*S1
            S1 + S1 -> S0; k4*S1*S1
            S0 + S1 -> S2; k5*S0*S1
            S1 -> S1+S0; k6*S1
            S0 + S1 -> S0; k7*S0*S1
            S2 -> S0; k8*S2
            S1 + S2 -> S1 + S1; k8*S1*S2
            k0 = 26.53735636809662
            k1 = 13.333731542907184
            k2 = 6.824197307764301
            k3 = 31.100427948616264
            k4 = 44.91681625994146
            k5 = 35.73589162966594
            k6 = 13.403172496587345
            k7 = 48.14543815511555
            k8 = 47.30926137960468
            S0 = 1.0
            S1 = 5.0
            S2 = 9.0'''

    def test_countReactions(self):
        rxnDict = ar.countReactions(self.astr)
        self.assertEqual(rxnDict['total'], 10)
        self.assertEqual(rxnDict['uni-uni'], 1 / rxnDict['total'])
        self.assertEqual(rxnDict['uni-bi'], 3 / rxnDict['total'])
        self.assertEqual(rxnDict['bi-uni'], 5 / rxnDict['total'])
        self.assertEqual(rxnDict['bi-bi'], 1 / rxnDict['total'])
        self.assertEqual(rxnDict['autocatalysis'], 4 / rxnDict['total'])
        self.assertEqual(rxnDict['degradation'], 3 / rxnDict['total'])


