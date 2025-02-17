from batch_face import RetinaFace, SixDRep
import cv2
import numpy as np
import json
import torch
import math
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
GPU = int(os.getenv('GPU'))
YAW_HIGH = int(os.getenv('YAW_HIGH'))
YAW_LOW = int(os.getenv('YAW_LOW'))
PITCH_HIGH = int(os.getenv('PITCH_HIGH'))
PITCH_LOW = int(os.getenv('PITCH_LOW'))


# fix this it should work wo gpu
# model used for detecting different faces in the frame
detector = RetinaFace(gpu_id=GPU)
# model used to zoom into the face and estimate head pose
head_pose_estimator = SixDRep(gpu_id=GPU)

# # multi-processing piece - CAN add later for faster inference times
# sleep_time = 0.01

# up down - head pose - within this range - engaged
pitch_range = (PITCH_LOW, PITCH_HIGH)
# left right - head pose - within this range - engaged 
yaw_range = (YAW_LOW, YAW_HIGH)


def inference_batch(batch):
    '''
    Runs face detection and head pose estimation on a batch of frames.
    '''
    global detector
    batch_numpy = np.array(batch)

    with torch.no_grad():
        # Run RetinaFace detection
        batch_face_object = detector(batch_numpy, return_dict=True)
        
        # ✅ Check if any faces are detected
        if not any(batch_face_object):  # If empty, return an empty list
            return [], []

        # Run head pose estimation only if faces are detected
        head_poses = head_pose_estimator(batch_face_object, batch_numpy, update_dict=True, input_face_type='dict')

    return batch_face_object, head_poses


def mark_batch(batch_face_object, batch):
    green = (0, 255, 0)
    red = (255, 0, 0)
    thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    marked_batch = []
    for frame, face_object in zip(batch, batch_face_object):
        f = frame
        for face in face_object:
            c1 = (round(face['box'][0]), round(face['box'][1]))
            c2 = (round(face['box'][2]), round(face['box'][3]))
            f = cv2.rectangle(frame, c1, c2, green, thickness)
            if face['focused']:
                f = cv2.putText(f, 'Focused', c1, font, font_scale, green, thickness=1)
            else:
                f = cv2.putText(f, 'Unocused', c1, font, font_scale, red, thickness=1)
        marked_batch.append(f)
    return marked_batch


def write_batch(marked_batch, writer, batch_face_dict, output_file):
    for frame in marked_batch:
        writer.write(frame)
    data = []
    with open(output_file, 'r') as f:
        data = json.load(f)
    for frame in range(len(batch_face_dict)):
        for face in range(len(batch_face_dict[frame]['faces'])):
            batch_face_dict[frame]['faces'][face]['box'] = batch_face_dict[frame]['faces'][face]['box'].tolist()
            batch_face_dict[frame]['faces'][face]['kps'] = batch_face_dict[frame]['faces'][face]['kps'].tolist()
            batch_face_dict[frame]['faces'][face]['score'] = float(batch_face_dict[frame]['faces'][face]['score'])
            for key in batch_face_dict[frame]['faces'][face]['head_pose']:
                batch_face_dict[frame]['faces'][face]['head_pose'][key] = float(batch_face_dict[frame]['faces'][face]['head_pose'][key])
    data += batch_face_dict
    with open(output_file, 'w') as f:
            data = json.dump(data, f, indent=4)


def focus_detection(batch_face_object):
    for frame_face_object in batch_face_object:
        for face in range(len(frame_face_object)):
            pitch = frame_face_object[face]['head_pose']['pitch'] < max(pitch_range) and frame_face_object[face]['head_pose']['pitch'] > min(pitch_range)
            yaw = frame_face_object[face]['head_pose']['yaw'] < max(yaw_range) and frame_face_object[face]['head_pose']['yaw'] > min(yaw_range)
            if pitch and yaw:
                frame_face_object[face]['focused'] = True
            else:
                frame_face_object[face]['focused'] = False
    return batch_face_object


