ID=$1
BLENDER_TYPE=$2
END_FRAME=$3

BLENDER=/d/blender/blender
# OUTPUT_SETTING="--blender-type ${BLENDER_TYPE} --res_x 640 --res_y 512"
# OUTPUT_SETTING="--blender-type ${BLENDER_TYPE} --res_x 1280 --res_y 1024"
OUTPUT_SETTING="--res_x 1280 --res_y 1024"
if [[ $BLENDER_TYPE == "adj" ]]; then
  echo "adjusting camera in blender"
  BLENDER="${BLENDER} -noaudio"
elif [[ $BLENDER_TYPE == "debug" ]]; then
  echo "adjusting camera in blender"
  BLENDER="${BLENDER} -noaudio"
elif [[ $BLENDER_TYPE == "img" ]]; then
  echo "rendering img"
  BLENDER="${BLENDER} --background -noaudio"
  OUTPUT_SETTING="${OUTPUT_SETTING} --use-transparent-bg"
elif [[ $BLENDER_TYPE == "video" ]]; then
  echo "rendering video"
  BLENDER="${BLENDER} --background -noaudio"
fi

folder_name=D:/blender_project/begin/fbx_export_joints_fixrot
# folder_name=/nas/home/huaijin/sequence_vis

${BLENDER} --python render_xbot.py \
        -- ${folder_name} ${OUTPUT_SETTING} \
        --id ${ID} --end_frame ${END_FRAME} --blender_type ${BLENDER_TYPE} 
# if [[ $BLENDER_TYPE == "video" ]]; then
#     read -p "input length: " -a LEN
#     python save_sm_data.py --task combine_video --work-dir ${folder_name}/${MOTION}/${ID} \
#         --save-path ${folder_name}/${MOTION}/${ID}/${ID}.mp4 --start-frame 1 --end-frame ${LEN}
# fi