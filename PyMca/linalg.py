#    Copyright (c) 2018-2013 V.A. Sole, ESRF
#
#   Permission to use and redistribute the source code or binary forms of
#   this software and its documentation, with or without modification is
#   hereby granted provided that the above notice of copyright, these
#   terms of use, and the disclaimer of warranty below appear in the
#   source code and documentation, and that none of the names of The
#   European Synchrotron Radiation Facility, or the authors
#   appear in advertising or endorsement of works derived from this
#   software without specific prior written permission from all parties.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#   SOFTWARE OR THE USE OR OTHER DEALINGS IN THIS SOFTWARE.
#
import numpy
__license__ = "BSD"
__author__ = "V.A. Sole - ESRF Data Analysis"
__doc__ = """
Similar function to the numpy lstsq function with a more rigorous uncertainty
treatement besides other optimizations in view of simultaneously solving several
equations of the form `a x = b`. Hopefully licensed under the same terms as
numpy itself (BSD license).
"""

# Linear Least Squares

def lstsq(a, b, rcond=None, sigma_b=None, weight=False,
          uncertainties=True, covariances=False, digested_output=False):
    """
    Return the least-squares solution to a linear matrix equation.

    Solves the equation `a x = b` by computing a vector `x` that
    minimizes the Euclidean 2-norm `|| b - a x ||^2`.  The equation may
    be under-, well-, or over- determined (i.e., the number of
    linearly independent rows of `a` can be less than, equal to, or
    greater than its number of linearly independent columns).  If `a`
    is square and of full rank, then `x` (but for round-off error) is
    the "exact" solution of the equation.

    Parameters
    ----------
    a : array_like, shape (M, N)
        "Model" matrix.
    b : array_like, shape (M,) or (M, K)
        Ordinate or "dependent variable" values. If `b` is two-dimensional,
        the least-squares solution is calculated for each of the `K` columns
        of `b`.
    sigma_b : uncertainties on the b values

    weight: 0 - No data weighting.
                If required, uncertainties will be calculated using either the
                supplied experimental uncertainties or an experimental
                uncertainty of 1 for each data point.
            1 - Statistical weight.
                Weighted fit using the supplied experimental uncertainties or the
                square root of the b values.

    uncertainties: If False, no uncertainties will be calculated unless the covariance
                matrix is requested.

    covariances: If True, an array of covariance matrix/matrices will be returned.

    digested_output: If True, returns a dictionnary with explicit keys

    Returns
    -------
    x : ndarray, shape (N,) or (N, K)
        Least-squares solution.  The shape of `x` depends on the shape of
        `b`.

    uncertainties: ndarray, shape (N,) or (N, K)

    covariances: ndarray, shape (N, N) or (K, N, N)

    Examples
    --------
    Fit a line, ``y = mx + c``, through some noisy data-points:

    >>> x = np.array([0, 1, 2, 3])
    >>> y = np.array([-1, 0.2, 0.9, 2.1])

    By examining the coefficients, we see that the line should have a
    gradient of roughly 1 and cut the y-axis at, more or less, -1.

    We can rewrite the line equation as ``y = Ap``, where ``A = [[x 1]]``
    and ``p = [[m], [c]]``.  Now use `lstsq` to solve for `p`:

    >>> A = np.vstack([x, np.ones(len(x))]).T
    >>> A
    array([[ 0.,  1.],
           [ 1.,  1.],
           [ 2.,  1.],
           [ 3.,  1.]])

    >>> m, c = np.linalg.lstsq(A, y)[0]
    >>> print m, c
    1.0 -0.95

    Plot the data along with the fitted line:

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(x, y, 'o', label='Original data', markersize=10)
    >>> plt.plot(x, m*x + c, 'r', label='Fitted line')
    >>> plt.legend()
    >>> plt.show()

    """

    a = numpy.array(a, dtype=numpy.float, copy=False)
    b = numpy.array(b, dtype=numpy.float, copy=False)
    a_shape = a.shape
    b_shape = b.shape
    original = b_shape
    if len(a_shape) != 2:
        raise ValueError("Model matrix must be two dimensional")
    if len(b_shape) == 1:
        b.shape = b_shape[0], 1
        b_shape = b.shape

    m  = a.shape[0]
    n  = a.shape[1]

    if m != b.shape[0]:
        raise ValueError('Incompatible dimensions between A and b matrices')

    fastest = False
    if sigma_b is not None:
        # experimental uncertainties provided these are the ones to use (if any)
        w = numpy.abs(numpy.array(sigma_b, dtype=numpy.float, copy=False))
        w = w + numpy.equal(w, 0)
        w.shape = b_shape
    elif weight == 0:
        # we have an unweighted fit with no uncertainties
        # assume all the uncertainties equal to 1
        fastest = True
        w = numpy.ones(b.shape, numpy.float)
    else:
        # "statistical" weight
        # we are asked to somehow weight the data but no uncertainties provided        
        # assume the uncertainties are the square root of the b values ...
        w = numpy.sqrt(numpy.abs(b))
        w = w + numpy.equal(w, 0)

    if covariances:
        covarianceMatrix = numpy.zeros((b_shape[1], n, n), numpy.float)

    if not weight:
        # no weight is applied
        # get the SVD decomposition of the A matrix
        U, s, V = numpy.linalg.svd(a, full_matrices=False)

        if rcond is None:
            s_cutoff = n * numpy.finfo(numpy.float).eps
        else:
            s_cutoff = rcond * s[0]
        s[s < s_cutoff] = numpy.inf
        
        # and get the parameters
        s.shape = -1
        dummy = numpy.dot(V.T, numpy.eye(n)*(1./s))
        parameters = numpy.dot(dummy, numpy.dot(U.T, b))
        parameters.shape = n, b.shape[1]
        if uncertainties or covariances:
            # get the uncertainties
            #(in the no-weight case without experimental uncertainties,
            # the uncertainties on the data points are ignored and the
            # uncertainty on the fitted parameters are independent of the input data!!!!)
            if fastest:
                # This is correct for all weights equal to 1
                _covariance = numpy.dot(dummy, dummy.T)
                sigmapar = numpy.sqrt(numpy.diag(_covariance))
                sigmapar = numpy.outer(sigmapar, numpy.ones(b_shape[1]))
                sigmapar.shape = n, b_shape[1]
                if covariances:
                    covarianceMatrix[:] = _covariance
            elif covariances:
                # loop in order not to use potentially big matrices
                # but calculates the covariance matrices
                # It only makes sense if the covariance matrix is requested
                sigmapar = numpy.zeros((n, b_shape[1]), numpy.float)
                for k in range(b_shape[1]):
                    pseudoData = numpy.eye(b_shape[0]) * w[:, k]
                    tmpTerm = numpy.dot(dummy, numpy.dot(U.T, pseudoData))
                    _covariance[:, :] = numpy.dot(tmpTerm, tmpTerm.T)
                    sigmapar[:, k] = numpy.sqrt(numpy.diag(_covariance))
                    covarianceMatrix[k] = _covariance
            else:
                # loop in order not to use potentially big matrices
                # but not calculating the covariance matrix
                d = numpy.zeros(b.shape, numpy.float)
                sigmapar = numpy.zeros((n, b_shape[1]))
                for k in range(b_shape[0]):
                    d[k] = w[k]
                    sigmapar += (numpy.dot(dummy, numpy.dot(U.T, d))) ** 2
                    d[k] = 0.0
                sigmapar[:, :] = numpy.sqrt(sigmapar)
    else:
        parameters = numpy.zeros((n, b_shape[1]), numpy.float)
        sigmapar = numpy.zeros((n, b_shape[1]), numpy.float)
        for i in range(b_shape[1]):
            tmpWeight = w[:, i:i+1]
            tmpData = b[:, i:i+1] / tmpWeight
            A = a / tmpWeight
            U, s, V = numpy.linalg.svd(A, full_matrices=False)
            if rcond is None:
                s_cutoff = n * numpy.finfo(numpy.float).eps
            else:
                s_cutoff = rcond * s[0]
            s[s < s_cutoff] = numpy.inf
            s.shape = -1
            dummy = numpy.dot(V.T, numpy.eye(n)*(1./s))
            parameters[:, i:i+1] = numpy.dot(dummy, numpy.dot(U.T, tmpData))
            if uncertainties or covariances:
                # get the uncertainties
                _covariance = numpy.dot(dummy, dummy.T)
                sigmapar[:, i] = numpy.sqrt(numpy.diag(_covariance))
                if covariances:
                    covarianceMatrix[i] = _covariance

    if len(original) == 1:
        parameters.shape = -1
    if covariances:
        sigmapar.shape = parameters.shape
        if len(original) == 1:
            covarianceMatrix.shape = parameters.shape[0], parameters.shape[0] 
        result = [parameters, sigmapar, covarianceMatrix]
    elif uncertainties:
        sigmapar.shape = parameters.shape
        result = [parameters, sigmapar]
    else:
        result = [parameters]

    if digested_output:
        ddict = {}
        ddict['parameters'] = result[0]
        if len(result) > 1:
            ddict['uncertainties'] = result[1]
        elif covariances:
            ddict['covariances'] = result[2]
        return ddict
    else:
        return result
        

