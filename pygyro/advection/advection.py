import numpy as np
from scipy.interpolate              import lagrange
from math                           import pi, floor, ceil

from ..splines.splines              import BSplines, Spline1D, Spline2D
from ..splines.spline_interpolators import SplineInterpolator1D, SplineInterpolator2D
from ..initialisation.initialiser   import fEq
from ..initialisation               import constants

def fieldline(theta,z,full_z,idx,iota):
    return theta+iota(constants.R0)*(full_z[idx]-z)/constants.R0

class ParallelGradient:
    """
    ParallelGradient: Class containing values necessary to derive a function
    along the direction parallel to the flux surface

    Parameters
    ----------
    spline : BSplines
        A spline along the theta direction

    eta_grids : list of array_like
        The coordinates of the grid points in each dimension

    iota : function handle - optional
        Function returning the value of iota at a given radius r.
        Default is constants.iota

    """
    def __init__( self, spline: BSplines, eta_grid: list, iota = constants.iota ):
        # Save z step
        self._dz = eta_grid[2][1]-eta_grid[2][0]
        # Save size in z direction
        self._nz = eta_grid[2].size
        
        # If there are too few points then the access cannot be optimised
        # at the boundaries in the way that has been used
        assert(self._nz>5)
        
        # Save the inverse as it is used multiple times
        self._inv_dz = 1.0/self._dz
        
        # Save theta step. If iota does not vary with the radius then this
        # should be one value. Otherwise it is an array.
        try:
            dtheta =  np.atleast_2d(self._dz * iota() / constants.R0)
        except:
            # The result is transposed to allow it to be used with simply
            # with dz
            dtheta = np.atleast_2d(self._dz * iota(eta_grid[0]) / constants.R0).T
        
        # Determine bz
        self._bz = self._dz / np.sqrt(self._dz**2+dtheta**2)
        
        # Save the necessary spline and interpolator
        self._interpolator = SplineInterpolator1D(spline)
        self._thetaSpline = Spline1D(spline)
        
        # Remember whether or not there are different values for iota
        self._variesInR = self._bz.size!=1
        
        # The positions at which the spline will be evaluated are always the same.
        # They can therefore be calculated in advance
        if (self._variesInR):
            self._thetaVals = np.empty([eta_grid[0].size, eta_grid[1].size, eta_grid[2].size, 6])
            for i,r in enumerate(eta_gird[0]):
                self._getThetaVals(r,self._thetaVals[i],eta_grid,iota)
        else:
            self._thetaVals = np.empty([eta_grid[1].size, eta_grid[2].size, 6])
            self._getThetaVals(eta_grid[0][0],self._thetaVals,eta_grid,iota)
    
    def _getThetaVals( self, r: np.ndarray, thetaVals: np.ndarray, eta_grid: list, iota ):
        # The positions at which the spline will be evaluated are always the same.
        # They can therefore be calculated in advance
        n = eta_grid[2].size
        
        # The first three theta values require the final three z values
        for k,z in enumerate(eta_grid[2][:3]):
            for i,l in enumerate([-3,-2,-1,1,2,3]):
                thetaVals[:,(k+l)%n,i]=fieldline(eta_grid[1],z,eta_grid[2],(k+l)%n,iota)
        
        # The central values only require consecutive values so the modulo
        # operator can be avoided
        for k,z in enumerate(eta_grid[2][3:-3],3):
            for i,l in enumerate([-3,-2,-1,1,2,3]):
                thetaVals[:,(k+l),i]=fieldline(eta_grid[1],z,eta_grid[2],k+l,iota)
        
        # The final three theta values require the first three z values
        for k,z in enumerate(eta_grid[2][-3:],n-3):
            for i,l in enumerate([-3,-2,-1,1,2,3]):
                thetaVals[:,(k+l)%n,i]=fieldline(eta_grid[1],z,eta_grid[2],(k+l)%n,iota)
    
    def parallel_gradient( self, phi_r: np.ndarray, i : int ):
        """
        Get the gradient of a function in the direction parallel to the
        flux surface

        Parameters
        ----------
        phi_r : array_like
            The values of the function at the nodes
        
        i : int
            The current index of r
        
        """
        # Get scalar values necessary for this slice
        if (self._variesInR):
            bz=self._bz[i]
            thetaVals = self._thetaVals[i]
        else:
            bz=self._bz
            thetaVals = self._thetaVals
        der=np.full_like(phi_r,0)
        
        # For each value of z interpolate the spline along theta and add
        # the value multiplied by the corresponding coefficient to the
        # derivative at the point at which it is required
        # This is split into three steps to avoid unnecessary modulo operations
        
        for i in range(3):
            self._interpolator.compute_interpolant(phi_r[:,i],self._thetaSpline)
            der[:,(i+3)%self._nz]-=self._thetaSpline.eval(thetaVals[:,i,0])
            der[:,(i+2)%self._nz]-=9*self._thetaSpline.eval(thetaVals[:,i,1])
            der[:,(i+1)%self._nz]-=45*self._thetaSpline.eval(thetaVals[:,i,2])
            der[:,(i-1)%self._nz]+=45*self._thetaSpline.eval(thetaVals[:,i,3])
            der[:,(i-2)%self._nz]+=9*self._thetaSpline.eval(thetaVals[:,i,4])
            der[:,(i-3)%self._nz]+=self._thetaSpline.eval(thetaVals[:,i,5])
        
        for i in range(3,self._nz-3):
            self._interpolator.compute_interpolant(phi_r[:,i],self._thetaSpline)
            der[:,(i+3)]-=self._thetaSpline.eval(thetaVals[:,i,0])
            der[:,(i+2)]-=9*self._thetaSpline.eval(thetaVals[:,i,1])
            der[:,(i+1)]-=45*self._thetaSpline.eval(thetaVals[:,i,2])
            der[:,(i-1)]+=45*self._thetaSpline.eval(thetaVals[:,i,3])
            der[:,(i-2)]+=9*self._thetaSpline.eval(thetaVals[:,i,4])
            der[:,(i-3)]+=self._thetaSpline.eval(thetaVals[:,i,5])
        
        for i in range(self._nz-3,self._nz):
            self._interpolator.compute_interpolant(phi_r[:,i],self._thetaSpline)
            der[:,(i+3)%self._nz]-=self._thetaSpline.eval(thetaVals[:,i,0])
            der[:,(i+2)%self._nz]-=9*self._thetaSpline.eval(thetaVals[:,i,1])
            der[:,(i+1)%self._nz]-=45*self._thetaSpline.eval(thetaVals[:,i,2])
            der[:,(i-1)%self._nz]+=45*self._thetaSpline.eval(thetaVals[:,i,3])
            der[:,(i-2)%self._nz]+=9*self._thetaSpline.eval(thetaVals[:,i,4])
            der[:,(i-3)%self._nz]+=self._thetaSpline.eval(thetaVals[:,i,5])
        
        der*= ( bz * self._inv_dz )/60
        
        return der

