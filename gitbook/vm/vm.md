# OPQ Virtual Machine

## Overview {#overview}

OPQ Virtual Machine is a virtual machine (VM) that comes preloaded with the entire OPQ software stack pre-configured and set to start at boot.

The VM also acts as a full system test bed and simulator. The VM contains a simulator that can simulate the raw waveform of OPQBoxes.

The VM runs on top of 64-bit Debian Linux.

## Installation {#installation}

_Note: Full installation may take upwards of 10 gigabytes of hard drive space._
1. Download and install the latest version of Virtual Box from https://www.virtualbox.org/wiki/Downloads
2. Download the latest OPQ VM image from our [Google Drive](https://drive.google.com/file/d/1TXWauNBatqtwpqR_RXMs2ZnAig8sG5Qz/view?usp=sharing)
3. Open Virtual Box, select `File` -> `Import Appliance...`
4. Find and select the OpqSim.ova file you downloaded in step 2.
5. Hit `Next` followed by `Import`. Importing can take a few moments...
6. You should now see OpqSim in your list of virtual machines.

## Running {#running}

1. Select the OpqSim virtual machine and press `Start`.
2. The machine will now boot. 
3. In general, you shouldn't need to log into the VM since the necessary services are already port forwarded via Virtual Box. However, should you need to log into the VM:
    1. Username is `pi` and password is `opq`.
    2. SSH into the machine with `ssh -p 3022 pi@localhost` or
    3. Log in through the GUI
    
### Interacting with the VM {#interactingvm}
Different services are preconfigured to be port forwarded to your local host from the VM. 

| Service    | Port  |
|------------|-------|
| SSH        | 3022  |
| MongoDB    | 27017 |
| OPQSim     | 8000  |
| Triggering | 28080 |

For example, to see the status of the triggering service, ensure the VM is running and then point your browser to http://localhost:28080 This page will show your the current state of what the triggering service is reading. 

The Mongo database can be connected directly as if it were local at port 27017.

### Interacting with the Simulator {#interactivingsim}

The [simulator](https://github.com/openpowerquality/opq/blob/master/sim/sim.py) boots with the VM and simulates a raw 16-bit signed integer waveform that represents the DAC measurements from an OPQBox.

At boot, the simulator will produce a nominal 60Hz sine wave at a perfect 120 Volts. The simulator state can be modified via HTTP POST requests. We provide low level and high level state modifications via filter definitions stored in JSON files.

#### Low level simulator manipulation

The following values define the state of the waveform being generated.

| Name           | Default Value | Notes |
|----------------|---------------|-------|
| amplitude      | 169.71        | Defines the amplitude of the sine wave. 167.71 = 120.0 Vrms |
| frequency      | 60.0          | The frequency in Hz of the generated wave. |
| sample_rate_hz | 12000.0       | The number of simulated samples per second |

The state of the waveform generator can be modified at any time by POSTing a JSON request to `http://localhost:8000`. The format of this type of request is

```
{
  "state": {
    "amplitude": 169.705627485,
    "frequency": 60.0,
    "phase": 0.0,
    "sample_rate_hz": 12000.0
  }
}
```

This example changes the amplitude, frequency, phase, and sample rate all at the same time. You should note that it's possible to only modify the values that you want and not all of them. For instance, if you wanted to generate a voltage swell, you could simply raise the amplitude:

```
{
  "state": {
    "amplitude": 200.0,
  }
}
```

#### High level simulator manipulation

We provide a higher level construct called filters that can be described using JSON and provide for automated control of the waveform generator. 


We currently support 2 filters, `nop` and `vrms`. We hope to soon implement simmulated support for frequency and THD as well.

The vrms filter will set the amplitude of a waveform over a defined number of cycles. Here is an example:

```
...
{
  "name": "vrms",
  "target_vrms": 100.0,
  "delay_samples": 12000.0
}
...
```

The above example shows a vrms filter that will take the current Vrms and change it to the target_vrms. This can be used to simulate both sags and swells. The argument `delay_samples` allows us to gradually shift the Vrms over the provided number of samples.

The nop filter will do nothing for the specified number of samples. Here is an example:

```
...
{
  "name": "nop",
  "delay_samples": 12000
}
...
```
 
The above example will do nothing for 12000 samples, leaving the simulator to produce whatever was in its last state.

You might be wondering why this useful? Filters must be wrapped in some JSON that defines filters and how they repeat. A complete filters json definition is provided below.

```
{
  "filters": [
    {
      "name": "vrms",
      "target_vrms": 140.0,
      "delay_samples": 12000
    },
    {
      "name": "nop",
      "delay_samples": 12000
    },
    {
      "name": "vrms",
      "target_vrms": 120.0,
      "delay_samples": 12000
    },
    {
      "name": "nop",
      "delay_samples": 12000
    }
  ],
  "does_repeat": true
}
```
 
This example generates a waveform that produces a swell to 140 Vrms, then sits in the swell state for 12000 samples, then drops back down to 120 Vrms, sits there for 12000 samples, and then repeats indefinitely. 

By chaining state filters with nop filters, we have script fine grained control over the waveform generation. This process will only get better as we introduce more filters.

Once a filter is applied, if you want to change the state or change the filter, you will need to add the `reset: true` directive to your JSON request. Here is an example.

```

{
  "filters": [
    {
      "name": "vrms",
      "target_vrms": 140.0,
      "delay_samples": 12000
    },
    {
      "name": "nop",
      "delay_samples": 12000
    },
    {
      "name": "vrms",
      "target_vrms": 120.0,
      "delay_samples": 12000
    },
    {
      "name": "nop",
      "delay_samples": 12000
    }
  ],
  "does_repeat": true,
  "reset": true
}

```

#### Using the provided HTTP POST client

In util/box/sim you can call sim.py and pass it a JSON file which the script will then POST to the simulator. Here is how it should be invoked.

```
python3 sim.py --state path/to/request.json
```

or 

```
pyhton3 sim.py -s path/to/request.json
```