def getModelMatrixFromFunction(model_function, dummy_parameters, xdata, derivative=None):
    nPoints = xdata.size
    nParameters = len(dummy_parameters)
    modelMatrix = numpy.zeros((nPoints, nParameters) , numpy.float)
    pwork = dummy_parameters * 1
    for i in range(len(dummy_parameters)):
        fitparam = dummy_parameters[i]
        if derivative is None:
            delta = (pwork[i] + numpy.equal(fitparam, 0.0)) * 0.00001
            pwork[i] = fitparam + delta
            f1 = model_function(pwork, xdata)
            pwork[i] = fitparam - delta
            f2 = model_function(pwork, xdata)
            help0 = (f1-f2) / (2.0 * delta)
            pwork[i] = fitparam
        else:
            help0 = derivative(pwork, i, xdata)
        help0.shape = -1
        modelMatrix[:, i] = help0
    return modelMatrix

def modelFunction(p, x):
    return p[0] + (p[1] + p[2] * x) * x

def test1():
    x = numpy.arange(10000.)
    x.shape = -1, 1
    y = modelFunction([100., 50., 4.], x)
    A = getModelMatrixFromFunction(modelFunction, [0.0, 0.0, 0.0], x)
    parameters, uncertainties = lstsq(A, y, uncertainties=True, weight=False)
    print("Expected = 100., 50., 4.")
    print("Obtained = %f, %f, %f" % (parameters[0], parameters[1], parameters[2]))

