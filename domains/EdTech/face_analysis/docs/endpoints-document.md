# Facial Analysis API Documentation

This API provides endpoints for analyzing facial engagement and attention in videos. It utilizes computer vision models to detect faces, estimate head poses, and determine if subjects are focused or looking away. The analysis is performed through a pipeline that processes videos, analyzes head directions, and calculates attention spans.

## Base URL

```
http://localhost:9005
```

## Endpoints

### 1. Process Video

Processes a video file to detect faces and analyze head poses.

**URL**: `/process-video`  
**Method**: `POST`  
**Content-Type**: `multipart/form-data`

**Form Parameters**:
- `file`: The video file to process (required)
- `batch_size`: Number of frames to process in each batch (default: 10)
- `output_fps`: Frame rate of the processed output (default: 4)

**Response**:
```json
[
  {
    "time": 1000.0,
    "faces": [
      {
        "box": [100, 50, 200, 150],
        "score": 0.98,
        "head_pose": {
          "pitch": 5.2,
          "yaw": -3.1,
          "roll": 0.5
        },
        "focused": true
      }
    ]
  },
  ...
]
```

**Response Fields**:
- `time`: Timestamp in milliseconds
- `faces`: Array of detected faces with:
  - `box`: Face bounding box coordinates [x1, y1, x2, y2]
  - `score`: Detection confidence score (0-1)
  - `head_pose`: Head orientation in degrees:
    - `pitch`: Up/down angle
    - `yaw`: Left/right angle
    - `roll`: Tilt angle
  - `focused`: Whether the face is determined to be focused based on head pose

### 2. Direction from JSON

Converts detailed face detection data into directional information (straight, left, right, up, down).

**URL**: `/direction-from-json`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
Same format as the response from `/process-video`.

**Response**:
```json
{
  "1000.0": ["straight", "left"],
  "1250.0": ["up", "straight"],
  ...
}
```

**Response Fields**:
- Object with timestamps as keys
- Each timestamp maps to an array of directions for each detected face

### 3. Attention from Direction

Calculates attention spans based on directional data.

**URL**: `/attention-from-direction`  
**Method**: `POST`  
**Content-Type**: `multipart/form-data`

**Form Parameters**:
- `data`: JSON string of direction data (required)
- `t1`: Threshold for "mostly focused" in milliseconds (default: 2000)
- `t2`: Threshold for "partially focused" in milliseconds (default: 4000)
- `thresh`: Minimum threshold for focus detection (default: 0.7)

**Response**:
```json
{
  "focused": [[1000, 5000], [10000, 15000]],
  "mostly focused": [[5000, 6500]],
  "partially focused": [[6500, 9000]],
  "unfocused": [[15000, 20000]]
}
```

**Response Fields**:
- `focused`: Array of time spans where subjects were fully focused
- `mostly focused`: Array of time spans with high attention
- `partially focused`: Array of time spans with moderate attention
- `unfocused`: Array of time spans with low or no attention

### 4. Complete Attention Pipeline

Executes the full pipeline from video upload to attention level calculation in one request.

**URL**: `/attention_pipeline`  
**Method**: `POST`  
**Content-Type**: `multipart/form-data`

**Form Parameters**:
- `file`: The video file to process (required)
- `batch_size`: Number of frames to process in each batch (default: 10)
- `output_fps`: Frame rate of the processed output (default: 4)
- `t1`: Threshold for "mostly focused" in milliseconds (default: 2000)
- `t2`: Threshold for "partially focused" in milliseconds (default: 4000)
- `thresh`: Minimum threshold for focus detection (default: 0.7)

**Response**:
Same format as `/attention-from-direction` response.

## Technical Details

### Focus Detection Criteria

- A face is considered "focused" when:
  - Pitch (up/down) angle is within the configured range (typically ±15-20°)
  - Yaw (left/right) angle is within the configured range (typically ±15-20°)

### Attention Categories

1. **Focused**: Subject is consistently looking straight ahead
2. **Mostly Focused**: Brief periods of distraction less than `t1` milliseconds
3. **Partially Focused**: Moderate periods of distraction between `t1` and `t2` milliseconds
4. **Unfocused**: Extended periods of distraction longer than `t2` milliseconds

### Processing Pipeline

1. Face detection using RetinaFace model
2. Head pose estimation using SixDRep model
3. Focus detection based on head pose angles
4. Direction classification (straight, left, right, up, down)
5. Attention span calculation based on focus continuity

## Error Handling

All endpoints return HTTP 500 with an error message if processing fails:

```json
{
  "detail": "Processing failed: [specific error message]"
}
```

## Configuration

The system uses environment variables for configuration:
- `GPU`: GPU ID for model acceleration
- `YAW_HIGH`/`YAW_LOW`: Maximum/minimum acceptable yaw angles
- `PITCH_HIGH`/`PITCH_LOW`: Maximum/minimum acceptable pitch angles