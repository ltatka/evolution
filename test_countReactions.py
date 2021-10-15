import unittest
import countReactions as cr
from sklearn import datasets


class UnitTests(unittest.TestCase):
    model = ('var S0\n'
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

    def test_getRateLawSpecies(self):
        rxn1 = 'S2 -> S1+S1; k5*S2\n'
        rxn2 = 'S1 + S1 -> S0 + S1; k9*S1*S1\n'
        components1 = cr.getRateLawSpecies(rxn1)
        components2 = cr.getRateLawSpecies(rxn2)
        self.assertListEqual(components1, ['S2'])
        self.assertListEqual(components2, ['S1', 'S1'])

    def test_rateLawIsIncorrect(self):
        r1 = 'S0 -> S1+S0; k1*S0\n'
        r2 = 'S2 + S0 -> S1 + S2; k8*S2*S0\n'
        r3 = 'S0 -> S1+S0; k1*S0*S0\n'
        r4 = 'S0 -> S1+S0; k1*S2*S0\n'
        r5 = 'S0 -> S1+S0; k1*S2\n'
        r6 = 'S1 + S2 -> S0; k1*S1*S1'
        self.assertFalse(cr.rateLawIsIncorrect(r1))
        self.assertFalse(cr.rateLawIsIncorrect(r2))
        self.assertTrue(cr.rateLawIsIncorrect(r3))
        self.assertTrue(cr.rateLawIsIncorrect(r4))
        self.assertTrue(cr.rateLawIsIncorrect(r5))
        self.assertTrue(cr.rateLawIsIncorrect(r6))

    def test_getReactionType(self):
        rxn1 = 'S2 -> S1+S1; k5*S2\n'
        rxn2 = 'S1 + S1 -> S0 + S1; k9*S1*S1\n'
        rxn3 = 'S1+S1->S2; k10*S1*S1'
        self.assertEqual(cr.getReactionType(rxn1), 'Uni-Bi')
        self.assertEqual(cr.getReactionType(rxn2), 'Bi-Bi')
        self.assertEqual(cr.getReactionType(rxn3), 'Bi-Uni')

    def test_splitReactantsProducts(self):
        rxn1 = 'S2 -> S1+S1; k5*S2\n'
        rxn2 = 'S1 + S1 -> S0 + S1; k9*S1*S1\n'
        rxn3 = 'S1+S0->S2; k10*S1*S0'
        r1, p1 = cr.splitReactantsProducts(rxn1)
        r2, p2 = cr.splitReactantsProducts(rxn2)
        r3, p3 = cr.splitReactantsProducts(rxn3)
        r4, p4, rType = cr.splitReactantsProducts(rxn3, returnType=True)
        self.assertListEqual(r1, ['S2'])
        self.assertListEqual(p1, ['S1', 'S1'])
        self.assertListEqual(r2, ['S1', 'S1'])
        self.assertListEqual(p2, ['S0', 'S1'])
        self.assertListEqual(r3, ['S1', 'S0'])
        self.assertListEqual(p3, ['S2'])
        self.assertEqual(rType, 'Bi-Uni')

    def test_isAutocatalytic(self):
        r1 = 'S1 -> S2; rateLaw'
        r2 = 'S1 + S1 -> S1; ratelaw'
        r4 = 'S1 -> S1+S1; ratelaw'
        r5 = 'S1 -> S2 + S2; ratelaw'
        r6 = 'S1 + S2 -> S0+S3; ratelaw'
        r7 = 'S1 + S2 -> S1+S1; ratelaw'
        r8 = 'S1 -> S1+S2; ratelaw'
        self.assertTrue(cr.isAutocatalytic(r4))
        self.assertTrue(cr.isAutocatalytic(r7))
        self.assertFalse(cr.isAutocatalytic(r8))
        self.assertFalse(cr.isAutocatalytic(r1))
        self.assertFalse(cr.isAutocatalytic(r2))
        self.assertFalse(cr.isAutocatalytic(r5))
        self.assertFalse(cr.isAutocatalytic(r6))

    def test_isDegradation(self):
        r1 = 'S1 + S2 -> S2; ratelaw'
        r2 = 'S1 + S1 -> S1; ratelaw'
        r3 = 'S1 + S2 -> S0; ratelaw'
        r4 = 'S1 + S2 -> S2 + S0; ratelaw'
        self.assertTrue(cr.isDegradation(r1))
        self.assertTrue(cr.isDegradation(r2))
        self.assertFalse(cr.isDegradation(r3))
        self.assertFalse(cr.isDegradation(r4))

    def test_countReactions(self):
        rxnCounts = cr.countReactions(self.model)
        trueCounts = {'Uni-Uni': 1,
                      'Uni-Bi': 3,
                      'Bi-Uni': 1,
                      'Bi-Bi': 2,
                      'Degradation': 1,
                      'Autocatalysis': 0,
                      'Total': 7}
        self.assertDictEqual(rxnCounts, trueCounts)

    def test_autocatalysisPresent(self):
        counts1 = {'Uni-Uni': 1,
                   'Uni-Bi': 3,
                   'Bi-Uni': 1,
                   'Bi-Bi': 2,
                   'Degradation': 1,
                   'Autocatalysis': 0,
                   'Total': 7}
        counts2 = {'Uni-Uni': 1,
                   'Uni-Bi': 3,
                   'Bi-Uni': 1,
                   'Bi-Bi': 2,
                   'Degradation': 1,
                   'Autocatalysis': 2,
                   'Total': 7}
        self.assertEqual(int(counts1['Autocatalysis'] > 0), 0)
        self.assertEqual(int(counts2['Autocatalysis'] > 0), 1)

    def test_bootstrap(self):
        leftSkew = [1, 1.2, 2, .9, 3, 1, 1, 1, 3, 4]
        rightSkew = [9, 9, 8.9, 8, 8, 9., 7, 7.8, 6]
        leftSkew2 = [1, .8, .9, 2, 3.9, 3.9, 1, 1, 1]
        p = cr.permutationTest(leftSkew, rightSkew)
        self.assertTrue(p < 0.05)
        p = cr.permutationTest(leftSkew, leftSkew2)
        self.assertTrue(p > 0.05)
