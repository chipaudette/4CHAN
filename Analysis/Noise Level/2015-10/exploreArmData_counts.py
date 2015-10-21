
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import os

# %% load data
#fname = '10 Second Noise Test - Data.csv'  #inputs shorted to each other
#fname = '2 Seconds Test Signal - Data.csv'
#fname = 'armData2.csv'
#fname = 'armData3-HeartBeat.csv'
#fname = 'armData3-HB-counts.csv'
#fname = 'armData4-HB-wCaps.csv'
pname = 'Data'
fs1_Hz = 256.0
fs2_Hz = 512.0
data_set = 4
if (data_set == 1):
    fs_Hz = fs1_Hz
    fname = 'Ganglion Data - Channels & Ref tied to DRL 01.csv';
    sname = 'Ganglion, Chan+Ref to DRL, Test 1'
    inamp_gain = np.array([160.0, 160.0, 80.0, 80.0])  #assumed for his inamp
elif (data_set == 2):
    fs_Hz = fs1_Hz
    fname = 'Ganglion Data - Channels & Ref tied to DRL 02.csv';
    sname = 'Ganglion, Chan+Ref to DRL, Test 2'
    inamp_gain = np.array([160.0, 160.0, 80.0, 80.0])  #assumed for his inamp   
elif (data_set == 2.1):
    fs_Hz = fs1_Hz
    fname = 'Ganglion Data - Channels & Ref tied to DRL 02b.csv';
    sname = 'Ganglion, Chan+Ref to DRL, Test 2(b)'
    inamp_gain = np.array([160.0, 160.0, 80.0, 80.0])  #assumed for his inamp   
elif (data_set == 3):
    fs_Hz = fs1_Hz
    fname = 'Ganglion Data - Channels & Ref tied to DRL 03.csv';
    sname = 'Ganglion, Chan+Ref to DRL, Test 3'
    inamp_gain = np.array([80.0, 80.0, 80.0, 80.0])  #assumed for his inamp   
elif (data_set == 3.1):
    fs_Hz = fs1_Hz
    fname = 'Ganglion Data - Channels & Ref tied to DRL 03b.csv';
    sname = 'Ganglion, Chan+Ref to DRL, Test 3(b)'
    inamp_gain = np.array([80.0, 80.0, 80.0, 80.0])  #assumed for his inamp    
elif (data_set == 4):
    fs_Hz = fs2_Hz
    fname = 'Ganglion Data - Channels & Ref teid to DRL 04.csv';
    sname = 'Ganglion, Chan+Ref to DRL, Test 4'
    inamp_gain = np.array([80.0, 80.0, 80.0, 80.0])  #assumed for his inamp      


data_counts = np.genfromtxt (os.path.join(pname,fname), delimiter=",")
#names = ['Chan 0', 'Chan 1']

#keep only some of the data
#nchan = data.shape[1]
nchan = 4
data_counts = data_counts[2:,1:(nchan+1)] #first column (col zero) is just a counter


#remove mean
if 0:
    data_counts = data_counts - np.mean(data_counts,0)


#reduce number of channels
if 0:
    ind = [0,1]
    data_counts = data_counts[:,ind]  #get just first column
    #inamp_gain = np.array([inamp_gain[ind]])
    inamp_gain = inamp_gain[ind]
    nchan = data_counts.shape[1]  #how many columns


# scale the data
#scale_counts_to_uV = 3.0/(2.0**32) * 1.0e6 
adc_gain = 1.0
scale_counts_to_uV = 1e6 * (1.2) / (2**(24-1) * inamp_gain * adc_gain * 1.5)  #MCP3912 data sheet, plus gain of preceeding INAMP
data_uV = data_counts * scale_counts_to_uV



# make the time vector
t_sec = np.arange(data_counts.shape[0]) / fs_Hz

# %% remove outliers
points_removed = np.zeros([data_uV.shape[0],1])
if (1):
    for Ichan in range(nchan):
        foo_data = np.array(data_uV[:,Ichan])
        mean_val = np.mean(foo_data,0)    
        std = np.std(foo_data)
        thresh = 5.0
        ind = np.where(abs(foo_data-mean_val) > thresh*std)
        points_removed[Ichan]=ind[0].size
        print(ind[0])
        print "Chan " + str(Ichan) + ": removing " + str(points_removed[Ichan]) + " points as outliers..."
        data_uV[ind,Ichan] = mean_val



