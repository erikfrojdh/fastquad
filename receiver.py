
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
    def __init__(self, ip, ports):
        self.mask = [(slice(0,256,1),slice(0,512,1)),
                    (slice(256,512,1),slice(0,512,1))]

        self.context = zmq.Context()
        self.sockets = [ self.context.socket(zmq.SUB) for p in ports ]
        for p,s in zip(ports, self.sockets):
            endpoint = f'tcp://{ip}:{p}'
            print(f'Connecting: {endpoint}')
            s.connect(endpoint)
            s.setsockopt(zmq.SUBSCRIBE, b'')
            s.setsockopt(zmq.RCVTIMEO, 100) #Wait 100ms

    def read_frame(self):
        """Read one frame from the two zmq streams"""
        image = np.zeros((512,512))

        for p,s in zip(self.mask, self.sockets):
            while True:
                msg = s.recv_multipart()
                if len(msg) == 2:
                    #We have header and data
                    break
                else:
                    #Special case dummy message at the end of acq, try to read next frame
                    pass


            header = json.loads(msg[0])
            data = msg[1]

            if header['bitmode'] == 4:
                tmp = np.frombuffer(data, dtype=np.uint8)
                tmp2 = np.zeros(tmp.size*2, dtype = tmp.dtype)
                tmp2[0::2] = np.bitwise_and(tmp, 0x0f)
                tmp2[1::2] = np.bitwise_and(tmp >> 4, 0x0f)
                image[p] = tmp2.reshape(256,512)
            else:
                image[p] = np.frombuffer(data, dtype = get_dtype(header['bitmode'])).reshape(256,512)
        
        image[self.mask[0]] = np.flipud(image[self.mask[0]])
        return image
