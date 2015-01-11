import numpy as np
import pandas as pd

def scan_to_df(npz,num_subchannels=128,sampling_freq=1.024e6,samples_to_trim=2048):
    d = np.load(npz)
    num_tunings = d['freqs'].shape[0]
    subchannel_offsets = sampling_freq*np.fft.fftshift(np.fft.fftfreq(num_subchannels))
    window = np.hamming(num_subchannels)
    frames = []
    for k in range(num_tunings):
        data = d['scales'][k]*(d['data_r'][k,:]+1j*d['data_i'][k,:])
        data = data[samples_to_trim:]
        data = data - data.mean()
        ff = np.abs(np.fft.fftshift(np.fft.fft(window*data.reshape((-1,num_subchannels)),axis=1)))**2
        tp = ff.sum(0)
        sk = (ff.shape[0]/2.0)*(ff**2).sum(0)/(tp**2)
        nspec = ff.shape[0]
        tp = tp/nspec
        f0 = d['freqs'][k]
        freqs = subchannel_offsets + f0
        timestamp = d['timestamps'][k]*np.ones(freqs.shape)
        frames.append(pd.DataFrame(dict(timestamp=timestamp,freq=freqs,skurtosis=sk,total_power=tp,nspec=nspec)))
    df = pd.concat(frames,ignore_index=True)
    d.close()
    return df

def process_files(fns):
    dfs = []
    for scan_num,fn in enumerate(fns):
        df = scan_to_df(fn)
        df['scan_num'] = scan_num
        df['scan_filename'] = fn
        dfs.append(df)

    dfs = pd.concat(dfs,ignore_index=True)
    return dfs

def load_archive(fn):
    npa = np.load(fn)
    df = pd.DataFrame.from_records(npa)
    return df
