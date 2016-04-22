# Loading libraries
from scipy.io  import loadmat
import h5py
from time import strptime
from calendar import timegm
import pysam

print pysam.__version__ 
print pysam.__file__

# /nfs/software/cn/el6.5/python/envs/.virtualenvs/cpython279/lib/python2.7/site-packages/RSeQC-2.6.2-py2.7-linux-x86_64.egg

# pip install --target="/nfs/software/cn/el6.5/python/envs/.virtualenvs/cpython279/lib/python2.7/" pysam
# pip install --target="/nfs/software/cn/el6.5/python/envs/.virtualenvs/cpython279/lib/python2.7/site-packages/" pysam

# At the end the solution was to chmod by Pablo and desinstall the pysam version inside RSeQC
## Files are in:
# ftp://anonymous:@ftp.mrc-lmb.cam.ac.uk/pub/tjucikas/wormdatabase

## I copied all animals from JU440 into:
## ~/2016_worm_DB/30m_wait/
## then from ~/2016_worm_DB I create ju440_all folder and use this command 
# find . -name \*.mat -exec cp {} ju440_all \;

input_file = '/Users/jespinosa/2016_worm_DB/ju440_all/575 JU440 on food L_2011_02_17__11_00___3___1_features.mat'

# worm_data = loadmat(input_file)

f = h5py.File(input_file)

f.keys()
f.id
f.ref
f.attrs.keys()
f['info'].keys()

## TO get the structure GO TO command line and type:
## h5ls -vlr "/Users/jespinosa/git/pergola/test/c_elegans_data_test/575 JU440 on food L_2011_02_17__11_00___3___1_features.mat"

### INFO
sex_r = f['info']['experiment']['worm']['sex']

# /info/experiment/worm/sex
## How to extract char 
## http://stackoverflow.com/questions/12036304/loading-hdf5-matlab-strings-into-python
# for c in sex_r:
#     print c
#     print unichr(c)
    
sex = [''.join(unichr(c) for c in sex_r)]
sex = str(''.join(unichr(c) for c in sex_r))

# /info/experiment/worm/habituation (time of habituation) 
# i.e. there is a lapse of time within which they don't track animals:
# "We observed a 30-min wait, before tracking, to allow worms to habituate 
# after being picked and moved to their tracking plate"

habituation_r = f['info']['experiment']['worm']['habituation']
habituation = [''.join(unichr(c) for c in habituation_r)]
habituation = str(''.join(unichr(c) for c in habituation_r))

f['info']['experiment']['environment'].keys() # [u'annotations', u'arena', u'chemicals', u'food', 
                                              #  u'illumination', u'temperature', u'timestamp', u'tracker']

# annotations (empty)
annotations_r = f['info']['experiment']['environment']['annotations']
annotations = [''.join(c.astype(str) for c in annotations_r)]
annotations = str(''.join(c.astype(str) for c in annotations_r))

# info/experiment/worm/genotype
genotype_r = f['info']['experiment']['worm']['genotype'] #type u2
genotype = [''.join(unichr(c) for c in genotype_r)]
genotype = str(''.join(unichr(c) for c in genotype_r))

# /info/experiment/worm/strain
strain_r = f['info']['experiment']['worm']['strain']
strain = str(''.join(unichr(c) for c in strain_r))

# age worm
# /info/experiment/worm/age
age_r = f['info']['experiment']['worm']['age'] #type u2
age = str(''.join(unichr(c) for c in age_r))

# /info/experiment/environment/food
food_r = f['info']['experiment']['environment']['food'] #type u2
food = str(''.join(unichr(c) for c in food_r))

# /info/experiment/environment/timestamp
timestamp_r = f['info']['experiment']['environment']['timestamp'] #type u2
timestamp = str(''.join(unichr(c) for c in timestamp_r))

# HH:MM:SS.mmmmmm
my_date_object = strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
unix_time = timegm(my_date_object) # utc based # correct!!!

# /info/video/length/time
time_recorded_r = f['info']['video']['length']['time']
time_recorded = time_recorded_r[0][0]

# /info/video/length/frames
frames_r = f['info']['video']['length']['frames']
time = frames_r[0][0] 

##############
## WORM DATA
f['worm'].keys() # [u'locomotion', u'morphology', u'path', u'posture']
f['worm']['locomotion'].keys()
f['worm']['locomotion']['velocity'].keys() # [u'head', u'headTip', u'midbody', u'tail', u'tailTip']

# These primary features were also evaluated in different contexts to give more complex parameterization: 
# for example, mean speed was measured over the entire video as well as independently for periods when the 
# animal was moving either forward or backward. Likewise, dorsal and ventral bending were measured over the 
# entire body and in specific regions such as the head, tail and midbody. Finally, specific behavioral events 
# such as reversals or omega turns were used to generate secondary parameters, such as the frequency, time spent
# in execution and distance covered during the event.

# la ideas seria por ejemplo hacer un bed para forward backward
# y otro para velocidad y entonces hacer un analysis parecido al del paper
# comparar por ejemplo si las velocidades son iguales

tail_v = f['worm']['locomotion']['velocity']['tail']['speed']
midbody_v = f['worm']['locomotion']['velocity']['midbody']['speed']
head_v = f['worm']['locomotion']['velocity']['head']['speed']
tail_v = f['worm']['locomotion']['velocity']['tailTip']['speed']
headTip_v = f['worm']['locomotion']['velocity']['headTip']['speed']
tailTip_v = f['worm']['locomotion']['velocity']['tailTip']['speed']

len(tail_v)
len(midbody_v)
len(head_v)
len(tail_v)