# %% plots
nrow = 2
ncol = 2
plt_count = -1
page_count = 0;
for Ichan in range(nchan):
    plt_count = plt_count +1
    if (plt_count >= nrow):
        plt_count = 0
    if (plt_count == 0):
        plt.figure(figsize=[12,8])
        page_count=page_count+1
    

    # which data to plot
    foo_data = np.array(data_uV[:,Ichan])
    foo_data[np.isnan(foo_data)]=0.0

    #time domain plot
    ax = plt.subplot(nrow,ncol,plt_count*ncol+1)
    plt.plot(t_sec,foo_data)
    plt.xlim([t_sec[0], t_sec[-1]])
    #plt.xlim([2, 6])
    #plt.ylim(np.array([-10, 10])+np.mean(foo_data,0))
    plt.ylim(np.array([-2, 2])+np.mean(foo_data,0))
    plt.title("Chan " + str(Ichan) + ": " + sname)
    plt.ylabel("Voltage (uV)")
    plt.xlabel("Time (sec)")
    txt = "InAmp Gain = " + str(inamp_gain[Ichan]) + '\nADC Gain = ' + str(adc_gain)
    print "Chan " + str(Ichan) + ": stddev = " + "{:.3f}".format(np.std(foo_data)) +'uV'
    ax.text(0.97, 0.95,
        txt + '\nStddev = ' + "{:.2f}".format(np.std(foo_data)) +'uV',
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        backgroundcolor='w')   
    
#    ax.text(0.03, 0.95,
#        filt_txt,
#        transform=ax.transAxes,
#        verticalalignment='top',
#        horizontalalignment='left',
#        backgroundcolor='w')  


   
    #compute average spectrum
    #NFFT=128*2
    #NFFT = int(round(fs_Hz))
    NFFT = int(4.0*fs_Hz)
    overlap = (7*NFFT) / 8
    foo_data = foo_data - np.mean(foo_data,0) # helps remove DC bleed into the low-freq bins
    PSDperHz, freqs, t = mlab.specgram(foo_data,
                               NFFT=NFFT,
                               window=mlab.window_hanning,
                               Fs=fs_Hz,
                               noverlap=overlap) # returns PSD power per Hz
    PSDperHz = np.mean(PSDperHz,1)     #average the multiple spectra into a single spectrum
    PSDperBin = PSDperHz * fs_Hz / float(NFFT)  #convert to "per bin"

    #plot spectrum
    ax = plt.subplot(nrow,ncol,plt_count*ncol+2)
    if 1:
        #plot as PSD per Hz...good for assessing the amplitude of the background noise
        #plt.plot(freqs,10.0*np.log10(PSDperHz))
        #plt.xlim([0,fs_Hz/2.0])
        plt.loglog(freqs,np.sqrt(PSDperHz))
        plt.ylabel("PSD (uVrms/sqrt(Hz))")
        #plt.ylim([-20, 70])
        plt.ylim([0.001, 10])
        plt.xlim([0.001, 100]);
    else:
        #plot as PSD per bin...good for assessing the amplitude of the sine wave
        plt.plot(freqs,10.0*np.log10(PSDperHz))
        plt.ylabel("PSD per Hz (dB re: 1uV)")        
        plt.xlim([0,fs_Hz/2.0])

    plt.title("Chan " + str(Ichan) + ": " + sname)
    plt.xlabel("Frequency (Hz)")
    
    # add annotation for FFT Parameters
    ax.text(0.97, 0.95,
        txt + '\nNFFT = ' + str(NFFT) + "\nfs = " + str(int(fs_Hz)) + " Hz",
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        backgroundcolor='w')
        
#    ax.text(0.03, 0.97,
#        filt_txt,
#        transform=ax.transAxes,
#        verticalalignment='top',
#        horizontalalignment='left',
#        backgroundcolor='w')  

    if (plt_count == nrow-1):
        #save the figure
        plt.tight_layout()
        plt.savefig('FIGs\\' + fname[0:-4] + '_page' + str(page_count) + '.png') 


