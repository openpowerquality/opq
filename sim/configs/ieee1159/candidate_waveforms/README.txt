This directory contains candidate waveforms that match classifications from the  IEEE1159 standard.

The file naming convention is as follows:

[sag|swell]_[padding samples]_[anomaly samples]_[pu]

Where [padding samples] is the number of samples of nominal on either side of the anomaly and [anomaly samples] is the
duration of the anomaly in samples and [pu] is "per unit" as defined in IEEE1159. In our case 120V=1.0pu.

It may be helpful to remember that 1 cycle = 200 samples and 1 second = 60 cycles.

Each waveform contains signed 16-bit integers.

Each waveform has 1/10th second (1200 samples) of steady state/nominal on either side.

Each .txt file contains an ASCII representation of the waveform where each sample is separated by new lines "\n".

Each .png file contains a plot of the waveform produced with gnuplot.

Every state change is delayed 400 samples (2 cycles) so they appear smoother rather than abrupt.

Each waveform has already been stored to mongodb's gridfs as raw bytes representing signed 16-bit integers using the
file naming convention discussed above (no file extensions).

The calibration constant associated with these waveforms is 152.0.

The following is a list of file names to info:

sag_1200_5000_0.9    Instantaneous sag, 25 cycles, 108v
sag_1200_5000_0.5    Instantaneous sag, 25 cycles, 60v
sag_1200_5000_0.1    Instantaneous sag, 25 cycles, 12v
swell_1200_5000_1.1  Instantaneous swell, 25 cycles, 132v
swell_1200_5000_1.4  Instantaneous swell, 25 cycles, 168v
swell_1200_5000_1.8  Instantaneous swell, 25 cycles, 228v
sag_1200_30000_0.09  Momentary interruption, 2.5s,  10.8v
sag_1200_30000_0.01  Momentary interruption, 2.5s,  1.2v
sag_1200_30000_0.9   Momentary sag, 2.5s, 108v
sag_1200_30000_0.5   Momentary sag, 2.5s, 60v
sag_1200_30000_0.1   Momentary sag, 2.5s, 12v
swell_1200_30000_1.1 Momentary swell, 2.5s, 132v
swell_1200_30000_1.4 Momentary swell, 2.5s, 168v
swell_1200_30000_1.8 Momentary swell, 2.5s, 228v
sag_1200_60000_0.09  Temporary interruption, 5s,  10.8v
sag_1200_60000_0.01  Temporary interruption, 5s,  1.2v
sag_1200_60000_0.9   Temporary sag, 5s, 108v
sag_1200_60000_0.5   Temporary sag, 5s, 60v
sag_1200_60000_0.1   Temporary sag, 5s, 12v
swell_1200_60000_1.1 Temporary swell, 5s, 132v
swell_1200_60000_1.4 Temporary swell, 5s, 168v
swell_1200_60000_1.8 Temporary swell, 5s, 228v