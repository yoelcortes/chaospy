"""A distribution that is based on a kernel density estimator (KDE)."""
import numpy
from scipy.stats import gaussian_kde

from ..baseclass import Dist
from ..operators.addition import Add
from .uniform import Uniform



class sample_dist(Dist):
    """A distribution that is based on a kernel density estimator (KDE)."""
    def __init__(self, samples, lo, up):
        self.samples = samples
        self.kernel = gaussian_kde(samples, bw_method="scott")
        self.flo = self.kernel.integrate_box_1d(0, lo)
        self.fup = self.kernel.integrate_box_1d(0, up)
        super(sample_dist, self).__init__(lo=lo, up=up)

    def _cdf(self, x, lo, up):
        cdf_vals = numpy.zeros(x.shape)
        for i in range(0, len(x)):
            cdf_vals[i] = [self.kernel.integrate_box_1d(0, x_i) for x_i in x[i]]
        cdf_vals = (cdf_vals - self.flo) / (self.fup - self.flo)
        return cdf_vals

    def _pdf(self, x, lo, up):
        return self.kernel(x)

    def _bnd(self, x, lo, up):
        return (lo, up)


def SampleDist(samples, lo=None, up=None):
    """
    Distribution based on samples.

    Estimates a distribution from the given samples by constructing a kernel
    density estimator (KDE).

    Args:
        samples:
            Sample values to construction of the KDE
        lo (float) : Location of lower threshold
        up (float) : Location of upper threshold

    Example:
        >>> distribution = chaospy.SampleDist([0, 1, 1, 1, 2])
        >>> print(distribution)
        sample_dist(lo=0, up=2)
        >>> q = numpy.linspace(0, 1, 5)
        >>> print(numpy.around(distribution.inv(q), 4))
        [0.     0.6016 1.     1.3984 2.    ]
        >>> print(numpy.around(distribution.fwd(distribution.inv(q)), 4))
        [0.   0.25 0.5  0.75 1.  ]
        >>> print(numpy.around(distribution.pdf(distribution.inv(q)), 4))
        [0.2254 0.4272 0.5135 0.4272 0.2254]
        >>> print(numpy.around(distribution.sample(4), 4))
        [1.2354 0.3248 1.845  0.9733]
        >>> print(numpy.around(distribution.mom(1), 4))
        1.0
        >>> print(numpy.around(distribution.ttr([1, 2, 3]), 4))
        [[1.3835 0.7983 1.1872]
         [0.2429 0.2693 0.4102]]
    """
    samples = numpy.asarray(samples)
    if lo is None:
        lo = samples.min()
    if up is None:
        up = samples.max()

    try:
        #construct the kernel density estimator
        dist = sample_dist(samples, lo, up)

    #raised by gaussian_kde if dataset is singular matrix
    except numpy.linalg.LinAlgError:
        dist = Uniform(lower=-numpy.inf, upper=numpy.inf)

    return dist
