import unittest
import evolUtils as ev

class MyTestCase(unittest.TestCase):


    def test(self):
        ant = '''
var S0
var S1
var S2
S1 + S2 -> S2 + S2; k0*S1*S2
S1 + S0 -> S1 + S1; k1*S1*S0
S1 -> S1+S0; k2*S1
S2 + S0 -> S0; k3*S2*S0
k0 = 1.9920416329912947
k1 = 47.54258428799684
k2 = 26.347064160356418
k3 = 32.59216460314004
S0 = 1.0
S1 = 5.0
S2 = 9.0
'''
        model = ev.convertToTModel(ant)

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