class FluxSurfaceAdvection:
    """
    FluxSurfaceAdvection: Class containing information necessary to carry out
    an advection step along the flux surface.

    Parameters
    ----------
    eta_grid: list of array_like
        The coordinates of the grid points in each dimension

    splines: list of BSplines
        The spline approximations along theta and z

    iota: function handle - optional
        Function returning the value of iota at a given radius r.
        Default is constants.iota

    """
    def __init__( self, eta_grid: list, splines: list, iota = constants.iota ):
        # Save all pertinent information
        self._points = eta_grid[1:3]
        self._nPoints = (self._points[0].size,self._points[1].size)
        self._interpolator = SplineInterpolator1D(splines[0])
        self._thetaSpline = Spline1D(splines[0])
        self._dz = eta_grid[2][1]-eta_grid[2][0]
        # dtheta is a scalar if iota does not depend on r and a vector otherwise
        try:
            self._dtheta =  np.atleast_2d(self._dz * iota() / constants.R0)
        except:
            self._dtheta = np.atleast_2d(self._dz * iota(eta_grid[0]) / constants.R0).T
        
        self._bz = self._dz / np.sqrt(self._dz**2+self._dtheta**2)
    
    def step( self, f: np.ndarray, dt: float, c: float, rGIdx: int = 0 ):
        """
        Carry out an advection step for the flux parallel advection

        Parameters
        ----------
        f: array_like
            The current value of the function at the nodes.
            The result will be stored here
        
        dt: float
            Time-step
        
        c: float
            Advection parameter d_tf + c d_xf=0
        
        rGIdx: int - optional
            The current index of r. Not necessary if iota does not depend on r
        
        """
        assert(f.shape==self._nPoints)
        
        # Find the distance travelled in the z direction
        zDist = -c*self._bz[rGIdx]*dt
        
        # Find the values of theta on the 6 z lines around the end point
        Shifts = floor( zDist ) + np.array([-2,-1,0,1,2,3])
        thetaShifts = self._dtheta[rGIdx]*Shifts
        
        # find the values of the function at each required point
        LagrangeVals = np.ndarray([self._nPoints[1],self._nPoints[0], 6])
        
        for i in range(self._nPoints[1]):
            self._interpolator.compute_interpolant(f[:,i],self._thetaSpline)
            for j,s in enumerate(Shifts):
                LagrangeVals[(i-s)%self._nPoints[1],:,j]=self._thetaSpline.eval(self._points[0]+thetaShifts[j])
        
        # Use lagrange interpolation to find the value at the final position
        for i,z in enumerate(self._points[1]):
            zPts = z+self._dz*Shifts
            for j in range(self._nPoints[0]):
                poly = lagrange(zPts,LagrangeVals[i,j,:])
                f[j,i] = poly(z+zDist)

