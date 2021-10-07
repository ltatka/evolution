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

    def test_isEqual(self):
        r1 = pp.Reaction(['S0', 'S1'], ['S2'], 1.4)
        r2 = pp.Reaction(['S1', 'S0'], ['S2'], 2.5)
        self.assertTrue(r1.isEqual(r2))
        r3 = pp.Reaction(['S1', 'S1'], ['S3'], 2.6)
        r4 = pp.Reaction(['S1', 'S1'], ['S5'], 1.9)
        self.assertFalse(r3.isEqual(r4))
        r5 = pp.Reaction(['S1', 'S3'], ['S2', 'S4'], 2.6)
        r6 = pp.Reaction(['S3', 'S1'], ['S4', 'S2'], 2.6)
        self.assertTrue(r5.isEqual(r6))

    def test_makeRxnSet(self):
        trueDict = {'S2 -> S0': 11.830987147018757,
                    'S0 -> S1 + S0': 5.400180372157445,
                    'S1 -> S0 + S1': 41.54190920864631,
                    'S1 -> S0 + S2': 4.7667514994980555,
                    'S2 + S1 -> S2': 15.50936673547638,
                    'S2 -> S1 + S1': 8.171034267002623,
                    'S2 -> S2 + S2': 15.252690388653708,
                    'S1 -> S0': 7.202857436875558,
                    'S2 + S0 -> S1 + S2': 13.147047088765943,
                    'S1 + S1 -> S0 + S1': 7.20304738000393,
                    'S0 -> S0 + S1': 48.71489357141781}
        trueCombinedRxns = ['S2->S0;k4*S2',
                             'S0->S1+S0;k6*S0',
                             'S1+S1->S0+S1;k11*S1*S1',
                             'S0->S0+S1;k12*S0']
        self.model.makeRxnDict()
        readDict = self.model.getReadableRxnDict()
        self.assertEqual(readDict, trueDict)
        self.assertEqual(self.model.combinedReactions, trueCombinedRxns)

    # def test_processRxnDict(self):
    #     trueReactions = ['S2->S0; k0*S2',
    #                      'S0->S1+S0; k1*S0',
    #                      'S1->S1+S0; k2*S1',
    #                      'S1->S2+S0; k3*S1',
    #                      'S1+S2->S2; k4*S1*S2',
    #                      'S2->S1; k5*S2',
    #                      'S1->S0; k6*S1',
    #                      'S2+S0->S1+S2; k7*S2*S0']
    #     reactions, rateconstants = self.model.processRxnDict()
    #     self.assertEqual(reactions, [])