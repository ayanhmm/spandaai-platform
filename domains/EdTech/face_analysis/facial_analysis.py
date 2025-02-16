from batch_face import RetinaFace, SixDRep
import cv2
import numpy as np
import torch
import math
import pandas as pd
from tqdm import tqdm


detector = RetinaFace(gpu_id=-1)
head_pose_estimator = SixDRep(gpu_id=-1)
pitch_range = (-40, 30)
yaw_range = (-30, 30)


def inference_batch(batch):
    '''
    Runs face detection and head pose estimation on a batch of frames.
    '''
    global detector
    batch_numpy = np.array(batch)

    with torch.no_grad():
        batch_face_object = detector(batch_numpy, return_dict=True)
        
        if not any(batch_face_object):
            return [], []

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
                f = cv2.putText(f, 'Unfocused', c1, font, font_scale, red, thickness=1)
        marked_batch.append(f)
    return marked_batch

def process_batch_data(marked_batch, writer, batch_face_dict):
    for frame in marked_batch:
        writer.write(frame)
    
    processed_data = []
    for frame in range(len(batch_face_dict)):
        frame_data = {'faces': []}
        for face in batch_face_dict[frame]['faces']:
            processed_face = {
                'box': face['box'].tolist() if isinstance(face['box'], np.ndarray) else list(face['box']),
                'kps': face['kps'].tolist() if isinstance(face['kps'], np.ndarray) else list(face['kps']),
                'score': float(face['score']),
                'head_pose': {k: float(v) for k, v in face['head_pose'].items()},
                'focused': face.get('focused', False)
            }
            frame_data['faces'].append(processed_face)
        processed_data.append(frame_data)
    
    return processed_data

def focus_detection(batch_face_object):
    for frame_face_object in batch_face_object:
        for face in range(len(frame_face_object)):
            pitch = frame_face_object[face]['head_pose']['pitch'] < max(pitch_range) and frame_face_object[face]['head_pose']['pitch'] > min(pitch_range)
            yaw = frame_face_object[face]['head_pose']['yaw'] < max(yaw_range) and frame_face_object[face]['head_pose']['yaw'] > min(yaw_range)
            frame_face_object[face]['focused'] = pitch and yaw
    return batch_face_object

def process_video(input_video: str, output_video: str | None = None, batch_size=10, output_fps=4):
    """
    Processes the video for engagement analysis and returns both engagement_results and attention_dict.
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
                        "score": float(face['score']),
                        "head_pose": {k: float(v) for k, v in face['head_pose'].items()},
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

    # Generate attention_dict directly from engagement_results
    attention_dict = attention_from_direction(engagement_results)

    return engagement_results, attention_dict

def engagement_from_focus(engagement_results):
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
    
    for frame in tqdm(engagement_results):
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
    df = pd.DataFrame(engagement)
    avg_row = df.mean().to_dict()
    avg_df = pd.DataFrame(avg_row, index=[0])
    print(avg_df.iloc[-1].value_counts(dropna=False))
    avg_df.to_csv('engagement_results.csv')
    return avg_df

def get_directions(engagement_results):
    directions = {}
    for frame in engagement_results:
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

def attention_from_direction(engagement_results, t1=2000, t2=4000, attention_threshold=0.7):
    """
    Computes attention spans based on head directions from engagement_results directly.
    """
    direction_data = {}
    for frame in engagement_results:
        frame_time = float(frame['time'])
        direction_data[frame_time] = sum(
            [1 if face['head_pose']['yaw'] > min(yaw_range) and face['head_pose']['yaw'] < max(yaw_range)
             else 0 for face in frame['faces']]
        ) / len(frame['faces']) if frame['faces'] else 0

    timestamps = sorted(list(direction_data.keys()))
    x = 0
    y = 0
    attention_dict = {'focused': [], 'mostly focused': [], 'partially focused': [], 'unfocused': []}

    while y < len(timestamps) and timestamps[y] - timestamps[x] <= t1:
        y += 1

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

    return attention_dict