def test2():
    import time
    try:
        from PyMca import Gefit
        GEFIT = True
        def f(p, x):
            return p[1] * x + p[0]
    except:
        GEFIT = False
    data = "0 0.8214 0.1 1 2.8471 0.3 2 4.852 0.5 3 7.5347 0.7 4 10.2464 0.9 5 10.2707 1.1 6 12.8011 1.3 7 13.7108 1.5 8 17.8501 1.7 9 15.3667 1.9 10 19.3933 2.1"
    data = numpy.array([float(x) for x in data.split()])
    data.shape = -1, 3

    # the model matrix for a straight line
    A = numpy.ones((data.shape[0],2), numpy.float)
    A[:, 1] = data[:, 0]
    print("Unweighted results:")
    t0 = time.time()
    y =  numpy.ones((data.shape[0], 1000), numpy.float) * data[:, 1:2]
    sigmay =  numpy.ones((data.shape[0], 1000), numpy.float) * data[:, 2:3]
    parameters, uncertainties = lstsq(A, y, #sigma_b=sigmay, #sigma_b=numpy.ones(sigmay.shape),
                                      uncertainties=True, weight=False)
    print("Elapsed = %f" % (time.time() - t0))
    print("Parameters    = %f, %f" % (parameters[0,100], parameters[1, 100]))
    print("Uncertainties = %f, %f" % (uncertainties[0,100], uncertainties[1, 100]))
    if GEFIT:
        t0 = time.time()
        for i in range(y.shape[1]):
            parameters, chisq, uncertainties = Gefit.LeastSquaresFit(f, [0.0, 0.0],
                                                xdata=data[:,0],
                                                ydata=data[:,1],
                                                sigmadata=data[:,2],
                                                weightflag=0,
                                                linear=1)
        print("Elapsed = %f" % (time.time() - t0))
        print("Gefit results:")
        print("Parameters    = %f, %f" % (parameters[0], parameters[1]))
        print("Uncertainties = %f, %f" % (uncertainties[0], uncertainties[1]))
                                                
    print("Mathematica results:")
    print("Parameters    = %f, %f" % (1.57043, 1.78945))
    print("Uncertainties = %f, %f" % (0.68363, 0.11555))

    print("Weighted results")
    t0 = time.time()
    #parameters, uncertainties = lstsq(A, data[:, 1], sigma_b=data[:,2],
    parameters, uncertainties = lstsq(A, y, sigma_b=numpy.outer(data[:,2], numpy.ones((1000, 1))),
                                      uncertainties=True, weight=True)
    print("Elapsed = %f" % (time.time() - t0))
    print("Parameters    = %f, %f" % (parameters[0, 100], parameters[1, 100]))
    print("Uncertainties = %f, %f" % (uncertainties[0, 100], uncertainties[1, 100]))    
    if GEFIT:
        parameters, chisq, uncertainties = Gefit.LeastSquaresFit(f, [0.0, 0.0],
                                                xdata=data[:,0],
                                                ydata=data[:,1],
                                                sigmadata=data[:,2],
                                                weightflag=1,
                                                linear=1)
        print("Gefit results:")
        print("Parameters    = %f, %f" % (parameters[0], parameters[1]))
        print("Uncertainties = %f, %f" % (uncertainties[0], uncertainties[1]))

    print("Mathematica results:")
    print("Parameters    = %f, %f" % (0.843827, 1.97982))
    print("Uncertainties = %f, %f" % (0.092449, 0.07262))

    return data

if __name__ == "__main__":
    test1()
    test2()