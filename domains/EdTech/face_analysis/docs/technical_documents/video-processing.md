**Video Processing Pipeline**

Our video processing framework utilizes OpenCV to ingest input video streams, processing them frame-by-frame for computational efficiency. Given the high frame rate of standard video formats, we implement frame rate reduction to a user-defined output FPS, thereby optimizing performance while retaining key temporal features necessary for inference.

### **Face Detection and Head Pose Estimation**
The core of our inference pipeline consists of two deep learning models:

1. **Face Detection - RetinaFace**
   - RetinaFace is a state-of-the-art single-stage face detector that employs a multi-task learning approach to simultaneously predict facial bounding boxes, five facial keypoints (eyes, nose, mouth corners), and confidence scores.
   - It utilizes a ResNet-50 backbone for feature extraction, leveraging Feature Pyramid Networks (FPN) and context modules to enhance detection accuracy across varying scales and lighting conditions.
   - The detection output comprises:
     - `box`: Bounding box coordinates (x, y, w, h) for each detected face.
     - `kps`: Key points (x, y) for the left eye, right eye, nose, and mouth corners.
     - `score`: Confidence score for the detected face.

2. **Head Pose Estimation - SixDRepNet**
   - SixDRepNet is a robust head pose estimation network designed to predict three Euler angles—pitch, yaw, and roll—from cropped face images.
   - It employs a ResNet-50 backbone followed by an MLP-based regression head, trained on the 300W-LP dataset.
   - The predicted head pose angles are formatted as:
     - `head_pose`: Dictionary containing:
       - `pitch`: Vertical tilt of the head (-90° to 90°)
       - `yaw`: Horizontal turn (-90° to 90°)
       - `roll`: Rotational tilt around the z-axis (-90° to 90°)

### **Inference Output Representation**
The processed video frames and their corresponding inference results are stored in a structured JSON format:

```json
[
    {
        "time": 1500,  // Timestamp in milliseconds
        "faces": [
            {
                "box": [x1, y1, x2, y2],
                "kps": [[x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5]],
                "score": 0.98,
                "head_pose": {"pitch": -5.2, "yaw": 12.3, "roll": 1.7}
            }
        ]
    }
]
```
The extracted faces can optionally be streamed with overlaid bounding boxes and head pose annotations for real-time visualization.

---

### **Head Direction Classification**
Following inference, we perform post-processing on the JSON output to generate a simplified format for easier analysis.

1. **Transformation Process**
   - The raw JSON is parsed, discarding unique face identifiers and retaining timestamped head direction labels.
   - Head pose angles are mapped into categorical labels (`"Straight"`, `"Left"`, `"Right"`, `"Up"`, `"Down"`) based on predefined angle thresholds.

2. **Simplified JSON Output**
   - The output is structured as:

```json
{
    "1500": ["Straight", "Left", "Right"],
    "1600": ["Straight", "Straight", "Up"]
}
```
Each timestamp corresponds to a list representing detected faces’ head orientations, making the dataset more readable and interpretable.

---

### **Attention Analysis Algorithm**

The attention scoring algorithm processes the transformed JSON to determine focus levels. This involves a statistical analysis of student attention across a moving time window.

1. **Parameters**
   - `t1`: Lower time threshold for mild distraction.
   - `t2`: Upper time threshold for severe distraction.
   - `attention_threshold`: Minimum required percentage of students looking straight.

2. **Computation**
   - Each timestamp is assigned an attention score, calculated as the fraction of students maintaining a `"Straight"` head direction.
   - The score is smoothed using a moving average filter.
   - If the average score falls below `attention_threshold`, distraction tracking is initiated:
     - If duration < `t1`, it is classified as **brief distraction**.
     - If `t1` ≤ duration < `t2`, it is classified as **moderate distraction**.
     - If duration ≥ `t2`, it is classified as **severe distraction**.

3. **Final Representation**
   - The final attention analysis results are stored in:

```json
{
    "1500": {"attention_score": 0.85, "distraction_level": "None"},
    "1600": {"attention_score": 0.60, "distraction_level": "Moderate"},
    "1700": {"attention_score": 0.40, "distraction_level": "Severe"}
}
```
This structured output enables real-time monitoring and retrospective analysis of classroom attention dynamics.

---

### **Libraries & Dependencies**
The implementation relies on the following libraries:
- **OpenCV** (`cv2`): Frame extraction and image preprocessing.
- **Torch** (`torch`): Deep learning framework for RetinaFace and SixDRepNet.
- **RetinaFace (InsightFace)**: Facial detection and keypoint extraction.
- **SixDRepNet**: Head pose estimation.
- **NumPy** (`numpy`): Data manipulation and statistical analysis.
- **JSON** (`json`): Storing and processing inference results.

This pipeline provides an end-to-end solution for video-based attention analysis, combining robust deep learning models with efficient video processing techniques.

