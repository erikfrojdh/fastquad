
import zmq
import json
import numpy as np

def get_dtype(dr):
    """
    Returns the correct numpy dtype from a number or string
    Note this dtype is used for storing data and is not neccessary the
    same as the number asked for
    """
    if isinstance(dr, str):
        dr = int(dr)
        
    if dr == 32:
        return np.int32
    elif dr == 16:
        return np.int16
    elif dr == 8:
        return np.uint8
    elif dr == 4:
        return np.uint8
    else:
        raise TypeError(f'Bitdepth: {dr} not supported')

class QuadZmqReceiver:
    
    def __init__(self, detector):
        self.mask = [(slice(0,256,1),slice(0,512,1)),
                    (slice(256,512,1),slice(0,512,1))]
        ip = detector.rx_zmqip
        ports = detector.rx_zmqport[0::2] #Skipping the switched off ports
        self.context = zmq.Context()
        self.sockets = [ self.context.socket(zmq.SUB) for p in ports ]
        for p,s in zip(ports, self.sockets):
            print('Initializing: {:d}'.format(p))
            s.connect('tcp://{:s}:{:d}'.format(ip.str(), p))
            s.setsockopt(zmq.SUBSCRIBE, b'')

    def read_frame(self):

        image = np.zeros((512,512)) #np.double

        for p,s in zip(self.mask, self.sockets):
            header = json.loads( s.recv()[0:-1] )
            data = s.recv()
            end = json.loads( s.recv()[0:-1] )
            if header['bitmode'] == 4:
                tmp = np.frombuffer(data, dtype=np.uint8)
                tmp2 = np.zeros(tmp.size*2, dtype = tmp.dtype)
                tmp2[0::2] = np.bitwise_and(tmp, 0x0f)
                tmp2[1::2] = np.bitwise_and(tmp >> 4, 0x0f)
                image[p] = tmp2.reshape(256,512)
            else:
                image[p] = np.frombuffer(data, dtype = get_dtype(header['bitmode'])).reshape(256,512)
        return image

if __name__ == "__main__":
    from slsdet import Eiger
    d = Eiger()
    r = QuadZmqReceiver(d)
    image = r.read_frame()