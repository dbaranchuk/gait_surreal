#!/bin/bash

array=([106]='10_04')
direction="forward"
#"backward"
subject_id="4"
#array=([1261]='ung_07_01' [1262]='ung_07_02' [1263]='ung_07_03' [1264]='ung_07_04' [1265]='ung_07_05' [1266]='ung_07_06' [1267]='ung_07_07' [1268]='ung_07_08' [1269]='ung_07_09' [1270]='ung_07_10' [1271]='ung_07_11' [1272]='ung_07_12' [1826]='ung_12_01' [1827]='ung_12_02' [1828]='ung_12_03' [2118]='ung_142_01' [2119]='ung_142_02' [2120]='ung_142_03' [2121]='ung_142_04' [2122]='ung_142_05' [2123]='ung_142_06' [2124]='ung_142_07' [2125]='ung_142_08' [2126]='ung_142_09' [2127]='ung_142_10' [2128]='ung_142_11' [2129]='ung_142_12' [2130]='ung_142_13' [2131]='ung_142_14' [2132]='ung_142_15' [2133]='ung_142_16' [2134]='ung_142_17' [2135]='ung_142_18' [2136]='ung_142_19' [1199]='91_01' [1200]='91_02' [1201]='91_03' [1202]='91_04' [1203]='91_05' [1204]='91_06' [1205]='91_07' [1206]='91_08' [1207]='91_09' [1208]='91_10' [1209]='91_11' [1210]='91_12' [1211]='91_13' [1212]='91_14' [1213]='91_15' [1214]='91_16' [1215]='91_17' [1216]='91_18' [1217]='91_19' [1218]='91_20' [1219]='91_21' [1220]='91_22' [1221]='91_23' [1222]='91_24' [1223]='91_25' [1224]='91_26' [1225]='91_27' [1226]='91_28' [1227]='91_29' [1228]='91_30' [1229]='91_31' [1230]='91_32' [1231]='91_33' [1232]='91_34' [1233]='91_35' [1234]='91_36' [1235]='91_37' [1236]='91_38' [59]='08_01' [60]='08_02' [61]='08_03' [62]='08_04' [63]='08_05' [64]='08_06' [65]='08_07' [66]='08_08' [67]='08_09' [68]='08_10' [69]='08_11' [748]='35_01' [749]='35_02' [749]='35_15' [751]='35_16' [763]='35_28' [764]='35_29' [765]='35_30' [766]='35_31' [767]='35_32' [768]='35_33' [769]='35_34' [807]='37_01' [808]='38_01' [809]='38_02')

# SET PATHS HERE
FFMPEG_PATH=/home/local/tools/ffmpeg/ffmpeg_build_sequoia_h264
X264_PATH=/home/local/tools/ffmpeg/x264_build/
PYTHON2_PATH=/usr/ # PYTHON 2
BLENDER_PATH=/home/local/tools/blender

# BUNLED PYTHON
BUNDLED_PYTHON=${BLENDER_PATH}/2.79/python
export PYTHONPATH=${BUNDLED_PYTHON}/lib/python3.4:${BUNDLED_PYTHON}/lib/python3.4/site-packages
export PYTHONPATH=${BUNDLED_PYTHON}:${PYTHONPATH}

# FFMPEG
export LD_LIBRARY_PATH=${FFMPEG_PATH}/lib:${X264_PATH}/lib:${LD_LIBRARY_PATH}
export PATH=${FFMPEG_PATH}/bin:${PATH}

#JOB_PARAMS="--idx 64 --name 08_06 --ishape 0 --stride 50"
#echo $JOB_PARAMS
### RUN PART 1  --- Uses python3 because of Blender
#$BLENDER_PATH/blender -b -t 6 -P main_part1.py --- ${JOB_PARAMS}

### RUN PART 2  --- Uses python2 because of OpenEXR
#PYTHONPATH="" ${PYTHON2_PATH}/bin/python2.7 main_part2.py ${JOB_PARAMS}


for i in "${!array[@]}"
do
    echo ${i}
    echo ${array[$i]}
    JOB_PARAMS="--idx ${i} --name ${array[$i]} --ishape 0 --stride 50 --subject_id ${subject_id} --direction ${direction}"
    echo $JOB_PARAMS
#    ### RUN PART 1  --- Uses python3 because of Blender
    $BLENDER_PATH/blender -b -t 4 -P main_part1.py --- ${JOB_PARAMS}
    #nohup $BLENDER_PATH/blender -b -t 4 -P main_part1.py --- ${JOB_PARAMS} > "${subject_id}.out"
done
