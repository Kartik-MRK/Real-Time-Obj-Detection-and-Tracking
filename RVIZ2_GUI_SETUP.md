# RViz2 Setup and GUI Configuration Guide

## Scope
This document is only for RViz2 setup and GUI configuration for your tracking demo.

It covers:
- Installing RViz2 on Ubuntu 22.04 with ROS2 Humble
- Launching RViz2
- Exact GUI changes to apply for a clean demo layout
- QoS fixes inside RViz2 if topics are not visible
- Saving and reusing RViz2 configuration

## 1. Prerequisites
- Ubuntu 22.04
- ROS2 Humble installed
- A running publisher for these topics:
  - `/tracking/image_annotated` (`sensor_msgs/Image`)
  - `/tracking/markers` (`visualization_msgs/MarkerArray`)

## 2. Install RViz2
Run the following commands:

```bash
sudo apt update
sudo apt install -y ros-humble-rviz2 ros-humble-rqt ros-humble-tf2-tools
source /opt/ros/humble/setup.bash
```

Verify:

```bash
rviz2 --help
```

## 3. Launch RViz2
Basic launch:

```bash
source /opt/ros/humble/setup.bash
rviz2
```

## 4. RViz2 GUI Changes (Step by Step)

## 4.1 Keep Required Panels Open
From the top menu, open `Panels` and ensure these are visible:
- Displays
- Views
- Tool Properties
- Selection
- Time

Recommended layout:
- Left: Displays
- Right: Views
- Bottom: Time
- Center: Render panel

## 4.2 Global Options (Mandatory)
In `Displays`, click `Global Options` and set:
- `Fixed Frame`: `map`
- If `map` is unavailable, use `odom`
- If `odom` is unavailable, use `base_link`
- `Frame Rate`: `30`
- `Background Color`: dark gray (for projector readability)

## 4.3 Add Image Display for Annotated Stream
1. Click `Add` in Displays.
2. Select `By display type` -> `Image`.
3. Rename display to `Tracking Image`.
4. Set:
   - `Topic`: `/tracking/image_annotated`
   - `Queue Size`: `5`
   - `Reliability Policy`: `Best Effort`
   - `Durability Policy`: `Volatile`
   - `History Policy`: `Keep Last`
   - `Depth`: `5`
   - `Transport Hint`: `raw`

Expected result: live annotated image appears in render panel.

## 4.4 Add MarkerArray Display for Tracking Output
1. Click `Add`.
2. Select `By display type` -> `MarkerArray`.
3. Rename display to `Tracking Markers`.
4. Set:
   - `Marker Topic`: `/tracking/markers`
   - `Queue Size`: `100`
   - `Reliability Policy`: `Reliable`
   - `Durability Policy`: `Volatile`
   - `History Policy`: `Keep Last`
   - `Depth`: `10`

Expected result: tracking markers, IDs, or overlays update in sync with motion.

## 4.5 Optional TF Display (Recommended)
1. Click `Add` -> `TF`.
2. Set:
   - `Show Axes`: `true`
   - `Show Arrows`: `true`
   - `Show Names`: `false` (reduces clutter)
   - `Marker Scale`: `0.3` to `0.5`

Use this only if it improves explanation during presentation.

## 4.6 Optional Grid Display
1. Click `Add` -> `Grid`.
2. Set:
   - `Reference Frame`: same as Fixed Frame
   - `Cell Size`: `1.0`
   - `Plane Cell Count`: `20`
   - `Alpha`: `0.35`

Keep it subtle so it does not hide markers.

## 4.7 View Controller Tuning for Demo
In `Views` panel:
- `Current View`: `Orbit` (or `TopDownOrtho` if your scene is map-like)
- Adjust focal point to center the content
- Set distance so markers and image are readable from audience distance
- Avoid changing camera constantly during demo

## 5. QoS Fixes in RViz2 GUI (If Nothing Appears)
If data is not visible, do these changes directly in RViz2:

## 5.1 Image Topic Troubleshooting
For `Tracking Image` display:
1. Confirm `Topic` is `/tracking/image_annotated`.
2. Switch `Reliability Policy`:
   - If currently `Best Effort`, try `Reliable`.
   - If currently `Reliable`, try `Best Effort`.
3. Increase `Queue Size` from `5` to `10`.
4. Toggle display `Enabled` off and on.

## 5.2 Marker Topic Troubleshooting
For `Tracking Markers` display:
1. Confirm `Marker Topic` is `/tracking/markers`.
2. Switch `Reliability Policy` once.
3. Increase `Depth` to `20`.
4. Ensure marker namespaces are enabled.

## 5.3 Fixed Frame Issues
If RViz shows frame errors:
1. Change `Fixed Frame` from `map` to `odom`.
2. If still red, change to `base_link`.
3. Keep the first frame that shows status as `OK`.

## 6. Save and Reuse RViz2 Config
Save profile:
1. Click `File` -> `Save Config As...`
2. Save as `tracking_demo.rviz`
3. Example location: `~/rviz/tracking_demo.rviz`

Reload profile later:
1. `File` -> `Open Config...`
2. Select `tracking_demo.rviz`

Launch directly with saved profile:

```bash
source /opt/ros/humble/setup.bash
rviz2 -d ~/rviz/tracking_demo.rviz
```

## 7. 60-Second Pre-Demo Checklist
- RViz2 started successfully
- Correct config profile loaded
- `Fixed Frame` valid (`map`, `odom`, or `base_link`)
- `Tracking Image` display shows live `/tracking/image_annotated`
- `Tracking Markers` display shows live `/tracking/markers`
- No red errors in Displays status
- Panels visible: Displays, Views, Tool Properties, Selection, Time
- Camera/view angle fixed and readable for presentation
- One quick movement test confirms markers update in real time

## 8. Minimal Command Reference
```bash
source /opt/ros/humble/setup.bash
rviz2
```

```bash
source /opt/ros/humble/setup.bash
rviz2 -d ~/rviz/tracking_demo.rviz
```
