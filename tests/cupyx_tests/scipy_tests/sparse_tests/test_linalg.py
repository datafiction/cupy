import unittest

import numpy
import pytest
try:
    import scipy.sparse
    import scipy.sparse.linalg
    import scipy.stats
    scipy_available = True
except ImportError:
    scipy_available = False

import cupy
from cupy import testing
from cupy.testing import condition
from cupyx.scipy import sparse
import cupyx.scipy.sparse.linalg  # NOQA


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@unittest.skipUnless(scipy_available, 'requires scipy')
class TestLsqr(unittest.TestCase):

    def setUp(self):
        rvs = scipy.stats.randint(0, 15).rvs
        self.A = scipy.sparse.random(50, 50, density=0.2, data_rvs=rvs)
        self.b = numpy.random.randint(15, size=50)

    def test_size(self):
        for xp, sp in ((numpy, scipy.sparse), (cupy, sparse)):
            A = sp.csr_matrix(self.A, dtype=self.dtype)
            b = xp.array(numpy.append(self.b, [1]), dtype=self.dtype)
            with pytest.raises(ValueError):
                sp.linalg.lsqr(A, b)

    def test_shape(self):
        for xp, sp in ((numpy, scipy.sparse), (cupy, sparse)):
            A = sp.csr_matrix(self.A, dtype=self.dtype)
            b = xp.array(numpy.tile(self.b, (2, 1)), dtype=self.dtype)
            with pytest.raises(ValueError):
                sp.linalg.lsqr(A, b)

    @condition.retry(10)
    @testing.numpy_cupy_allclose(atol=1e-1, sp_name='sp')
    def test_csrmatrix(self, xp, sp):
        A = sp.csr_matrix(self.A, dtype=self.dtype)
        b = xp.array(self.b, dtype=self.dtype)
        x = sp.linalg.lsqr(A, b)
        return x[0]

    @condition.retry(10)
    @testing.numpy_cupy_allclose(atol=1e-1, sp_name='sp')
    def test_ndarray(self, xp, sp):
        A = xp.array(self.A.A, dtype=self.dtype)
        b = xp.array(self.b, dtype=self.dtype)
        x = sp.linalg.lsqr(A, b)
        return x[0]