class VParallelAdvection:
    """
    VParallelAdvection: Class containing information necessary to carry out
    an advection step along the v-parallel surface.

    Parameters
    ----------
    eta_vals: list of array_like
        The coordinates of the grid points in each dimension

    splines: BSplines
        The spline approximations along v

    edgeFunc: function handle - optional
        Function returning the value at the boundary as a function of r and v
        Default is fEquilibrium

    """
    def __init__( self, eta_vals: list, splines: BSplines, edgeFunc = fEq ):
        self._points = eta_vals[3]
        self._nPoints = (self._points.size,)
        self._interpolator = SplineInterpolator1D(splines)
        self._spline = Spline1D(splines)
        
        self._evalFunc = np.vectorize(self.evaluate, otypes=[np.float])
        self._edge = edgeFunc
    
    def step( self, f: np.ndarray, dt: float, c: float, r: float ):
        """
        Carry out an advection step for the v-parallel advection

        Parameters
        ----------
        f: array_like
            The current value of the function at the nodes.
            The result will be stored here
        
        dt: float
            Time-step
        
        c: float
            Advection parameter d_tf + c d_xf=0
        
        r: float
            The radial coordinate
        
        """
        assert(f.shape==self._nPoints)
        self._interpolator.compute_interpolant(f,self._spline)
        
        f[:]=self._evalFunc(self._points-c*dt, r)
    
    def evaluate( self, v, r ):
        if (v<self._points[0] or v>self._points[-1]):
            return self._edge(r,v)
        else:
            return self._spline.eval(v)

class PoloidalAdvection:
    """
    PoloidalAdvection: Class containing information necessary to carry out
    an advection step along the poloidal surface.

    Parameters
    ----------
    eta_vals: list of array_like
        The coordinates of the grid points in each dimension

    splines: list of BSplines
        The spline approximations along theta and r

    """
    def __init__( self, eta_vals: list, splines: list ):
        self._points = eta_vals[1::-1]
        self._shapedQ = np.atleast_2d(self._points[0]).T
        self._nPoints = (self._points[0].size,self._points[1].size)
        self._interpolator = SplineInterpolator2D(splines[0],splines[1])
        self._spline = Spline2D(splines[0],splines[1])
        
        self.evalFunc = np.vectorize(self.evaluate, otypes=[np.float])
    
    def step( self, f: np.ndarray, dt: float, phi: Spline2D, v: float ):
        """
        Carry out an advection step for the poloidal advection

        Parameters
        ----------
        f: array_like
            The current value of the function at the nodes.
            The result will be stored here
        
        dt: float
            Time-step
        
        phi: Spline2D
            Advection parameter d_tf + {phi,f}=0
        
        r: float
            The parallel velocity coordinate
        
        """
        assert(f.shape==self._nPoints)
        self._interpolator.compute_interpolant(f,self._spline)
        
        multFactor = dt/constants.B0
        
        drPhi = phi.eval(*self._points,0,1)/self._points[1]
        dthetaPhi = phi.eval(*self._points,1,0)/self._points[1]
        
        # Step one of Heun method
        # x' = x^n + f(x^n)
        endPts = ( self._shapedQ   -     drPhi*multFactor,
                   self._points[1] + dthetaPhi*multFactor )
        
        for i in range(self._nPoints[0]):
            for j in range(self._nPoints[1]):
                # Handle theta boundary conditions
                while (endPts[0][i][j]<0):
                    endPts[0][i][j]+=2*pi
                while (endPts[0][i][j]>2*pi):
                    endPts[0][i][j]-=2*pi
                
                # Phi is 0 outside of domain
                if (not (endPts[1][i][j]<self._points[1][0] or 
                         endPts[1][i][j]>self._points[1][-1])):
                    # Add the new value of phi to the derivatives
                    # x^{n+1} = x^n + 0.5( f(x^n) + f(x^n + f(x^n)) )
                    #                               ^^^^^^^^^^^^^^^
                    drPhi[i,j]     += phi.eval(endPts[0][i][j],endPts[1][i][j],0,1)/endPts[1][i][j]
                    dthetaPhi[i,j] += phi.eval(endPts[0][i][j],endPts[1][i][j],1,0)/endPts[1][i][j]
        
        multFactor*=0.5
        
        # Step two of Heun method
        # x^{n+1} = x^n + 0.5( f(x^n) + f(x^n + f(x^n)) )
        endPts = ( self._shapedQ   -     drPhi*multFactor,
                   self._points[1] + dthetaPhi*multFactor )
        
        # Find value at the determined point
        for i,theta in enumerate(self._points[0]):
            for j,r in enumerate(self._points[1]):
                f[i,j]=self.evalFunc(endPts[0][i][j],endPts[1][i][j],v)
    
    def exact_step( self, f, endPts, v ):
        assert(f.shape==self._nPoints)
        self._interpolator.compute_interpolant(f,self._spline)
        
        for i,theta in enumerate(self._points[0]):
            for j,r in enumerate(self._points[1]):
                f[i,j]=self.evalFunc(endPts[0][i][j],endPts[1][i][j],v)
    
    def evaluate( self, theta, r, v ):
        if (r<self._points[1][0]):
            return 0
            #return fEq(self._points[1][0],v);
        elif (r>self._points[1][-1]):
            return 0
            #return fEq(r,v);
        else:
            while (theta>2*pi):
                theta-=2*pi
            while (theta<0):
                theta+=2*pi
            return self._spline.eval(theta,r)