def process_video(input_video: str, output_file: str, output_video: str | None = None,
                  batch_size=10, output_fps=4):
    """
    Processes the video for engagement analysis and returns attention_dict.
    """

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise Exception("Video file not found or cannot be opened.")

    fw, fh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    fps_ratio = round(input_fps / output_fps)

    out = None
    if output_video:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, output_fps, (fw, fh))

    engagement_results = []

    frame_counter = -1
    batch, batch_timestamps = [], []
    flag = True

    while flag:
        ret, frame = cap.read()
        if not ret:
            flag = False
        frame_counter += 1
        if (frame_counter % fps_ratio) and flag:
            continue
        if flag:
            batch.append(frame)
            batch_timestamps.append(frame_counter * 1000 / input_fps)
        
        if (len(batch) == batch_size) or (not flag and len(batch)):
            batch_face_object, _ = inference_batch(batch)
            batch_face_object = focus_detection(batch_face_object)

            for face_object, time_stamp in zip(batch_face_object, batch_timestamps):
                processed_faces = []
                for face in face_object:
                    processed_faces.append({
                        "box": face['box'].tolist() if isinstance(face['box'], np.ndarray) else list(face['box']),
                        "score": float(face['score']) if isinstance(face['score'], np.floating) else face['score'],
                        "head_pose": {k: float(v) if isinstance(v, (np.float32, np.float64)) else v for k, v in face['head_pose'].items()},
                        "focused": bool(face['focused'])
                    })

                engagement_results.append({
                    "time": float(time_stamp),
                    "faces": processed_faces
                })

            if output_video:
                marked_batch = mark_batch(batch_face_object, batch)
                for frame in marked_batch:
                    out.write(frame)

            batch, batch_timestamps = [], []

    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

    # Save engagement results to file for `attention_from_direction()`
    with open(output_file, 'w') as f:
        json.dump(engagement_results, f, indent=4)

    # Generate attention_dict using the saved file
    attention_dict = attention_from_direction(output_file)

    return attention_dict  # ✅ Returns fixed `attention_dict`


# This version returns list of dict in json form
def process_video(input_video: str, output_video: str | None = None,
                  batch_size=10, output_fps=4):
    """
    Processes the video for engagement analysis and returns attention_dict.
    """

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise Exception("Video file not found or cannot be opened.")

    fw, fh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    fps_ratio = round(input_fps / output_fps)

    out = None
    if output_video:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, output_fps, (fw, fh))

    engagement_results = []

    frame_counter = -1
    batch, batch_timestamps = [], []
    flag = True

    while flag:
        ret, frame = cap.read()
        if not ret:
            flag = False
        frame_counter += 1
        if (frame_counter % fps_ratio) and flag:
            continue
        if flag:
            batch.append(frame)
            batch_timestamps.append(frame_counter * 1000 / input_fps)
        
        if (len(batch) == batch_size) or (not flag and len(batch)):
            batch_face_object, _ = inference_batch(batch)
            batch_face_object = focus_detection(batch_face_object)

            for face_object, time_stamp in zip(batch_face_object, batch_timestamps):
                processed_faces = []
                for face in face_object:
                    processed_faces.append({
                        "box": face['box'].tolist() if isinstance(face['box'], np.ndarray) else list(face['box']),
                        "score": float(face['score']) if isinstance(face['score'], np.floating) else face['score'],
                        "head_pose": {k: float(v) if isinstance(v, (np.float32, np.float64)) else v for k, v in face['head_pose'].items()},
                        "focused": bool(face['focused'])
                    })

                engagement_results.append({
                    "time": float(time_stamp),
                    "faces": processed_faces
                })

            if output_video:
                marked_batch = mark_batch(batch_face_object, batch)
                for frame in marked_batch:
                    out.write(frame)

            batch, batch_timestamps = [], []

    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

    return engagement_results


# WORK IN PROGRESS
def engagement_from_focus(filename):
    # incomplete
    def dist(p1, p2):
        return math.sqrt(abs(p1[0]-p2[0])**2 + abs(p1[1]-p2[1])**2)
    
    class Face:
        def __init__(self, arr):
            self.location = (arr[0], arr[1])
            self.range = dist((arr[0], arr[1]), (arr[2], arr[3]))
            self.data = dict()
            self.engagement = dict()
        
        def could_be(self, arr):
            return self.range >= dist(self.location, (arr[0], arr[1]))
        
        def update(self, arr):
            self.location = (arr[0], arr[1])
            self.range = dist((arr[0], arr[1]), (arr[2], arr[3]))
    
    faces = []

    with open(filename, 'r') as file:
        data = json.load(file)
    
    for frame in tqdm(data):
        for new_face in frame['faces']:
            matched = False
            for old_face in faces:
                if old_face.could_be(new_face['box']):
                    old_face.update(new_face['box'])
                    old_face.data[frame['time']] = int(new_face['focused'])
                    matched = True
                    break
            if not matched:
                faces.append(Face(new_face['box']))

    focus_limit = 3
    tolerence = 0.7

    for face in tqdm(faces):
        t = sorted(list(face.data.keys()))
        st, et = 0, 0
        moving_sum = 0
        while et < len(t):
            if t[et] - t[st] <= focus_limit * 1000:
                moving_sum += face.data[t[et]]
            while t[et] - t[st] > focus_limit * 1000:
                moving_sum -= face.data[t[st]]
                st += 1
            face.engagement[t[et]] = int(moving_sum/(et-st if et>st else 1) >= tolerence)
            et += 1
    
    engagement = [face.engagement for face in faces]
    #convert to df and get engagement % of each timestamp
    df = pd.DataFrame(engagement)
    avg_row = df.mean().to_dict()
    avg_df = pd.DataFrame(avg_row, index=[0])
    print(avg_df.iloc[-1].value_counts(dropna=False))
    avg_df.to_csv('temp.csv')