f['worm']['path'].keys() # [u'coordinates', u'curvature', u'duration', u'range']
f['worm']['path']['duration'].keys() # [u'arena', u'head', u'midbody', u'tail', u'worm']
f['worm']['path']['duration']['arena'].keys() #[u'height', u'max', u'min', u'width']
f['worm']['path']['duration']['arena']['min'].keys() # x y
f['worm']['path']['duration']['arena']['min']['x'][0]
f['worm']['path']['duration']['arena']['min']['y'][0]
f['worm']['path']['duration']['arena']['max']['x'][0]
f['worm']['path']['duration']['arena']['max']['y'][0]

f['worm']['path']['duration']['head'].keys() # [u'indices', u'times']
f['worm']['path']['duration']['head']['indices']
f['worm']['path']['duration']['head']['times'][0][1]
f['worm']['path']['duration']['head']['indices'][0][1]

times = f['worm']['path']['duration']['head']['times'][0]
len(times)
times[0]

## 
f['worm']['path']['duration']['arena']

## son las tres iguales 26995

head_v[200:300]
tailTip_v[200:300]
headTip_v[200:300]
tailTip_v[200][0] #nan

# Is this nan related with mode or paused
mode_l[200] #no 
start_paused # no is when the animals stop moving

f['worm']['locomotion']['velocity'].keys()  # [u'head', u'headTip', u'midbody', u'tail', u'tailTip']

for i in midbody_v[1:40]: print i

# Frames contain the frames recorded during the experiment
frames
len(midbody_v) # 26995 estos son las frames
# web frames 26995

time_recorded  # 898.932 
898.932 / 60 # = 14.9822

# min x 60s/1min
14.9822 * 60 # =  898.932

# web FPS 30.03
898.932 * 30.03 #= 26994.92796 #it match OK!!!

## Info
f['info'].keys()
f['info']['video'].keys()
f['info']['video']['resolution'].keys()

fps = f['info']['video']['resolution']['fps'][0][0]

width_pix = f['info']['video']['resolution']['width'][0][0]

26995/640

## Locomoation data (forward, backward, etc)
f['worm']['locomotion'].keys()
f['worm']['locomotion']['motion'].keys() # [u'backward', u'forward', u'mode', u'paused']
f['worm']['locomotion']['motion']['forward'].keys() # [u'frames', u'frequency', u'ratio']
f['worm']['locomotion']['motion']['forward']['frames'].keys() # [u'distance', u'end', u'interDistance', u'interTime', u'start', u'time']
f['worm']['locomotion']['motion']['forward']['frames']['distance'][0][0]

#motion
start_for_r = f['worm']['locomotion']['motion']['forward']['frames']['start']
end_for_r = f['worm']['locomotion']['motion']['forward']['frames']['end']
start_back_r = f['worm']['locomotion']['motion']['backward']['frames']['start']
end_back_r = f['worm']['locomotion']['motion']['backward']['frames']['end']

# paused
start_paused_r = f['worm']['locomotion']['motion']['paused']['frames']['start']
end_paused_r = f['worm']['locomotion']['motion']['paused']['frames']['end']

end_paused = list()
for element in end_paused_r:
    end_paused.append(f[element[0]][0][0])
end_paused[0]
start_paused = list()
for element in start_paused_r:
    start_paused.append(f[element[0]][0][0])

end_for[-1]
start_for[-1]

start_for[0] #17 En midbody es 17+1
start_back[0] #274
end_back[0] #299
start_paused[0] #860
((0.30*3 + 0.20*1 + 0.10*2)/100)/2
((0.30*3 + 0.20*1 + 0.10*2)/100)/4
midbody_v[0:12]
midbody_v[0:17] # it is exactly the index without summing or substracting 1
midbody_v[0:18]

# What is mode
mode_l = f['worm']['locomotion']['motion']['mode']
mode_l[-20]

# mode_l = list()
# for element in mode_r:
#     mode_l.append(f[element[0]][0][0])


len(midbody_v)

midbody_v[start_for[-1]: end_for[-1]]

midbody_v[1:3]

midbody_v[26580: 26994]

midbody_v[26579]

## WORKING
# http://stackoverflow.com/questions/27670149/read-matlab-v7-3-file-into-python-list-of-numpy-arrays-via-h5py
end_t = [f[element[0]][:] for element in end]

end_t

# Los datos de los celegans estan en la pagina web cuando pones show all.

sex
habituation # 30 minutes 
annotations
genotype
strain
age
food
unix_time
fps

##############
## WORM DATA
# turns
# /worm/locomotion/turns/omegas/frames/start

# start_omegas_r = f['worm']['locomotion']['turns']['omegas']['frames']['start'][0][0]
# end_omegas_r = f['worm']['locomotion']['turns']['omegas']['frames']['end'][0][0]
# start_upsilons_r = f['worm']['locomotion']['turns']['upsilons']['frames']['start'][0][0]
# start_upsilons_r = f['worm']['locomotion']['turns']['upsilons']['frames']['start'][0][1]

## Asi funciona
# f['worm']['locomotion']['turns'].keys() # [u'omegas', u'upsilons']

# end_upsilons_r = f['worm']['locomotion']['turns']['upsilons']['frames']['end'][0][0]
# end_upsilons_r = f['worm']['locomotion']['turns']['upsilons']['frames']['end'][0][1]

# f[end_upsilons_r][0][0]

# ary_start_upsilons_r = f['worm']['locomotion']['turns']['upsilons']['frames']['start'][0]
# ary_end_upsilons_r = f['worm']['locomotion']['turns']['upsilons']['frames']['end'][0]
# ary_refs = ary_end_upsilons_r
