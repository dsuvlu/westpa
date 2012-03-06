'''
Tools for Monte Carlo bootstrap error analysis
'''

from __future__ import print_function, division; __metaclass__ = type
import math, numpy

def get_bssize(alpha):
    '''Return a bootstrap data set size appropriate for the given confidence level'''
    return int(10**(math.ceil(-math.log10(alpha)) + 1))

def bootstrap_ci(estimator, data, alpha, n_sets=None, args=(), kwargs={}, sort=numpy.msort, extended_output = False):
    '''Perform a Monte Carlo bootstrap of a (1-alpha) confidence interval for the given ``estimator``.
    Returns (fhat, ci_lower, ci_upper), where fhat is the result of ``estimator(data, *args, **kwargs)``,
    and ``ci_lower`` and ``ci_upper`` are the lower and upper bounds of the surrounding confidence
    interval, calculated by calling ``estimator(syndata, *args, **kwargs)`` on each synthetic data
    set ``syndata``.  If ``n_sets`` is provided, that is the number of synthetic data sets generated,
    otherwise an appropriate size is selected automatically (see ``get_bssize()``).
    
    ``sort``, if given, is applied to sort the results of calling ``estimator`` on each 
    synthetic data set prior to obtaining the confidence interval.
    
    Individual entries in synthetic data sets are selected by the first index of ``data``, allowing this
    function to be used on arrays of multidimensional data.
    
    If ``extended_output`` is True (by default not), instead of returning (fhat, lb, ub), this function returns
    (fhat, lb, ub, ub-lb, abs((ub-lb)/fhat), and max(ub-fhat,fhat-lb)) (that is, the estimated value, the
    lower and upper bounds of the confidence interval, the width of the confidence interval, the relative
    width of the confidence interval, and the symmetrized error bar of the confidence interval).'''
    
    data = numpy.asanyarray(data)
    
    fhat = estimator(data, *args, **kwargs)
    
    try:
        estimator_shape = fhat.shape
    except AttributeError:
        estimator_shape = ()
        
    try:
        estimator_dtype = fhat.dtype
    except AttributeError:
        estimator_dtype = type(fhat) 
        
    dlen = len(data)
    n_sets = n_sets or get_bssize(alpha)
    
    f_synth = numpy.empty((n_sets,) + estimator_shape, dtype=estimator_dtype)
    
    for i in xrange(0, n_sets):
        indices = numpy.random.randint(dlen, size=(dlen,))
        f_synth[i] = estimator(data[indices], *args, **kwargs)
        
    f_synth_sorted = sort(f_synth)
    lbi = int(math.floor(n_sets*alpha/2))
    ubi = int(math.ceil(n_sets*(1-alpha/2)))
    lb = f_synth_sorted[lbi]
    ub = f_synth_sorted[ubi]
    
    try:
        if extended_output:
            return (fhat, lb, ub, ub-lb, abs((ub-lb)/fhat) if fhat else 0, max(ub-fhat,fhat-lb))
        else:
            return (fhat, lb, ub)
    finally:
        # Do a little explicit memory management
        del f_synth, f_synth_sorted
    