def direction_from_json(filename, outfile):
    with open(filename, 'r') as file:
        data = json.load(file)
    
    directions = dict()
    for frame in data:
        directions[frame['time']] = []
        for face in frame['faces']:
            direction = 'straight'
            if face['head_pose']['yaw'] > max(yaw_range):
                direction = 'right'
            elif face['head_pose']['yaw'] < min(yaw_range):
                direction = 'left'
            elif face['head_pose']['pitch'] > max(pitch_range):
                direction = 'up'
            elif face['head_pose']['pitch'] < min(pitch_range):
                direction = 'down'
            directions[frame['time']].append(direction)
        
    with open(outfile, 'w') as file:
        json.dump(directions, file, indent=4)


def direction_from_json(json_data):
    data = json_data

    directions = dict()
    for frame in data:
        directions[frame['time']] = []
        for face in frame['faces']:
            direction = 'straight'
            if face['head_pose']['yaw'] > max(yaw_range):
                direction = 'right'
            elif face['head_pose']['yaw'] < min(yaw_range):
                direction = 'left'
            elif face['head_pose']['pitch'] > max(pitch_range):
                direction = 'up'
            elif face['head_pose']['pitch'] < min(pitch_range):
                direction = 'down'
            directions[frame['time']].append(direction)
        
    return directions


def attention_from_direction(data_source, t1=2000, t2=4000, attention_threshold=0.7) -> dict:
    """
    Computes attention spans based on head directions.
    
    Args:
        data_source: Path to JSON file containing engagement data.
                     OR
                     Engagement data in json format.
        t1: Threshold (in milliseconds) for "mostly focused".
        t2: Threshold (in milliseconds) for "partially focused".
        attention_threshold: Minimum threshold for focus detection.

    Returns:
        A dictionary with attention spans categorized into:
            - focused
            - mostly focused
            - partially focused
            - unfocused
    """
    if type(data_source) == str:
        with open(data_source, 'r') as f:
            data = json.load(f)
    else:
        data = data_source

    # Convert JSON dictionary keys (timestamps) into float values
    direction_data = {}
    for frame in data:
        frame_time = float(frame)
        direction_data[frame_time] = sum([1 if face == 'straight' else 0 for face in data[frame]]) / len(data[frame]) if data[frame] else 0  # Avoid division by zero

    # Process time-based attention spans
    timestamps = sorted(list(direction_data.keys()))
    x = 0
    y = 0
    attention_dict = {'focused': [], 'mostly focused': [], 'partially focused': [], 'unfocused': []}

    # Initialize moving window for attention detection
    while y < len(timestamps) and timestamps[y] - timestamps[x] <= t1:
        y += 1  # Expand the window

    moving_sum = sum([direction_data[t] for t in timestamps[x:y]])
    window_size = y - x
    attention = attention_threshold < moving_sum / window_size if window_size > 0 else False
    last_marker = 0

    while y < len(timestamps):
        moving_sum += direction_data[timestamps[y]] - direction_data[timestamps[x]]
        new_attention = attention_threshold < moving_sum / window_size if window_size > 0 else False

        if attention != new_attention:
            if attention:
                attention_dict['focused'].append((timestamps[last_marker], timestamps[y]))
            else:
                duration = timestamps[y] - timestamps[last_marker]
                if duration < t1:
                    attention_dict['mostly focused'].append((timestamps[last_marker], timestamps[y]))
                elif duration < t2:
                    attention_dict['partially focused'].append((timestamps[last_marker], timestamps[y]))
                else:
                    attention_dict['unfocused'].append((timestamps[last_marker], timestamps[y]))
            attention = new_attention
            last_marker = x + 1

        y += 1
        x += 1

    return attention_dict  # ✅ Fixed structure


def frontend_pipeline(input_video: str, output_video: str | None = None, batch_size=10, output_fps=4, 
                      t1=2000, t2=4000, attention_threshold=0.7):
    engagement_results = process_video(input_video, output_video, batch_size, output_fps)
    directions = direction_from_json(engagement_results)
    attention_dict = attention_from_direction(directions, t1, t2, attention_threshold)
    return attention_dict