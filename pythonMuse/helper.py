import numpy as np
from scipy import fft as spfft
from scipy.signal import lfilter
from scipy.signal import cheby1
from scipy.signal import lfilter


def is_data_valid(data, timestamps):
    if timestamps == 0.0:
        return False
    if all(data == 0.0):
        return False
    return True


def PPG_error(Exceptions):
    pass  # Not implemented yet


def doMuseFFT(toFFT, sRate):
    lengthFFT = toFFT.shape[0]
    resolution = sRate / lengthFFT
    frequenciesToKeep = 60

    binWidth = int(np.ceil(1 / resolution))
    numBins = int(np.floor(frequenciesToKeep / binWidth))

    coefficients = np.fft.fft(toFFT, axis=0)
    coefficients = coefficients / lengthFFT
    coefficients = np.abs(coefficients)
    coefficients = coefficients[1:frequenciesToKeep + 1] * 2

    coefficients = np.reshape(coefficients, [numBins, binWidth, toFFT.shape[1]])
    coefficients = np.mean(coefficients, axis=1)

    return coefficients

def doMuseFilteredPlot(toFiltered, filter, filterLength):
    numSensors = toFiltered.shape[1] # Expected=4

    if filter == 'Average':
        for i in range(numSensors):
            toFiltered[:,i] = np.convolve(toFiltered[:,i], np.ones(filterLength)/filterLength, mode='same') # Moving averate filter. Source: https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
    elif filter == 'Lowpass': # Source: https://stackoverflow.com/questions/46784822/low-pass-chebyshev-type-i-filter-with-scipy
        
        # Prepare filter parameters
        fs = 256 # Double check this sampling rate
        order = 5
        Apass = 0.001
        fcut = 50 # Cutoff frequency
        wn = 2*fcut/fs

        # Create Chebyshev filter
        b, a = cheby1(order, Apass, wn)

        # Calculate filtered input
        toFiltered = lfilter(b, a, toFiltered)
    else:
        raise ValueError('doMuseFilteredPlot: Filter not found.')

    return toFiltered

def doMuseWavelet(toWavelet, sRate, frequencySteps, minimumFrequency, maximumFrequency):
    mortletParameter = [6]
    samplingRate = sRate

    frequencyResolution = np.linspace(start=minimumFrequency, stop=maximumFrequency, num=frequencySteps)  # linear scale
    s = np.divide(
        np.logspace(start=np.log10(mortletParameter[0]), stop=np.log10(mortletParameter[-1]), num=frequencySteps), (
                2 * np.pi * frequencyResolution))
    waveletTime = np.arange(start=-2, stop=2, step=1 / samplingRate)

    lengthWavelet = waveletTime.shape[0] + 1
    middleWavelet = int((lengthWavelet - 1) / 2)

    lengthData = toWavelet.shape[0]

    lengthConvolution = lengthWavelet + lengthData - 1

    waveletData = np.zeros([toWavelet.shape[1], frequencyResolution.shape[0], toWavelet.shape[0]])
    for channelCounter in range(toWavelet.shape[1]):

        channelData = toWavelet[:, channelCounter]
        fftData = spfft.fft(channelData, lengthConvolution)
        timeFrequencyData = np.zeros([toWavelet.shape[0], frequencyResolution.shape[0]])

        for fi in range(frequencyResolution.shape[0]):
            wavelet = np.multiply(
                np.exp(2 * (0 + 1j) * np.pi * frequencyResolution[fi] * waveletTime),
                np.exp(-waveletTime ** 2 / (2 * s[fi] ** 2)))

            fftWavelet = spfft.fft(wavelet, lengthConvolution)
            fftWavelet = fftWavelet / np.max(fftWavelet)

            waveletOutput = spfft.ifft(np.multiply(fftWavelet, fftData))

            waveletOutput = waveletOutput[middleWavelet:-middleWavelet]

            timeFrequencyData[:, fi] = np.abs(waveletOutput)

        waveletData[channelCounter, :, :] = timeFrequencyData.T
    return waveletData
