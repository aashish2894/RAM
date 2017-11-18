from run_mnist import MNIST_DOMAIN_OPTIONS
from run_mnist import PARAMETERS

from network import RAM
from MNIST_Processing import MNIST

from matplotlib import pyplot as plt
import numpy as np

save = True

mnist_size = MNIST_DOMAIN_OPTIONS.MNIST_SIZE
channels = MNIST_DOMAIN_OPTIONS.CHANNELS
minRadius = MNIST_DOMAIN_OPTIONS.MIN_ZOOM
sensorResolution = MNIST_DOMAIN_OPTIONS.SENSOR
loc_std = MNIST_DOMAIN_OPTIONS.LOC_STD
nZooms = MNIST_DOMAIN_OPTIONS.NZOOMS
nGlimpses = MNIST_DOMAIN_OPTIONS.NGLIMPSES

#Reduce the batch size for evaluatoin
batch_size = 2 #PARAMETERS.BATCH_SIZE

totalSensorBandwidth = nZooms * sensorResolution * sensorResolution * channels
mnist = MNIST(mnist_size, batch_size, channels, minRadius, sensorResolution,
                   nZooms, loc_std, MNIST_DOMAIN_OPTIONS.UNIT_PIXELS,
                   MNIST_DOMAIN_OPTIONS.TRANSLATE, MNIST_DOMAIN_OPTIONS.TRANSLATED_MNIST_SIZE)
ram = RAM(totalSensorBandwidth, batch_size, nGlimpses,
               PARAMETERS.OPTIMIZER, PARAMETERS.LEARNING_RATE, PARAMETERS.LEARNING_RATE_DECAY,
               PARAMETERS.MIN_LEARNING_RATE, PARAMETERS.MOMENTUM,
               MNIST_DOMAIN_OPTIONS.LOC_STD, PARAMETERS.CLIPNORM, PARAMETERS.CLIPVALUE)

ram.load_model(PARAMETERS.MODEL_FILE_PATH, PARAMETERS.MODEL_FILE)
print("Loaded model from " + PARAMETERS.MODEL_FILE_PATH + PARAMETERS.MODEL_FILE)


plt.ion()
plt.show()

X, Y= mnist.get_batch_test(batch_size)
img = np.reshape(X, (batch_size, mnist_size, mnist_size, channels))
for k in xrange(batch_size):
    one_img = img[k,:,:,:]

    plt.title(Y[k], fontsize=40)
    plt.imshow(one_img[:,:,0], cmap=plt.get_cmap('gray'),
               interpolation="nearest")
    plt.draw()
    #time.sleep(0.05)
    if save:
        plt.savefig("symbol_" + repr(k) + ".png")
    plt.pause(1.0001)

loc = np.random.uniform(-1, 1,(batch_size, 2))
sample_loc = np.tanh(np.random.normal(loc, loc_std, loc.shape))
for n in range(nGlimpses):
    zooms = mnist.glimpseSensor(X,sample_loc)
    ng = 1
    nz = 1
    #for g in zooms:
    for g in range(batch_size):
        plt.title(Y[g], fontsize=40)
        for z in zooms[g]:
        #for z in g:
            plt.imshow(z[:,:], cmap=plt.get_cmap('gray'),
                       interpolation="nearest")

            plt.draw()
            if save:
                plt.savefig("symbol_" + repr(g) +
                            "glimpse_" + repr(n) +
                            "zoom_" + repr(nz) + ".png")
            #time.sleep(0.05)
            plt.pause(1.0001)
            nz += 1
        ng += 1
    a_prob, loc = ram.choose_action(zooms, sample_loc)
    sample_loc = np.tanh(np.random.normal(loc, loc_std, loc.shape))
ram.reset_states()


