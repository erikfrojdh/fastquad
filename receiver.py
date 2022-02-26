
import zmq
import json
import numpy as np

def get_storage_dtype(n_bits):
    """
    Convert from number of bits to the numpy data type that
    is used to store the data. If an unsupported number of bits
    are passed in the function raises a TypeError
    """
    n_bits = int(n_bits) #in case string was passed in
    if n_bits == 32:
        return np.int32
    elif n_bits == 16:
        return np.int16
    elif n_bits == 8:
        return np.uint8
    elif n_bits == 4:
        return np.uint8
    else:
        raise TypeError(f'Bitdepth: {n_bits} not supported')


def decode(data, n_bits):
    """
    From bytes to numpy array. In the case of 4 bit data we need
    to expand to 8 bits to be able to manipulate the data in a 
    convenient way.
    """
    if n_bits == 4:
        tmp = np.frombuffer(data, dtype=np.uint8)
        tmp2 = np.zeros(tmp.size*2, dtype = tmp.dtype)
        tmp2[0::2] = np.bitwise_and(tmp, 0x0f)
        tmp2[1::2] = np.bitwise_and(tmp >> 4, 0x0f)
        return tmp2.reshape(256,512)
    else:
        return np.frombuffer(data, dtype = get_storage_dtype(n_bits)).reshape(256, 512)

class QuadZmqReceiver:
    """
    Class to manage the connection to the zmq streams and 
    to provide the read_frame function.
    """

    #This mask can be used to select top or bottom of
    #the detector. Format is which rows then which columns
    mask = [(slice(0,256,1),slice(0,512,1)), (slice(256,512,1),slice(0,512,1))]

    def __init__(self, ip, ports, timeout_ms = -1):
        """
        Initialize the class, and set up the zmq connection
        """
        self.context = zmq.Context()
        self.sockets = [ self.context.socket(zmq.SUB) for p in ports ]
        for p,s in zip(ports, self.sockets):
            endpoint = f'tcp://{ip}:{p}'
            print(f'Connecting: {endpoint}')
            s.connect(endpoint)
            s.setsockopt(zmq.SUBSCRIBE, b'')
            s.setsockopt(zmq.RCVTIMEO, timeout_ms)

    def read_frame(self):
        """
        Read one frame from the two zmq streams and put the image together
        """

        #Create an image of 512x512 pixels. The default data type
        #in numpy is double
        image = np.zeros((512,512))

        #For each socket (the quad has two) we read one image
        #This is done in a while loop to be able to continue reading
        #if we get the end of transmission message (single message)
        for p,s in zip(self.mask, self.sockets):

            #Receive multipart messages until we get one of length 2 
            #this means header and data. At end of an acquisition 
            #there is a length 1 message that we can filter in this way
            while True:
                msg = s.recv_multipart()
                if len(msg) == 2:
                    header = json.loads(msg[0])
                    data = msg[1]
                    break

            image[p] = decode(data, header['bitmode'])

        #Flip the rows of the "top" module to match the image
        #TODO! could maybe be read from the header
        image[self.mask[0]] = np.flipud(image[self.mask[0]])
        return image
