import sys
import os 
from os import remove
from os.path import join, dirname, realpath, exists
import numpy as np

def load_body_data(smpl_data, name, idx=0):
    cmu_parms = {}
    for seq in smpl_data.files:
        if seq == ('pose_' + name):
            cmu_parms[seq.replace('pose_', '')] = {'poses':smpl_data[seq],
                                                   'trans':smpl_data[seq.replace('pose_','trans_')]}
    return(cmu_parms, name)
    
import time
start_time = None
def log_message(message):
    elapsed_time = time.time() - start_time
    print("[%.2f s] %s" % (elapsed_time, message))


# Cut gaits to exclude shit frames (as in main_part1)
def cut_sequence(name, data):
    if name == '05_01':
        data['poses'] = data['poses'][:-80]
        data['trans'] = data['trans'][:-80]
    elif name == '39_01':
        data['poses'] = data['poses'][:-20]
        data['trans'] = data['trans'][:-20]
    elif name == '10_04':
        data['poses'] = data['poses'][60:]
        data['trans'] = data['trans'][60:]
    elif name == '45_01':
        data['poses'] = data['poses'][:180]
        data['trans'] = data['trans'][:180]
    elif name == 'ung_47_01':
        data['poses'] = data['poses'][:240]
        data['trans'] = data['trans'][:240]
    elif name == 'ung_77_28':
        data['poses'] = data['poses'][240:840]
        data['trans'] = data['trans'][240:840]
    elif name == 'ung_82_11':
        data['poses'] = data['poses'][240:]
        data['trans'] = data['trans'][240:]
    elif name == 'ung_91_57':
        data['poses'] = data['poses'][250:-250]
        data['trans'] = data['trans'][250:-250]
    elif name == 'ung_104_02':
        data['poses'] = data['poses'][:-240]
        data['trans'] = data['trans'][:-240]
    elif name == 'ung_113_25':
        data['poses'] = data['poses'][:-120]
        data['trans'] = data['trans'][:-120]
    elif name == 'ung_120_20':
        data['poses'] = data['poses'][240:1200]
        data['trans'] = data['trans'][240:1200]
    elif name == 'ung_132_18':
        data['poses'] = data['poses'][120:]
        data['trans'] = data['trans'][120:]
    elif name == 'ung_136_21':
        data['poses'] = data['poses'][60:-60]
        data['trans'] = data['trans'][60:-60]
    elif name == 'ung_139_28':                         
        data['poses'] = data['poses'][240:960]
        data['trans'] = data['trans'][240:960]  
    return data


