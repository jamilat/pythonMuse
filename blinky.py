#!/usr/bin/python
# MASTERFILE for blink detection project

from pythonMuse.Muse import Muse
import matplotlib;
import sys
import re
from gpiozero import LED

# constants used for data view modes
wave = 1
fft = 2
wavelet = 3
    
matplotlib.use("TkAgg")  # This option may or may not be needed according to your OS and Python setup (Ipython...)
# See this link for further details: https://stackoverflow.com/questions/7156058/matplotlib-backends-do-i-care
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.interactive(False)  # This option may or may not be needed according to your OS and Python setup (Ipython...)
def getModes(d):
    if 'museName' not in d:
        d['museName'] = 'Muse-C87E'
    if 'plotWhat' not in d:
        d['plotWhat'] = 1
    if 'plotUpdateInterval' not in d:
        d['plotUpdateInterval'] = 100
    if "plotLength" not in d:
        d['plotLength'] = 512  # Length of the plot (in samples). For a 2 second plot, set this variable to be sampleRate*2
    if 'sampleRate' not in d:
        d['sampleRate'] = 256
    return d

def connectMuse(museObj):
    for i in range(10):
        print("Attempting to find " + museObj.target_name + ". Attempt " + str(i + 1) + " of 10...")
        r = museObj.connect()  # Returns none if not found
        if r is not None:  # If found
            batt = r.pullBattery()  # Get battery information from the Muse
            print('Muse Battery is ' + str(batt))  # Print battery level
            break  # Get out of the for loop
        else:  # Muse not found
            print("No MUSE found, trying again...")
    # TODO: throw exception if muse not found

def plotMuse(d):
    fig = plt.figure()  # Open an empty figure
    fig.canvas.mpl_connect('close_event', close_handle)  # Close_handle will be called upon closing the window

    # Adding four subplots (note the indexing, 3,1,2,4)
    global ax1, ax2, ax3, ax4
    ax1 = fig.add_subplot(2, 2, 3)
    ax2 = fig.add_subplot(2, 2, 1)
    ax3 = fig.add_subplot(2, 2, 2)
    ax4 = fig.add_subplot(2, 2, 4)

    if d['plotWhat'] == 1:  # If plot wave is selected
        # FuncAnimation function runs animateEEG every plotUpdateInterval (ms)
        ani = animation.FuncAnimation(fig, animateEEG, interval=d['plotUpdateInterval'])
        plt.show()

def animateEEG(i):  # A function to plot EEG, this will be called every "plotUpdateInterval" ms by FuncAnimation
    muse.updateBuffer()  # Pulls a chunk of EEG data from MUSE hardware, filters them (if applicable) and
    # updates the internal variables. The next line gets these new values.
    #plotX, plotBuffer = muse.getPlot()  # Get timestamps (first output) and (filtered, if applicable) EEG data.
    plotX, plotBuffer = muse.getFilteredPlot('Average', 15)

    if muse.getBlinks(plotBuffer):
        blink_led.on()
    else:
        blink_led.off()

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

if __name__ == "__main__":
    modeDict = {}
    for arg in sys.argv:
        m = re.search('(.*)=(.*)', arg)
        if m is not None:
            print(m[0], m[1], m[2])
            modeDict[m[1]] = m[2]

    modeDict = getModes(modeDict)

    # Cutoff frequencies for low/high pass and the notch band-stop filters. Set to -1 to skip the filter
    highFreq = 0.1
    lowFreq = 30
    notchFreq = 60
    filterOrder = 5  # Butterworth filter order for low/high pass filters
    # (see:https://en.wikipedia.org/wiki/Butterworth_filter)

    # Define RPi Pins
    blink_led = LED(26)

    # Here we create the main object from Muse class. This object (muse) will be used for pulling eeg, plotting, ...
    muse = Muse(target_name=modeDict['museName'], plotLength=modeDict['plotLength'], sampleRate=modeDict['sampleRate'], highPassFreq=highFreq,
                lowPassFreq=lowFreq, notchFreq=notchFreq, filterOrder=filterOrder)

    # Attempting to find and connect to the target MUSE, will retry 10 times.
    connectMuse(muse)
    plotMuse(modeDict)
    