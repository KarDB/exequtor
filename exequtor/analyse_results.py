import numpy as np
import matplotlib.pyplot as plt
import generate_instructions.py as gi
from datetime import datetime

folderwithdata = 'datafolder/'

def safe_optimized_parameter()
    savename_optimized_parameters = "Optimized_parameters_ + datetime.today().strftime("%Y-%m-%d-%H-%M-%S")

gi.change_status_optimization('finished')





sweep_val = []
SNRvals = []
maxvals = []
maxinds = []
SNR = []

shift = 200
shiftend = 2000
fts = []
top=0
bottom=-1
left=0
right=-1
dfile = glob.glob('Sync_*.yaml')
num_files = len(dfile)
#sweep_param = "params['pulse_sequence']['pi']"
#sweep_param = "params['pulse_sequence']['pi_half']"
#sweep_param = "params['pulse_sequence']['laserduration']"
#sweep_param = "params['pulse_sequence']['readout_time']"
#sweep_param = "params['static_devices']['rf_source']['channels']['channel_1']['frequency']"
#sweep_param = "params['static_devices']['mw_source']['channels']['channel_1']['frequency']"
sweep_param = "params['pulse_sequence']['N']"
#sweep_param = "params['pulse_sequence']['readout_time']"
#dfile = dfile[:5]
dfile.sort()
for i, file in enumerate(dfile):
    data = np.load(file.replace('.yaml','.npy'))
    with open(file, 'r') as f:
        params = yaml.safe_load(f)
    dt = params['duration_puseseq_cycle']*1e-6
    #print(dt)
    fax = np.fft.rfftfreq(data.shape[2], dt)
    if len(data.shape) == 5:
        data2 = (data[1,0,:,top:bottom,left:right]-data[0,0,:,top:bottom,left:right])/(data[1,0,:,top:bottom,left:right]+data[0,0,:,top:bottom,left:right])
        ft = np.fft.rfft(data2.mean(axis=(1,2)), axis=0)
        ftcomplex = ft.copy()
    elif len(data.shape) == 3:
        data2 = (data[1,0,:]-data[0,0,:])/(data[1,0,:]+data[0,0,:])
        ft = np.fft.rfft(data2)
        ftcomplex = ft.copy()
        ft_half = np.fft.rfft(data2[int(len(data2)/2):])
        ftax_half = np.fft.rfftfreq(int(len(data2)/2), dt)


    plot_cutoff = 10
    ft = np.abs(ft)
    plt.plot(fax[plot_cutoff:] + i*0, ft[plot_cutoff:] + 0*i, c=cm.cool(i/num_files))
    maxind = np.argmax(ft[shift:shiftend]) + shift
    if len(data.shape) == 5:
        std = ftcomplex.mean(axis=(1,2))[maxind+10:].real.std()
    else:
        std = ftcomplex[maxind+10:].real.std()
    maxinds.append(maxind)
    maxval = max(ft[maxind-10:])
    maxval = ft[maxind]
    maxvals.append(maxval)
    sweep_val.append(eval(sweep_param))
    SNR.append(maxval/std)
    del data
    del data2
    fts.append(ft)
    gc.collect()
maxinds = np.asarray(maxinds)
print(maxinds, maxvals)
plt.scatter(fax[maxinds], maxvals, )
fts = np.asarray(fts)
plt.savefig('Sweep_syncs.png')