if __name__ == '__main__':
    # time logging
    #global start_time
    start_time = time.time()
    
    from pickle import load
    import argparse
    
    # parse commandline arguments
    log_message(sys.argv)
    parser = argparse.ArgumentParser(description='Generate synth dataset images.')
    parser.add_argument('--idx', type=int,
                        help='idx of the requested sequence')
    parser.add_argument('--name', type=str,
                        help='name of the requested sequence')
    parser.add_argument('--ishape', type=int,
                        help='requested cut, according to the stride')
    parser.add_argument('--stride', type=int,
                        help='stride amount, default 50')
    parser.add_argument('--direction', type=str,
                        help='subject direction, default forward')
    parser.add_argument('--subject_id', type=int,
                        help='local subject id, default 0')

    args = parser.parse_args(sys.argv[sys.argv.index("---") + 1:])

    idx = args.idx
    name = args.name
    ishape = args.ishape
    stride = args.stride
    direction = args.direction
    subject_id = args.subject_id


    log_message("input idx: %d" % idx)
    log_message("input name: %s" % name)
    log_message("input ishape: %d" % ishape)
    log_message("input stride: %d" % stride)
    log_message("Subject direction: %s" % direction)
    log_message("Local subject id: %d" % subject_id)
    
    if idx == None:
        exit(1)
    if ishape == None:
        exit(1)
    if stride == None:
        log_message("WARNING: stride not specified, using default value 50")
        stride = 50
    
    # import idx info (name, split)
    idx_info = load(open("pkl/idx_info.pickle", 'rb'))

    # get runpass
    (runpass, idx) = divmod(idx, len(idx_info))

    log_message("start part 2")
    
    import hashlib
    import random
    # initialize random seeds with sequence id
    s = "synth_data:%d:%d:%d" % (idx, runpass, ishape)
    seed_number = int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    log_message("GENERATED SEED %d from string '%s'" % (seed_number, s))
    random.seed(seed_number)
    np.random.seed(seed_number)
    
    # import configuration
    import config
    params = config.load_file('config', 'SYNTH_DATA')
    
    smpl_data_folder = params['smpl_data_folder']
    smpl_data_filename = params['smpl_data_filename']
    resy = params['resy']
    resx = params['resx']
    tmp_path = params['tmp_path']
    output_path = params['output_path']
    output_types = params['output_types']
    stepsize = params['stepsize']
    clipsize = params['clipsize']
    openexr_py2_path = params['openexr_py2_path']
    
    # check whether openexr_py2_path is loaded from configuration file
    if 'openexr_py2_path' in locals() or 'openexr_py2_path' in globals():
        for exr_path in openexr_py2_path.split(':'):
            sys.path.insert(1, exr_path)

    # to read exr imgs
    import OpenEXR 
    import array
    import Imath
    
    log_message("Loading SMPL data")
    smpl_data = np.load(join(smpl_data_folder, smpl_data_filename))
    cmu_parms, name = load_body_data(smpl_data, name, idx)

    tmp_path = join(tmp_path, 'run%d_%s_c%04d' % (runpass, name.replace(" ", ""), (ishape + 1)))
    res_paths = {k:join(tmp_path, '%05d_%s'%(idx, k)) for k in output_types if output_types[k]}

    data = cmu_parms[name]
    data = cut_sequence(name, data)
    
    nframes = len(data['poses'][::stepsize])
    output_path = join(output_path, 'run%d' % runpass, name.replace(" ", ""))
    
    # .mat files
    matfile_normal = join(output_path, name.replace(" ", "") + "_c%04d_normal.mat" % (ishape + 1))
    matfile_gtflow = join(output_path, name.replace(" ", "") + "_c%04d_gtflow.mat" % (ishape + 1))
    matfile_depth = join(output_path, name.replace(" ", "") + "_c%04d_depth.mat" % (ishape + 1))
    matfile_segm = join(output_path, name.replace(" ", "") + "_c%04d_segm.mat" % (ishape + 1))
    dict_normal = {}
    dict_gtflow = {}
    dict_depth = {}
    dict_segm = {}
    get_real_frame = lambda ifr: ifr
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

    # overlap determined by stride (# subsampled frames to skip)
    fbegin = ishape*stepsize*stride
    fend = min(ishape*stepsize*stride + stepsize*clipsize, len(data['poses']))
    # LOOP OVER FRAMES
    for seq_frame, (pose, trans) in enumerate(zip(data['poses'][fbegin:fend:stepsize], data['trans'][fbegin:fend:stepsize])):
        iframe = seq_frame
        
        log_message("Processing frame %d" % iframe)
        
        for k, folder in res_paths.items():
            if not k== 'vblur' and not k=='fg':
                path = join(folder, 'Image%04d.exr' % get_real_frame(seq_frame))
                exr_file = OpenEXR.InputFile(path)
                if k == 'normal':
                    mat = np.transpose(np.reshape([array.array('f', exr_file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B")], (3, resx, resy)), (1, 2, 0))
                    dict_normal['normal_%d' % (iframe + 1)] = mat.astype(np.float32, copy=False) # +1 for the 1-indexing
                elif k == 'gtflow':
                    mat = np.transpose(np.reshape([array.array('f', exr_file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G")], (2, resx, resy)), (1, 2, 0))
                    dict_gtflow['gtflow_%d' % (iframe + 1)] = mat.astype(np.float32, copy=False)
                elif k == 'depth':
                    mat = np.reshape([array.array('f', exr_file.channel(Chan, FLOAT)).tolist() for Chan in ("R")], (resx, resy))
                    dict_depth['depth_%d' % (iframe + 1)] = mat.astype(np.float32, copy=False)
                elif k == 'segm':
                    mat = np.reshape([array.array('f', exr_file.channel(Chan, FLOAT)).tolist() for Chan in ("R")], (resx, resy))
                    dict_segm['segm_%d' % (iframe + 1)] = mat.astype(np.uint8, copy=False)
                #remove(path)

    import scipy.io
    scipy.io.savemat(matfile_normal, dict_normal, do_compression=True)
    scipy.io.savemat(matfile_gtflow, dict_gtflow, do_compression=True)
    scipy.io.savemat(matfile_depth, dict_depth, do_compression=True)
    scipy.io.savemat(matfile_segm, dict_segm, do_compression=True)

    # cleaning up tmp
    if tmp_path != "" and tmp_path != "/":
        log_message("Cleaning up tmp")
        os.system('rm -rf %s' % tmp_path)


    log_message("Completed batch")
