ID=$1
BLENDER_TYPE=$2

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

if [[ $BLENDER_TYPE == "video" ]] || [[ $BLENDER_TYPE == "adj" ]] || [[ $BLENDER_TYPE == "debug" ]]; then
  read -p "start frame: " -a start
  read -p "end frame: " -a end
  ${BLENDER} --python render_xbot.py \
      -- ${folder_name} ${OUTPUT_SETTING} \
      --id ${ID} --start_frame ${start} --end_frame ${end} --blender_type ${BLENDER_TYPE} 
  if [[ $BLENDER_TYPE == "video" ]]; then
    python ./utils/combine_video.py --work-dir ${folder_name}/rend_imgs/${ID} \
        --save-path ${folder_name}/rend_video/${ID}/start${start}end${end}.mp4 --start-frame ${start} --end-frame ${end}
  fi
fi

if [[ $BLENDER_TYPE == "img" ]]; then
  read -p "select frame: " -a select_frame
  ${BLENDER} --python render_xbot.py \
    -- ${folder_name} ${OUTPUT_SETTING} \
    --id ${ID} --start_frame ${select_frame} --end_frame ${select_frame} --blender_type ${BLENDER_TYPE} 
fi