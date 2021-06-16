#!/usr/bin/python
# MASTERFILE for blink detection project

from pythonMuse.Muse import Muse
import matplotlib;
import sys
import re

matplotlib.use("TkAgg")  # This option may or may not be needed according to your OS and Python setup (Ipython...)
# See this link for further details: https://stackoverflow.com/questions/7156058/matplotlib-backends-do-i-care
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.interactive(False)  # This option may or may not be needed according to your OS and Python setup (Ipython...)

def animateEEG(i):  # A function to plot EEG, this will be called every "plotUpdateInterval" ms by FuncAnimation
    muse.updateBuffer()  # Pulls a chunk of EEG data from MUSE hardware, filters them (if applicable) and
    # updates the internal variables. The next line gets these new values.
    plotX, plotBuffer = muse.getPlot()  # Get timestamps (first output) and (filtered, if applicable) EEG data.

    # Clear the plot scenes to update
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    # Plot the updated samples
    ax1.plot(plotX, plotBuffer[:, 0])
    ax2.plot(plotX, plotBuffer[:, 1])
    ax3.plot(plotX, plotBuffer[:, 2])
    ax4.plot(plotX, plotBuffer[:, 3])

    # Limit (and fix) the Y-axis of the plots for better representation.
    ax1.set_ylim(-1000, 1000)
    ax2.set_ylim(-1000, 1000)
    ax3.set_ylim(-1000, 1000)
    ax4.set_ylim(-1000, 1000)

def close_handle(evt):  # This function will be called when the plot window is closing
    print("disconnecting Muse")
    muse.disconnect()  # Disconnecting MUSE

if __name__ == "__main__":  # This function runs when you run this file (python example.py)
    # TODO: take cli
    #  museName, plotWhat, plotUpdateInterval, plotLength, sampleRate, highFreq, lowFreq, notchFreq, filterOrder
    print(sys.argv)

    museName = 'Muse-3BEA'  # target MUSE name.

    plotWhat = 3  # Choose what to plot, 1: wave, 2: FFT, 3: wavelet
    plotUpdateInterval = 100  # How often the plots should be updated
    plotLength = 512  # Length of the plot (in samples). For a 2 second plot, set this variable to be sampleRate*2

    sampleRate = 256  # The sample rate of the MUSE hardware

    # Cutoff frequencies for low/high pass and the notch band-stop filters. Set to -1 to skip the filter
    highFreq = 0.1
    lowFreq = 30
    notchFreq = 60
    filterOrder = 5  # Butterworth filter order for low/high pass filters
    # (see:https://en.wikipedia.org/wiki/Butterworth_filter)

    # Here we create the main object from Muse class. This object (muse) will be used for pulling eeg, plotting, ...
    muse = Muse(target_name=museName, plotLength=plotLength, sampleRate=sampleRate, highPassFreq=highFreq,
                lowPassFreq=lowFreq, notchFreq=notchFreq, filterOrder=filterOrder)

    # Attempting to find and connect to the target MUSE, will retry 10 times.
    for i in range(10):
        print("Attempting to find " + museName + ". Attempt " + str(i + 1) + " of 10...")
        r = muse.connect()  # Returns none if not found
        if r is not None:  # If found
            break  # Get out of the for loop
        else:  # Muse not found
            print("No MUSE found, trying again...")

    batt = muse.pullBattery()  # Get battery information from the Muse
    print('Muse Battery is ' + str(batt))  # Print battery level

    fig = plt.figure()  # Open an empty figure
    fig.canvas.mpl_connect('close_event', close_handle)  # Close_handle will be called upon closing the window

    # Adding four subplots (note the indexing, 3,1,2,4)
    ax1 = fig.add_subplot(2, 2, 3)
    ax2 = fig.add_subplot(2, 2, 1)
    ax3 = fig.add_subplot(2, 2, 2)
    ax4 = fig.add_subplot(2, 2, 4)

    if plotWhat == 1:  # If plot wave is selected
        # FuncAnimation function runs animateEEG every plotUpdateInterval (ms)
        ani = animation.FuncAnimation(fig, animateEEG, interval=plotUpdateInterval)
        plt.show()