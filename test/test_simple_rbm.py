import unittest
from RBM2 import *
from activationFunction import *
import theano.sandbox.cuda as cuda
from utils import *
import theano.tensor as T
import numpy as np
import scipy.stats as ss

class SingleRBMTest(unittest.TestCase):
    def setUpRBM(self):
        v = 5
        v2 = 5
        h = 10
        tr = TrainParam(learning_rate=0.01,
                        momentum_type=CLASSICAL,
                        momentum=0.5,
                        weight_decay=0.01,
                        plot_during_training=True,
                        output_directory="Test",
                        sparsity_constraint=False,
                        batch_size=1,
                        epochs=15)

        rbm = RBM(v, v2, h,
                  associative=False, # for now
                  cd_type=CLASSICAL,
                  cd_steps=10,
                  train_parameters=tr)

        self.rbm = rbm
        self.x = np.array([[1, 1, 1, 0, 0]], dtype=np.float32)
        self.tx = theano.shared(np.array([[1, 1, 1, 0, 0]], dtype=np.float32))
        self.x2 = np.array([[1, 1, 1, 0, 0],
                            [0, 0, 0, 0, 1]],
                           dtype=np.float32)
        self.tx2 = theano.shared(np.array([[1, 1, 1, 0, 0],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 1],
                            ],
                            dtype=np.float32))

    def test_parameters_order(self):
        self.setUpRBM()
        rbm = self.rbm
        self.assertEqual(str(rbm.params[0]), 'W')
        self.assertEqual(str(rbm.params[1]), 'v_bias')
        self.assertEqual(str(rbm.params[2]), 'h_bias')

    def test_negative_statistics(self):
        self.setUpRBM()
        rbm = self.rbm
        x = T.matrix("x")
        res = rbm.negative_statistics(x)
        updates = res[0]

        # Returns chain end
        f = theano.function([x], res[1:], updates=updates)

        # sample, v, vp, vs, h, hp, hs = f(self.x)
        # print sample
        # print vs

        result = f(self.x)
        # print result[0]

        pass

    def test_free_energy(self):
        self.setUpRBM()
        rbm = self.rbm
        w = rbm.W.get_value(borrow=True)
        v = T.dmatrix("v")
        v_bias = np.array(rbm.v_bias.eval())
        h_bias = np.array(rbm.h_bias.eval())

        res = rbm.free_energy(v)
        f = theano.function([v], [res])
        theano_res = np.array(f(self.x))

        # Test for case only v1 is present
        n1 = - np.dot(self.x, v_bias)
        n2 = np.exp(h_bias + np.dot(self.x, w))
        n3 = - np.sum(np.log(1 + n2))
        np_res = n1 + n3

        # print theano_res
        # print np_res

        diff = theano_res == np_res
        self.assertAlmostEqual(theano_res, np_res, places=5)

    def test_partial_derivatives(self):
        self.setUpRBM()
        rbm = self.rbm
        x = T.dmatrix("x")
        y = T.dmatrix("y")

        grad_meta = rbm.get_partial_derivitives(x, y)
        gradients = grad_meta["gradients"]
        updates = grad_meta["updates"]
        v_total_inputs = grad_meta["statistics"]
        g_W, g_v, g_h = gradients
        f = theano.function([x], [g_W, g_v, g_h], updates=updates)
        g_W, g_v, g_h = f(self.x)
        # print g_W
        # print g_v
        # print g_h
        pass

    def test_get_train_fn(self):
        self.setUpRBM()
        rbm = self.rbm
        fn = rbm.get_train_fn(self.tx, None)
        res = fn(0)
        print res

        pass

    def test_train(self):
        self.setUpRBM()
        rbm = self.rbm
        pass

if __name__ == '__main__':
    print "Test Simple RBM"
    unittest.main()