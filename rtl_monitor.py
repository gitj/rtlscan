# -*- coding: utf-8 -*-
"""
Created on Thu Jan 08 21:42:44 2015
"""

import numpy as np
import rtlsdr
import time

gain = 26.0
nsamp = 2**16
freqs = np.arange(400e6,500e6,1e6)

sdr = rtlsdr.RtlSdr()
sdr.gain = gain
sdr.sample_rate = 1.024e6

nscans = 0
while nscans < 100:
    data_r = []
    data_i = []
    timestamps = []
    scales = []
    tic = time.time()
    for freq in freqs:
        sdr.center_freq = freq
        raw = sdr.read_samples(nsamp)
        timestamps.append(time.time())
        scale = raw.real.ptp()
        scales.append(scale)
        raw = 2**8*raw/scale
        data_r.append(raw.real.astype('int8'))
        data_i.append(raw.imag.astype('int8'))
    print "completed scan %d in %.1f seconds" % (nscans, (time.time()-tic))
    tic = time.time()
    np.savez(time.strftime('/data/%Y-%m-%d_%H%M%S.npz'), data_r = np.vstack(data_r),
             data_i = np.vstack(data_i), freqs=freqs, timestamps = np.array(timestamps),
             scales = np.array(scales))
    print "saved in %.1f seconds" % (time.time()-tic)
    nscans += 1
        
