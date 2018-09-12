from pyccel.decorators import types

@types('double','double[:]','int','double[:]','int')
def eval_spline_1d_scalar(x,knots,degree,coeffs,der=0):
    span  =  find_span( knots, degree, x )
    
    from numpy      import empty
    basis  = empty( degree+1, dtype=float )
    if (der==0):
        basis_funs( knots, degree, x, span, basis )
    elif (der==1):
        basis_funs_1st_der( knots, degree, x, span, basis )
    
    y=0.0
    for j in range(degree+1):
        y+=coeffs[span-degree+j]*basis[j]
    return y

@types('double[:]','double[:]','int','double[:]','double[:]','int')
def eval_spline_1d_vector(x,knots,degree,coeffs,y,der=0):
    from numpy      import empty
    if (der==0):
        for i in range(len(x)):
            span  =  find_span( knots, degree, x[i] )
            basis  = empty( degree+1, dtype=float )
            basis_funs( knots, degree, x[i], span, basis )
            
            y[i]=0.0
            for j in range(degree+1):
                y[i]+=coeffs[span-degree+j]*basis[j]
    elif (der==1):
        for i in range(len(x)):
            span  =  find_span( knots, degree, x[i] )
            basis  = empty( degree+1, dtype=float )
            basis_funs( knots, degree, x[i], span, basis )
            basis_funs_1st_der( knots, degree, x[i], span, basis )
            
            y[i]=0.0
            for j in range(degree+1):
                y[i]+=coeffs[span-degree+j]*basis[j]
    return y

@types('double','double','double[:]','int','double[:]','int','double[:,:]','int','int')
def eval_spline_2d_scalar(x,y,kts1,deg1,kts2,deg2,coeffs,der1=0,der2=0):
    span1  =  find_span( kts1, deg1, x )
    span2  =  find_span( kts2, deg2, y )
    
    from numpy      import empty
    basis1  = empty( deg1+1, dtype=float )
    basis2  = empty( deg2+1, dtype=float )
    if (der1==0):
        basis_funs( kts1, deg1, x, span1, basis1 )
    elif (der1==1):
        basis_funs_1st_der( kts1, deg1, x, span1, basis1 )
    if (der2==0):
        basis_funs( kts2, deg2, y, span2, basis2 )
    elif (der2==1):
        basis_funs_1st_der( kts2, deg2, y, span2, basis2 )
    
    theCoeffs = empty([deg1+1,deg2+1])
    theCoeffs[:,:] = coeffs[span1-deg1:span1+1,span2-deg2:span2+1]
    
    z = 0.0
    for i in range(deg1+1):
        theCoeffs[i,0] = theCoeffs[i,0]*basis2[0]
        for j in range(1,deg2+1):
            theCoeffs[i,0] += theCoeffs[i,j]*basis2[j]
        z+=theCoeffs[i,0]*basis1[i]
    return z


@types('double[:]','double[:]','double[:]','int','double[:]','int','double[:,:]','double[:]','int','int')
def eval_spline_2d_vector(x,y,kts1,deg1,kts2,deg2,coeffs,z,der1=0,der2=0):
    from numpy      import empty
    theCoeffs = empty([deg1+1,deg2+1])
    if (der1==0):
        if (der2==0):
            for i in range(len(x)):
                span1  =  find_span( kts1, deg1, x[i] )
                span2  =  find_span( kts2, deg2, y[i] )
                basis1  = empty( deg1+1, dtype=float )
                basis2  = empty( deg2+1, dtype=float )
                basis_funs( kts1, deg1, x[i], span1, basis1 )
                basis_funs( kts2, deg2, y[i], span2, basis2 )
                
                theCoeffs[:,:] = coeffs[span1-deg1:span1+1,span2-deg2:span2+1]
                
                z[i] = 0.0
                for j in range(deg1+1):
                    theCoeffs[j,0] = theCoeffs[j,0]*basis2[0]
                    for k in range(1,deg2+1):
                        theCoeffs[j,0] += theCoeffs[j,k]*basis2[k]
                    z[i]+=theCoeffs[j,0]*basis1[j]
        elif(der2==1):
            for i in range(len(x)):
                span1  =  find_span( kts1, deg1, x[i] )
                span2  =  find_span( kts2, deg2, y[i] )
                basis1  = empty( deg1+1, dtype=float )
                basis2  = empty( deg2+1, dtype=float )
                basis_funs( kts1, deg1, x[i], span1, basis1 )
                basis_funs_1st_der( kts2, deg2, y[i], span2, basis2 )
                
                theCoeffs[:,:] = coeffs[span1-deg1:span1+1,span2-deg2:span2+1]
                
                z[i] = 0.0
                for j in range(deg1+1):
                    theCoeffs[j,0] = theCoeffs[j,0]*basis2[0]
                    for k in range(1,deg2+1):
                        theCoeffs[j,0] += theCoeffs[j,k]*basis2[k]
                    z[i]+=theCoeffs[j,0]*basis1[j]
    elif (der1==1):
        if (der2==0):
            for i in range(len(x)):
                span1  =  find_span( kts1, deg1, x[i] )
                span2  =  find_span( kts2, deg2, y[i] )
                basis1  = empty( deg1+1, dtype=float )
                basis2  = empty( deg2+1, dtype=float )
                basis_funs_1st_der( kts1, deg1, x[i], span1, basis1 )
                basis_funs( kts2, deg2, y[i], span2, basis2 )
                
                theCoeffs[:,:] = coeffs[span1-deg1:span1+1,span2-deg2:span2+1]
                
                z[i] = 0.0
                for j in range(deg1+1):
                    theCoeffs[j,0] = theCoeffs[j,0]*basis2[0]
                    for k in range(1,deg2+1):
                        theCoeffs[j,0] += theCoeffs[j,k]*basis2[k]
                    z[i]+=theCoeffs[j,0]*basis1[j]
        elif(der2==1):
            for i in range(len(x)):
                span1  =  find_span( kts1, deg1, x[i] )
                span2  =  find_span( kts2, deg2, y[i] )
                basis1  = empty( deg1+1, dtype=float )
                basis2  = empty( deg2+1, dtype=float )
                basis_funs_1st_der( kts1, deg1, x[i], span1, basis1 )
                basis_funs_1st_der( kts2, deg2, y[i], span2, basis2 )
                
                theCoeffs[:,:] = coeffs[span1-deg1:span1+1,span2-deg2:span2+1]
                
                z[i] = 0.0
                for j in range(deg1+1):
                    theCoeffs[j,0] = theCoeffs[j,0]*basis2[0]
                    for k in range(1,deg2+1):
                        theCoeffs[j,0] += theCoeffs[j,k]*basis2[k]
                    z[i]+=theCoeffs[j,0]*basis1[j]
