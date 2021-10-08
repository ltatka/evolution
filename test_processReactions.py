import unittest
import postprocessReactions as pp
from damped_analysis import isModelDampled

class UnitTests(unittest.TestCase):
    ant = ('var S0\n'
           'var S1\n'
           'var S2\n'
           'S2 -> S0; k0*S2\n'
           'S0 -> S1+S0; k1*S0\n'
           'S1 -> S0+S1; k2*S1\n'
           'S1 -> S0+S2; k3*S1\n'
           'S2 -> S0; k4*S2\n'
           'S2 + S1 -> S2; k5*S2*S1\n'
           'S0 -> S1+S0; k6*S0\n'
           'S2 -> S1+S1; k7*S2\n'
           'S2 -> S2+S2; k8*S2\n'
           'S1 -> S0; k9*S1\n'
           'S2 + S0 -> S1 + S2; k10*S2*S0\n'
           'S1 + S1 -> S0 + S1; k11*S1*S1\n'
           'S0 -> S0+S1; k12*S0\n'
           'k0 = 7.314829248542936\n'
           'k1 = 35.95227823979854\n'
           'k2 = 41.54190920864631\n'
           'k3 = 4.7667514994980555\n'
           'k4 = 11.830987147018757\n'
           'k5 = 15.50936673547638\n'
           'k6 = 5.400180372157445\n'
           'k7 = 8.171034267002623\n'
           'k8 = 15.252690388653708\n'
           'k9 = 7.202857436875558\n'
           'k10 = 13.147047088765943\n'
           'k11 = 7.20304738000393\n'
           'k12 = 48.71489357141781\n'
           'S0 = 1.0\n'
           'S1 = 5.0\n'
           'S2 = 9.0')

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

    def test_parseReactionString(self):
        r = 'S2 + S0 -> S1 + S2; k10*S2*S0'
        re, pr = self.model.parseReactionString(r)
        self.assertListEqual(re, ['S2', 'S0'])
        self.assertListEqual(pr, ['S1', 'S2'])
        r2 = 'S2 -> S2+S2; k8*S2'
        re2, pr2 = self.model.parseReactionString(r2)
        self.assertListEqual(re2, ['S2'])
        self.assertListEqual(pr2, ['S2', 'S2'])

    def test_rxnIsEqual(self):
        r1 = 'S0 -> S0+S1; k12*S0'
        r2 = 'S0 -> S1+S0; k1*S0'
        self.assertTrue(self.model.rxnIsEqual(r1, r2))
        r3 = 'S1 + S1 -> S0 + S1; k11*S1*S1'
        r4 = 'S1 -> S0 + S1; k11*S1*S1'
        self.assertFalse(self.model.rxnIsEqual(r3, r4))

    def test_reactantEqualsProduct(self):
        r = 'S1 + S2 -> S2 + S1; k12*S1*S2'
        self.assertTrue(self.model.reactantEqualsProduct(r))

    def test_rxnDictContains(self):
        testModel = pp.AntimonyModel('')
        testModel.rxnDict = {'S0 -> S1+S0': 1}
        rxn = 'S0 -> S0+S1; k12*S0'
        contains, key = testModel.rxnDictContains(rxn)
        self.assertTrue(contains)
        self.assertEqual('S0 -> S1+S0', key)

    def test_makeRxnSet(self):
        trueDict = {'S2 -> S0': 19.145816395561692,
                    'S0 -> S1+S0': 90.0673521833738,
                    'S1 -> S0+S1': 41.54190920864631,
                    'S1 -> S0+S2': 4.7667514994980555,
                    'S2 + S1 -> S2': 15.50936673547638,
                    'S2 -> S1+S1': 8.171034267002623,
                    'S2 -> S2+S2': 15.252690388653708,
                    'S1 -> S0': 7.202857436875558,
                    'S2 + S0 -> S1 + S2': 13.147047088765943,
                    'S1 + S1 -> S0 + S1': 7.20304738000393}

        trueCombinedRxns = ['S2 -> S0',
                            'S0 -> S1+S0',
                            'S0 -> S0+S1']
        self.model.makeRxnDict()
        self.assertEqual(self.model.rxnDict, trueDict)
        self.assertEqual(self.model.combinedReactions, trueCombinedRxns)

    def test_processRxnDict(self):
        trueReactionList = ['S2 -> S0; k0*S2',
                             'S0 -> S1+S0; k1*S0',
                             'S1 -> S0+S1; k2*S1',
                             'S1 -> S0+S2; k3*S1',
                             'S2 + S1 -> S2; k4*S2*S1',
                             'S2 -> S1+S1; k5*S2',
                             'S2 -> S2+S2; k6*S2',
                             'S1 -> S0; k7*S1',
                             'S2 + S0 -> S1 + S2; k8*S2*S0',
                             'S1 + S1 -> S0 + S1; k9*S1*S1']
        trueRateConstants = ['k0 = 19.145816395561692',
                             'k1 = 90.0673521833738',
                             'k2 = 41.54190920864631',
                             'k3 = 4.7667514994980555',
                             'k4 = 15.50936673547638',
                             'k5 = 8.171034267002623',
                             'k6 = 15.252690388653708',
                             'k7 = 7.202857436875558',
                             'k8 = 13.147047088765943',
                             'k9 = 7.20304738000393']
        reactionList, rateConstantList = self.model.processRxnDict()
        self.assertListEqual(reactionList, trueReactionList)
        self.assertListEqual(rateConstantList, trueRateConstants)

    def test_reafactorModel(self):
        trueAnstr = ('var S0\n'
                     'var S1\n'
                     'var S2\n'
                     'S2 -> S0; k0*S2\n'
                     'S0 -> S1+S0; k1*S0\n'
                     'S1 -> S0+S1; k2*S1\n'
                     'S1 -> S0+S2; k3*S1\n'
                     'S2 + S1 -> S2; k4*S2*S1\n'
                     'S2 -> S1+S1; k5*S2\n'
                     'S2 -> S2+S2; k6*S2\n'
                     'S1 -> S0; k7*S1\n'
                     'S2 + S0 -> S1 + S2; k8*S2*S0\n'
                     'S1 + S1 -> S0 + S1; k9*S1*S1\n'
                     'k0 = 19.145816395561692\n'
                     'k1 = 90.0673521833738\n'
                     'k2 = 41.54190920864631\n'
                     'k3 = 4.7667514994980555\n'
                     'k4 = 15.50936673547638\n'
                     'k5 = 8.171034267002623\n'
                     'k6 = 15.252690388653708\n'
                     'k7 = 7.202857436875558\n'
                     'k8 = 13.147047088765943\n'
                     'k9 = 7.20304738000393\n'
                     'S0 = 1.0\n'
                     'S1 = 5.0\n'
                     'S2 = 9.0')
        anstr = self.model.refactorModel()
        self.assertEqual(anstr, trueAnstr)

    def test_removeDuplicateRxns(self):
        trueAnstr = ('var S0\n'
                     'var S1\n'
                     'var S2\n'
                     'S2 -> S0; k0*S2\n'
                     'S0 -> S1+S0; k1*S0\n'
                     'S1 -> S0+S1; k2*S1\n'
                     'S1 -> S0+S2; k3*S1\n'
                     'S2 + S1 -> S2; k4*S2*S1\n'
                     'S2 -> S1+S1; k5*S2\n'
                     'S2 -> S2+S2; k6*S2\n'
                     'S1 -> S0; k7*S1\n'
                     'S2 + S0 -> S1 + S2; k8*S2*S0\n'
                     'S1 + S1 -> S0 + S1; k9*S1*S1\n'
                     'k0 = 19.145816395561692\n'
                     'k1 = 90.0673521833738\n'
                     'k2 = 41.54190920864631\n'
                     'k3 = 4.7667514994980555\n'
                     'k4 = 15.50936673547638\n'
                     'k5 = 8.171034267002623\n'
                     'k6 = 15.252690388653708\n'
                     'k7 = 7.202857436875558\n'
                     'k8 = 13.147047088765943\n'
                     'k9 = 7.20304738000393\n'
                     'S0 = 1.0\n'
                     'S1 = 5.0\n'
                     'S2 = 9.0')
        trueAntLines = ['var S0',
                        'var S1',
                        'var S2',
                        'S2 -> S0; k0*S2',
                        'S0 -> S1+S0; k1*S0',
                        'S1 -> S0+S1; k2*S1',
                        'S1 -> S0+S2; k3*S1',
                        'S2 + S1 -> S2; k4*S2*S1',
                        'S2 -> S1+S1; k5*S2',
                        'S2 -> S2+S2; k6*S2',
                        'S1 -> S0; k7*S1',
                        'S2 + S0 -> S1 + S2; k8*S2*S0',
                        'S1 + S1 -> S0 + S1; k9*S1*S1',
                        'k0 = 19.145816395561692',
                        'k1 = 90.0673521833738',
                        'k2 = 41.54190920864631',
                        'k3 = 4.7667514994980555',
                        'k4 = 15.50936673547638',
                        'k5 = 8.171034267002623',
                        'k6 = 15.252690388653708',
                        'k7 = 7.202857436875558',
                        'k8 = 13.147047088765943',
                        'k9 = 7.20304738000393',
                        'S0 = 1.0',
                        'S1 = 5.0',
                        'S2 = 9.0']
        astr = self.ant
        testModel = pp.AntimonyModel(astr)
        testModel.combineDuplicateRxns()
        self.assertEqual(testModel.ant, trueAnstr)
        self.assertListEqual(testModel.antLines, trueAntLines)

    def test_deleteUnnecessaryReactions(self):
        astr = self.ant
        testModel = pp.AntimonyModel(astr)
        testModel.combineDuplicateRxns()
        testModel.deleteUnnecessaryReactions()
        trueDeletedRxns = ['S1 -> S0+S1; k2*S1',
                           'S2 -> S2+S2; k6*S2',
                           'S1 -> S0; k7*S1']
        trueAnstr = ('var S0\n'
                    'var S1\n'
                    'var S2\n'
                    'S2 -> S0; k0*S2\n'
                    'S0 -> S1+S0; k1*S0\n'
                    'S1 -> S0+S2; k3*S1\n'
                    'S2 + S1 -> S2; k4*S2*S1\n'
                    'S2 -> S1+S1; k5*S2\n'
                    'S2 + S0 -> S1 + S2; k8*S2*S0\n'
                    'S1 + S1 -> S0 + S1; k9*S1*S1\n'
                    'k0 = 19.145816395561692\n'
                    'k1 = 90.0673521833738\n'
                    'k3 = 4.7667514994980555\n'
                    'k4 = 15.50936673547638\n'
                    'k5 = 8.171034267002623\n'
                    'k8 = 13.147047088765943\n'
                    'k9 = 7.20304738000393\n'
                    'S0 = 1.0\n'
                    'S1 = 5.0\n'
                    'S2 = 9.0')
        self.assertListEqual(testModel.deletedRxns, trueDeletedRxns)
        self.assertEqual(testModel.ant, trueAnstr)