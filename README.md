# Onshape-Microbit

This repository shows demonstrations of how Onshape models can be used as digital twins for interacting with a Micro:bit microcontroller.

## Onshape-Arduino

This sub-folder demonstrates how Onshape can be used as a digital twin for interacting with an Arduino microcontroller.

### Onshape-Arduino/pot-to-serial.ino

A simple Arduino script which reads 3 10k potentiometers using `analogRead()`.  The three pot values are concatenated into a delimited strong and sent to the serial port every 0.5 seconds.

### Onshape-Arduino/apitest.py

This Python script accomplishes the following:

* Reads Onshape API authentication from a .json file
* Calls the `https://cad.onshape.com/api/assemblies/d/{}/w/{}/e/{}/matevalues` endpoint to get the mates from the robot model 
* Connects to the Arduino via serial port (hard coded address) and reads one line at a time
* Converts potentiometer values to radians and updates the mate values
* Posts updated mate values to `matevalues` endpoint

![Untitled 2](https://github.com/user-attachments/assets/1f4b0029-8b95-4019-9ab6-1c20801b3ca9)
