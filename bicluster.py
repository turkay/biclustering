'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import numpy
import random
import operator
import time
from math import *

#A, k, m rows
#B, l, n cols

ITERATIONS = 1000
SIZE = 1000
SHAPE = ( SIZE, SIZE )

# Populate a test matrix with gaussian noise in (0,1)
X = numpy.random.normal( size=SHAPE )
X += 2
X *= 0.5

# Add a feature to detect
FEATURE = numpy.zeros( SHAPE )
FEATURE[0:SIZE/2,0:SIZE/2] = 4
X += FEATURE

m, n = X.shape

# Select initial k and l from {1...[m/2]} and {1...[n/2]} respectively (at random)
def get_k_and_l( m, n ):
    k = random.randint( 1, int( m/2 ) )
    l = random.randint( 1, int( n/2 ) )
    return ( k, l )

def get_initial_B( l, n, X ):
    l_zeros = numpy.zeros( ( 1, l ), dtype=int )
    l_rands = numpy.random.random( ( 1, l ) )
    l_rands *= n
    l_zeros += l_rands
    which_l_cols = l_zeros
    B = numpy.zeros( X.shape )
    for i in which_l_cols:
        B[:,i] = X[:,i]
    return B
       
def get_initial_B_inds( l, n, X ):
    l_zeros = numpy.zeros( ( 1, l ), dtype=int )
    l_rands = numpy.random.random( ( 1, l ) )
    l_rands *= n
    l_zeros += l_rands
    return l_zeros

def get_A_from_row_indicies( rows, X ):
    A = numpy.zeros( X.shape )
    for row in rows:
        A[row,:] = X[row,:]
    return A

def get_l_cols_with_largest_sum_over_A( l, A_rows, X ):
    sums = [ ]
    for row in A_rows:
        sums.append( sum( X[row,:] ) )

    # Col indicies sorted from lowest to highest:
    inds = [ i for ( i, j ) in sorted( enumerate( sums ), key = operator.itemgetter( 1 ) ) ]
    return inds[-l:]

def get_k_rows_with_largest_sum_over_B( k, B_cols, X ):
    sums = [ ]
    for col in B_cols:
        sums.append( sum( X[:,col] ) )

    # Row indicies sorted lowest to highest:
    inds = [ i for ( i, j ) in sorted( enumerate( sums ), key = operator.itemgetter( 1 ) ) ]
    best_rows = inds[-k:]
    return best_rows 

def get_B_from_col_indicies( cols, X ):
    B = numpy.zeros( X.shape )
    for col_index in cols:
        B[:,col_index] = X[:,col_index]
    return B

def have_converged( newA, newB, oldA, oldB ):
    a_converged = ( sum( oldA ) - sum( newA ) ).all( ) == 0 
    b_converged = ( sum( oldB ) - sum( newB ) ).all( ) == 0 
    if a_converged and b_converged:
        return True
    else:
        return False

def inds_have_converged( new_a_inds, new_b_inds, old_a_inds, old_b_inds ):
    a_converged = ( set( new_a_inds ) == set( old_a_inds ) )
    b_converged = ( set( new_b_inds ) == set( old_b_inds ) )
    if a_converged and b_converged:
        return True
    else:
        return False

def get_intersection( A, B ):
    intersection = numpy.zeros( A.shape )
    C = A * B
    indicies = C.nonzero( )
    intersection[ indicies ] = A[ indicies ]
    return intersection

def binomial( n, k ):
    if n > k:
        return factorial( n ) / ( factorial( k ) * factorial( n - k ) )

def S( U, k, l, m, n ):
    tau = numpy.average( U )

    first_term  = -log( binomial( m, k ) * binomial( n, l ), 2 )
    second_term = ( ( tau**2.0 ) * k * l ) / ( 2.0 * log( 2.0 ) )
    third_term  = -log( ( tau**2.0 * k * l ), 2 ) / 2.0

    return log( 2.0 ) * ( first_term + second_term + third_term ) 
        
def get_intersection_inds( rows, cols ):
    A = get_A_from_row_indicies( rows, X )
    B = get_B_from_col_indicies( cols, X )
    return get_intersection( A, B )


def get_remaining_time( start_time, total_time, iteration ):
    if iteration == 0:
        return ""
    elapsed_time = total_time - start_time
    time_per_iteration = elapsed_time / iteration
    return str( time_per_iteration * ( ITERATIONS - iteration ) / 60 ) + " minutes remaining"

def get_n_randoms_from_list( n, mylist ):
    out = [ ]
    for i in range( n ):
        pos = random.randrange( len( mylist ) )
        elem = mylist[ pos ]
        mylist[pos] = mylist[-1]
        del mylist[-1]
        out.append( elem )
    return out
    

if __name__ == '__main__':
    winner        = numpy.zeros( X.shape )
    winning_score = 0 
    end_time      = False
    start_time    = time.time( )
    for it in range( 0, ITERATIONS ):
        print it
        k, l  = get_k_and_l( m, n )
        b_inds = get_n_randoms_from_list( l, range( X.shape[ 1 ] ) )
        last_a_inds = [ ]
        last_b_inds = [ ]
        while True: 
            a_inds = get_k_rows_with_largest_sum_over_B( k, b_inds, X )
            b_inds = get_l_cols_with_largest_sum_over_A( l, a_inds, X )
            if inds_have_converged( a_inds, b_inds, last_a_inds, last_b_inds ):
                break
            last_a_inds = a_inds
            last_b_inds = b_inds
        U = get_intersection_inds( a_inds, b_inds )
        U_score = S( U, k, l, m, n )
        if U_score > winning_score:
            winner = U.copy( )
            winning_score = U_score
        print get_remaining_time( start_time, time.time( ), it )
    
    print winning_score
    print winner
