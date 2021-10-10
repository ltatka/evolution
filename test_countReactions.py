import unittest
import countReactions as cr

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

    def test_getReactionType(self):
        rxn1 = 'S2 -> S1+S1; k5*S2\n'
        rxn2 = 'S1 + S1 -> S0 + S1; k9*S1*S1\n'
        rxn3 = 'S1+S1->S2; k10*S1*S1'
        self.assertEqual(cr.getReactionType(rxn1), 'uni-bi')
        self.assertEqual(cr.getReactionType(rxn2), 'bi-bi')
        self.assertEqual(cr.getReactionType(rxn3), 'bi-uni')

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
        self.assertEqual(rType, 'bi-uni')

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

    def test_getPortions(self):
        reactionDict = {'uni-uni': 25,
                        'uni-bi': 15,
                        'bi-uni': 10,
                        'bi-bi': 50,
                        'degradation': 45,
                        'autocatalysis': 15,
                        'total': 100}
        truePortions = {'uni-uni portion': 0.25,
                        'uni-uni': 25,
                        'uni-bi portion': 0.15,
                        'uni-bi': 15,
                        'bi-uni portion': 0.1,
                        'bi-uni': 10,
                        'bi-bi portion': 0.5,
                        'bi-bi': 50,
                        'degradation portion': 0.45,
                        'degradation': 45,
                        'autocatalysis portion': 0.15,
                        'autocatalysis': 15,
                        'total': 100,
                        }
        rxnDict = cr.getPortions(reactionDict)
        self.assertDictEqual(rxnDict, truePortions)

    def test_reactionCounts(self):
        rxnCounts = cr.countReactions(self.model)
        trueCounts = {'uni-uni portion': 0.14285714285714285,
                      'uni-uni': 1,
                      'uni-bi portion': 0.42857142857142855,
                      'uni-bi': 3,
                      'bi-uni portion': 0.14285714285714285,
                      'bi-uni': 1,
                      'bi-bi portion': 0.2857142857142857,
                      'bi-bi': 2,
                      'degradation portion': 0.14285714285714285,
                      'degradation': 1,
                      'autocatalysis portion': 0.0,
                      'autocatalysis': 0,
                      'total': 7}
        self.assertDictEqual(rxnCounts, trueCounts)

