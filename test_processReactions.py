import unittest
import postprocessReactions as pp

class UnitTests(unittest.TestCase):

    ant = '''var S0
var S1
var S2
S2 -> S0; k0*S2
S0 -> S1+S0; k1*S0
S1 -> S0+S1; k2*S1
S1 -> S0+S2; k3*S1
S2 -> S0; k4*S2
S2 + S1 -> S2; k5*S2*S1
S0 -> S1+S0; k6*S0
S2 -> S1+S1; k7*S2
S2 -> S2+S2; k8*S2
S1 -> S0; k9*S1
S2 + S0 -> S1 + S2; k10*S2*S0
S1 + S1 -> S0 + S1; k11*S1*S1
S0 -> S0+S1; k12*S0
k0 = 7.314829248542936
k1 = 35.95227823979854
k2 = 41.54190920864631
k3 = 4.7667514994980555
k4 = 11.830987147018757
k5 = 15.50936673547638
k6 = 5.400180372157445
k7 = 8.171034267002623
k8 = 15.252690388653708
k9 = 7.202857436875558
k10 = 13.147047088765943
k11 = 7.20304738000393
k12 = 48.71489357141781
S0 = 1.0
S1 = 5.0
S2 = 9.0'''

    model = pp.AntimonyModel(ant)

    def test_init(self):
        trueReactions = ['S2 -> S0; k0*S2',
                         'S0 -> S1+S0; k1*S0',
                         'S1 -> S0+S1; k2*S1',
                         'S1 -> S0+S2; k3*S1',
                         'S2 -> S0; k4*S2',
                         'S2 + S1 -> S2; k5*S2*S1',
                         'S0 -> S1+S0; k6*S0',
                         'S2 -> S1+S1; k7*S2',
                         'S2 -> S2+S2; k8*S2',
                         'S1 -> S0; k9*S1',
                         'S2 + S0 -> S1 + S2; k10*S2*S0',
                         'S1 + S1 -> S0 + S1; k11*S1*S1',
                         'S0 -> S0+S1; k12*S0']
        trueRateConstants = ['k0 = 7.314829248542936',
                             'k1 = 35.95227823979854',
                             'k2 = 41.54190920864631',
                             'k3 = 4.7667514994980555',
                             'k4 = 11.830987147018757',
                             'k5 = 15.50936673547638',
                             'k6 = 5.400180372157445',
                             'k7 = 8.171034267002623',
                             'k8 = 15.252690388653708',
                             'k9 = 7.202857436875558',
                             'k10 = 13.147047088765943',
                             'k11 = 7.20304738000393',
                             'k12 = 48.71489357141781']
        self.assertEqual(self.model.reactions, trueReactions)
        self.assertEqual(self.model.rateConstants, trueRateConstants)
        self.assertTrue(len(self.model.reactions) == len(self.model.rateConstants))

    def test_makeRxnSet(self):
        trueDict= {(frozenset({'S2'}), frozenset({'S0'})): 19.145816395561692,
                    (frozenset({'S0'}), frozenset({'S0', 'S1'})): 90.0673521833738,
                    (frozenset({'S1'}), frozenset({'S0', 'S1'})): 48.74495658865024,
                    (frozenset({'S1'}), frozenset({'S0', 'S2'})): 4.7667514994980555,
                    (frozenset({'S2', 'S1'}), frozenset({'S2'})): 15.50936673547638,
                    (frozenset({'S2'}), frozenset({'S1'})): 8.171034267002623,
                    (frozenset({'S1'}), frozenset({'S0'})): 7.202857436875558,
                    (frozenset({'S0', 'S2'}), frozenset({'S2', 'S1'})): 13.147047088765943}
        trueCombinedRxns = ['S2->S0;k4*S2',
                             'S0->S1+S0;k6*S0',
                             'S1+S1->S0+S1;k11*S1*S1',
                             'S0->S0+S1;k12*S0']
        rxnDict = self.model.makeRxnDict()
        self.assertEqual(rxnDict, trueDict)
        self.assertEqual(self.model.combinedReactions, trueCombinedRxns)