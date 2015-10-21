
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

# %% load data
fname = '10 Second Noise Test - Data.csv'  #inputs shorted to each other
#fname = '2 Seconds Test Signal - Data.csv'
fname = 'armData2.csv'
fname = 'armData3-HeartBeat.csv'
data = np.genfromtxt (fname, delimiter=",")
#names = ['Chan 0', 'Chan 1']


#keep only some of the data
nchan = data.shape[1]
if 1:
    data = data[:,0]
    nchan=1;
    #names = names[0]

# scale the data
#scale_counts_to_uV = 3.0/(2.0**32) * 1.0e6 
inamp_gain = np.array([80.0, 80.0])  #assumed for his inamp
adc_gain = 1
#scale_counts_to_uV = 1e6 * (1.2) / (2**(24-1) * inamp_gain * adc_gain * 1.5)  #MCP3912 data sheet, plus gain of preceeding INAMP
#data_uV = data * scale_counts_to_uV
data_uV = data


# make the time vector
fs_Hz = 244.14
t_sec = np.arange(data.shape[0]) / fs_Hz

# %% Filter
from scipy import signal

#add colum
data_uV = np.column_stack((data_uV,data_uV))

# BP filter the data to remove DC and high frequencies
bp_cutoff_Hz = np.array([1.0, 50.0])
b, a = signal.butter(4, bp_cutoff_Hz/(fs_Hz / 2.0), 'bandpass')  # define the filter
data_uV[:,-1]=signal.lfilter(b, a, data_uV[:,-1], 0)  # apply along the zeroeth dimension


# notch filter the data to remove 60 Hz and 120 Hz
notch_freq_Hz = np.array([60.0])  # these are the center frequencies
for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each center freq
    bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
    b, a = signal.butter(3, bp_stop_Hz/(fs_Hz / 2.0), 'bandstop')  # create the filter
    data_uV[:,-1] = signal.lfilter(b, a, data_uV[:,-1], 0)  # apply along the zeroeth dimension
    
nchan = data_uV.shape[1]
names = ["Raw", "Filtered"]

filt_txt = "BP = [" + str(bp_cutoff_Hz[0]) + ", " + str(bp_cutoff_Hz[1]) + "] Hz"
filt_txt = filt_txt + "\nNotch at " + str(notch_freq_Hz[0]) + "Hz"

# %% plots
plt.figure(figsize=[12,8])
nrow = 2
ncol = 2
for Ichan in range(nchan):

    # which data to plot
    foo_data = np.array(data_uV[:,Ichan])
    foo_data[np.isnan(foo_data)]=0.0

    #time domain plot
    ax = plt.subplot(nrow,ncol,Ichan*ncol+1)
    plt.plot(t_sec,foo_data)
    plt.xlim([t_sec[0], t_sec[-1]])
    plt.xlim([2, 8])
    plt.title(fname + ", " + names[Ichan])
    plt.ylabel("Voltage (uV)")
    plt.xlabel("Time (sec)")
    txt = "InAmp Gain = " + str(inamp_gain[Ichan]) + '\nADC Gain = ' + str(adc_gain)
    ax.text(0.97, 0.95,
        txt + '\nStddev = ' + "{:.1f}".format(np.std(foo_data)) +'uV',
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        backgroundcolor='w')   
    
    ax.text(0.03, 0.95,
        filt_txt,
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='left',
        backgroundcolor='w')  


   
    #compute average spectrum
    NFFT=128*2
    overlap = (7*NFFT) / 8
    #foo_data = foo_data - np.mean(foo_data,0) # helps remove DC bleed into the low-freq bins
    PSDperHz, freqs, t = mlab.specgram(foo_data,
                               NFFT=NFFT,
                               window=mlab.window_hanning,
                               Fs=fs_Hz,
                               noverlap=overlap) # returns PSD power per Hz
    PSDperHz = np.mean(PSDperHz,1)     #average the multiple spectra into a single spectrum
    PSDperBin = PSDperHz * fs_Hz / float(NFFT)  #convert to "per bin"

    #plot spectrum
    ax = plt.subplot(nrow,ncol,Ichan*ncol+2)
    if 1:
        #plot as PSD per Hz...good for assessing the amplitude of the background noise
        plt.plot(freqs,10.0*np.log10(PSDperHz))
        plt.ylabel("PSD per Hz (dB re: 1uV)")
        #plt.ylim([-20, 70])
        plt.ylim([0, 90])
    else:
        #plot as PSD per bin...good for assessing the amplitude of the sine wave
        plt.plot(freqs,10.0*np.log10(PSDperHz))
        plt.ylabel("PSD per Hz (dB re: 1uV)")        
    plt.xlim([0,fs_Hz/2.0])
    plt.title(fname + ", " + names[Ichan])
    plt.xlabel("Frequency (Hz)")
    
    # add annotation for FFT Parameters
    ax.text(0.97, 0.95,
        txt + '\nNFFT = ' + str(NFFT) + "\nfs = " + str(int(fs_Hz)) + " Hz",
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        backgroundcolor='w')
        
    ax.text(0.03, 0.05,
        filt_txt,
        transform=ax.transAxes,
        verticalalignment='bottom',
        horizontalalignment='left',
        backgroundcolor='w')  

plt.tight_layout()
plt.savefig('FIGs\\' + fname[1:-4] + '.png') 

