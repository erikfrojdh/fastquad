# fastquad

Scripts to run the fast Egier quad. 

## eiger_viewer

The live viewer is reading data from the slsReceiver zmq stream. The receiver is configured to send out data every ~500ms

This can be run on the server with X forwarding or on your computer given that they are on the same network. 

```python
./eiger_viewer
```

## QuadZmqReceiver

Reads data from the two zmq streams and assembles the full image. Is launched in the background by the viewer but could also be used to prototype online processing. High speed would likely need a different implementation.

## run

Script that starts the detector and receiver with a large amount of frames running at 4 kHz 

```
#on lbemsrv6
./run
```

## acquire

Save N amount of frames to the filename/path configured. Automatically converts the data to hdf5 and adds the gap pixels. 

```
#on lbemsrv6
./acquire 1000
```