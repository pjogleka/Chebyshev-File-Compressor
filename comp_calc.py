import numpy as np
from scipy.interpolate import interp1d


def normalize(alt_vals):

    a = alt_vals[0]
    b = alt_vals[-1]
    scale = (b - a)/2
    translation = (a + b)/2
    alt_vals_norm = (alt_vals - translation) / scale
    return alt_vals_norm


def cheb_calc(file_type, alt_vals_norm, cs, N):
    '''Calculate Chebyshev values and errors'''
    
    # Get Chebyshev nodes (real component of 2N roots of unity in [0, pi]) and their approximate corresponding frequency values
    cheb_nodes = np.cos(np.arange(N + 1) * np.pi / N)
    cheb_vals = cs(cheb_nodes)
    
    # Get Chebyshev coefficients (pg. 13 chebfun 01)
    DFT = np.fft.fft(np.hstack((cheb_vals, cheb_vals[N - 1: 0: -1]))).real
    cheb_coeff = DFT[:N+1] / N
    cheb_coeff[0] /= 2
    cheb_coeff[-1] /= 2
    cheb_coeff = np.around(cheb_coeff, decimals = 6)
    
    # Get Chebyshev approximation values at grid points
    cheb_approx = np.exp(np.polynomial.chebyshev.chebval(alt_vals_norm, cheb_coeff))

    return cheb_coeff, cheb_approx


def get_error(freq_vals, cheb_approx):
    
    error = freq_vals - cheb_approx
    rel_err = np.abs(error) / freq_vals * 100
    max_rel_err = np.max(rel_err)
    return max_rel_err


def find_N(file_type, alt_vals_norm, freq_vals, cs, cutoff, tol):
    '''Iteratively find suitable interpolant, finding minimal degree approximant within error tolerance'''
    
    # Initialize N and error
    N = 1
    max_rel_err = tol + 1

    # Step through values of N until error is below tolerance
    while max_rel_err >= tol:
        N += 15
        if N >= cutoff + 15:
            break
        cheb_coeff, cheb_approx = cheb_calc(file_type, alt_vals_norm, cs, N)
        max_rel_err = get_error(freq_vals, cheb_approx)
    
    # Reduce N until error is right above tolerance
    while max_rel_err < tol:
        N -= 1
        cheb_coeff, cheb_approx = cheb_calc(file_type, alt_vals_norm, cs, N)
        max_rel_err = get_error(freq_vals, cheb_approx)

    # Set N to highest acceptable value
    N += 1
    cheb_coeff, cheb_approx = cheb_calc(file_type, alt_vals_norm, cs, N)
    
    # Abandon compression if futile
    flag = False
    if N + 1 > cutoff:
        cheb_coeff = freq_vals
        flag = True
    
    return flag, cheb_coeff, cheb_approx


def freq_adjust(freq_vals):
    '''Replace zeros with small value to avoid log error'''
    return np.array([1e-6 if x == 0 else x for x in freq_vals])


def interp_data(alt_vals_norm, freq_vals):
    '''Approximate frequency values at Chebyshev nodes'''
    return interp1d(alt_vals_norm, freq_vals)


def get_cheb_data(file_type, alt_vals, freq_vals, tol):
    '''Calculate Chebyshev interpolation for data'''

    # Find repeat "tail" values to encode
    repeats = np.where(freq_vals == freq_vals[0])
    consecutive_repeats = np.split(repeats, np.where(np.diff(repeats) != 1)[0] + 1)[0][0]
    huff = (len(consecutive_repeats) - 1, freq_vals[0])
    
    # Interpolate from end of tail onwards
    freq_vals = freq_vals[len(consecutive_repeats) - 1:]
    alt_vals = alt_vals[len(consecutive_repeats) - 1:]
    
    freq_vals = freq_adjust(freq_vals)
    alt_vals_norm = normalize(alt_vals)
    
    cs = interp_data(alt_vals_norm, np.log(freq_vals))
    
    # Return Chebyshev information and metrics
    cutoff = 0.8 * np.size(alt_vals)
    flag, cheb_coeff, cheb_approx = find_N(file_type, alt_vals_norm, freq_vals, cs, cutoff, tol)

    return huff, flag, cheb_coeff, cheb_approx