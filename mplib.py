import matplotlib
# matplotlib.use('Gtk3Agg')
# matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import time
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import time

data = np.random.uniform(size=(2000,512))
fig, ax = plt.subplots()
plt.tight_layout()

tstart = time.time()
num_plots = 0
while time.time()-tstart < 1:
    ax.clear()
    ax.imshow(data, interpolation='nearest', aspect='auto', origin='lower')

    plt.pause(0.001)
    num_plots += 1
print(num_plots)