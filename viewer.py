import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore
pg.setConfigOptions(imageAxisOrder='row-major')
pg.mkQApp()
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('EIGER')


p1 = win.addPlot(title="")
img = pg.ImageItem(colorMap = 'viridis')
p1.addItem(img)

hist = pg.HistogramLUTItem()
hist.setImageItem(img)
hist.gradient.loadPreset('viridis')
win.addItem(hist)

data = np.random.rand(512,512)
img.setImage(data)

win.resize(900, 800)
win.show()

p1.autoRange()  
p1.setAspectLocked(True)




def update():
    levels = hist.getLevels()
    img.setImage(np.random.rand(512,512))
    hist.setLevels(*levels)
    
    #app.processEvents()  ## force complete redraw for every plot



def imageHoverEvent(event):
    if event.isExit():
        p1.setTitle("")
        return
    pos = event.pos()
    i, j = pos.y(), pos.x()
    i = int(np.clip(i, 0, data.shape[0] - 1))
    j = int(np.clip(j, 0, data.shape[1] - 1))
    val = data[i, j]
    ppos = img.mapToParent(pos)
    x, y = ppos.x(), ppos.y()
    p1.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: %.3g" % (x, y, i, j, val))

img.hoverEvent = imageHoverEvent


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)

if __name__ == '__main__':
    pg.exec()