import numpy as np
import time
import Pyro4
import pandas as pd

# Pyro4 configuration
Pyro4.config.SERIALIZER = 'serpent'
Pyro4.config.SERIALIZERS_ACCEPTED = {'serpent', 'json', 'marshal', 'pickle'}

Path= 'Z:\\Projects\\Defects for QTM\\Raw data\\2025-03-05'
# Connects to WinSpec in G13
################

temp=4 #K
e_time=25 #s
power=230 #uW

if 1:
    print('connect to ws')
    # uri = 'PYRO:WinSpec@phd-exile-phys.ethz.ch:9093' #G8 spectrometer
    # uri = 'PYRO:WinSpec@phd-exile-phys.ethz.ch:9091' #G11 spectrometer
    uri = 'PYRO:WinSpec@G13-spectrometer.dhcp-int.phys.ethz.ch:9090'
    # uri = 'PYRO:WinSpec@G13-spectrometer.dhcp-int.phys.ethz.ch:55466'
    # uri = 'PYRO:G15WinSpec@phd-exile-phys.ethz.ch:9092'
    ws = Pyro4.Proxy(uri)
    print(ws)
    ws.exposure_time=e_time
    nFrames = 1
    ws.num_frames = nFrames
#    buf = ws.get_spectrum(wlen=True)
# gratingDict = {1500: 1, 300: 2, 1200: 3}
print('spect ok')
###########################

x_step=0.4/15
y_step=0.4/15
x_number=100
y_number=70
Loc_start_x=0
Loc_start_y=0


Loc_start=[Loc_start_x,Loc_start_y]


for i in range(y_number):
    Loc=[]
    Para=[]
    Spectrum=[]
    Wavelength=[]
    for j in range (x_number):
        Loc_x=Loc_start[0]+x_step*j
        Loc_y=Loc_start[1]+y_step*i
        daq.set_ao0(Loc_x)
        daq.set_ao1(Loc_y)
  
        Loc.append([Loc_x,Loc_y])
        
        time.sleep(0.01)
        
        buf = ws.get_spectrum(wlen=True)
        spec,w_array = np.array(buf)
        winSpec = ws.specdict
        Spectrum.append(spec)
        Para.append(winSpec)
        Wavelength.append(w_array)
        time.sleep(0.01)
        if j==0:
            Progress=i/y_number
            print('Progress is %.2f%%'%(Progress*100)+' at '+time.strftime("%y-%m-%d-%H-%M-%S",time.localtime()))
    daq.smooth_set_ao0(0)


    #Get spectrum and waveength from WinSpec
    ###########################
    
    ############################
    Loc=np.array(Loc)
    Spectrum=np.array(Spectrum)
    Wavelength=np.array(Wavelength)
    
    dataframe_Loc = pd.DataFrame(Loc)
    dataframe_Spec = pd.DataFrame(Spectrum)
    dataframe_Wav = pd.DataFrame(Wavelength)
    dataframe_Para = pd.DataFrame(Para)
    
    #'save data'
    
    name="hBNSpectrumScan T=%s K Power=%s uW Exposuretime=%s"%(temp,power,e_time)+time.strftime("%y-%m-%d-%H-%M-%S",time.localtime())
    dataframe_Loc.to_csv(Path+r'\Loc_'+name+'.csv', index=False, sep=',')
    dataframe_Spec.to_csv(Path+r'\Spec_'+name+'.csv', index=False, sep=',')   
    dataframe_Wav.to_csv(Path+r'\Wav_'+name+'.csv', index=False, sep=',')
    dataframe_Para.to_csv(Path+r'\Para_'+name+'.csv', index=False, sep=',')

#daq.set_ao0(-0.1)
#daq.set_ao1(-0.1)
