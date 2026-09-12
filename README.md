# AMCL Localization — TurtleBot3 (turtlebot3_world)

## 1. Project Overview

This project configures **AMCL (Adaptive Monte Carlo Localization)** to localize a TurtleBot3 robot within a previously built map of `turtlebot3_world`. The map used here was generated in a separate SLAM Toolbox mapping project and is reused as-is.

The goal is to prove that AMCL can:
- Load a pre-built static map via `map_server`
- Accept an initial pose estimate
- Converge its particle filter onto the robot's true pose
- Continue tracking the robot's pose reliably as it drives

## 2. Package Structure

```
amcl_localization_demo/
├── config/
│   └── amcl.yaml
├── launch/
│   └── amcl_launch.py
├── map/
│   ├── turtlebot3_world_map.yaml
│   └── turtlebot3_world_map.pgm
├── demo/
│   └── amcl_localization_demo.mp4
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 3. Build Instructions

Clone into your ROS 2 Jazzy workspace:

```bash
cd ~/ros2_ws/src
git clone https://github.com/yassinnmhmoudd/amcl_localization_yassin_bassem.git amcl_localization_demo
```

Install dependencies:

```bash
sudo apt update
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-turtlebot3*
```

Set the TurtleBot3 model:

```bash
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
```

Build:

```bash
cd ~/ros2_ws
colcon build --packages-select amcl_localization_demo
source install/setup.bash
```

## 4. Commands Used to Launch the Simulator and AMCL

Single command launches everything — `turtlebot3_world` in Gazebo, `map_server`, `amcl`, and `lifecycle_manager`:

```bash
ros2 launch amcl_localization_demo amcl_launch.py
```

The `lifecycle_manager` automatically configures and activates both `map_server` and `amcl` — no manual lifecycle commands are needed. Confirm both are active:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

Both should report `active`.

## 5. RViz Configuration

Launch RViz:

```bash
rviz2
```

Set **Fixed Frame → `map`** (set this *before* using 2D Pose Estimate — AMCL rejects pose estimates given in any other frame).

Add the following displays:
- `RobotModel`
- `LaserScan` (topic `/scan`)
- `TF`
- `Map` (topic `/map`)
- `ParticleCloud` (topic `/particle_cloud`)

## 6. Screenshot and Observations for the Correct Initial Pose

After giving AMCL a **wrong** initial pose (via 2D Pose Estimate), the LaserScan does not align with the map's geometry, and the terminal shows AMCL processing a pose far from the robot's actual location.

After giving AMCL the **correct** initial pose (matching the robot's real position and heading), the terminal confirms the pose was accepted:

```
[amcl]: initialPoseReceived
[amcl]: Setting pose (...): x y theta
```

Once correct, the LaserScan aligns with the robot's real surroundings, and the particle filter's output (see `/particle_cloud` and `/amcl_pose`) converges to a tight cluster around the true pose instead of a wide spread.

*(Screenshot to be inserted here.)*

## 7. Screenshot Showing the Particle Cloud

The particle cloud can be inspected directly from the topic:

```bash
ros2 topic echo /particle_cloud --once
```

This returns an array of individual particle poses and weights. Before convergence (wrong/initial pose), particle positions are spread across a wide range of x/y values. After convergence (correct pose), particle positions cluster tightly together.

*(Screenshot to be inserted here.)*

> **Note:** in this environment, RViz's `Map` and `ParticleCloud` visual displays fail to render (GLSL shader compatibility issue with the sandbox's software renderer — `indexed_8bit_image.vert/frag` compile errors). Both topics publish valid, correctly-typed data confirmed via `ros2 topic echo` and `ros2 topic info`; only the visual rendering of these two specific displays is affected. See section 11 for details.

## 8. TF Tree Screenshot

The TF tree can be inspected with:

```bash
ros2 run tf2_ros tf2_echo map odom
```

Once AMCL has received a valid initial pose, this returns a live `map → odom` transform, confirming the full chain `map → odom → base_footprint → base_scan` is connected and consistent.

*(Screenshot / `view_frames` PDF to be inserted here.)*

## 9. Required Topic and Transform Outputs

Confirm sensor data is live:

```bash
ros2 topic echo /scan --once
ros2 topic echo /odom --once
```

Confirm AMCL's outputs:

```bash
ros2 topic info /particle_cloud
# Type: nav2_msgs/msg/ParticleCloud

ros2 topic echo /amcl_pose --once
```

Confirm the transform tree:

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_footprint
```

## 10. Demo Video Link

[Demo video](demo/amcl_localization_demo.mp4)

*(Or replace with a hosted link, e.g. YouTube/Drive, once uploaded.)*

## 11. Common Problems Faced and How They Were Solved

- **`AMCL cannot publish a pose or update the transform`** — expected behavior. AMCL will not publish `map → odom` until it receives an initial pose via `/initialpose` (RViz's 2D Pose Estimate, or published manually). Resolved by giving an initial pose estimate.

- **`Ignoring initial pose in frame "odom"; initial poses must be in the global frame, "map"`** — occurred because RViz's Fixed Frame was still set to `odom` when 2D Pose Estimate was clicked, so the pose was stamped in the wrong frame. Resolved by setting Fixed Frame to `map` *before* clicking 2D Pose Estimate (the red "frame does not exist" warning can be safely ignored at that point).

- **`Frame [map] does not exist`** — expected until AMCL processes a valid initial pose and begins broadcasting `map → odom`. Resolved once the correct-frame pose estimate above was given.

- **Map display renders as solid yellow / GLSL shader errors (`indexed_8bit_image.vert/frag`)** — confirmed to be a rendering limitation of the remote VNC/software-rendering environment, not a data or configuration issue. `map_server` logs confirmed the map loaded correctly (`175 X 103 map @ 0.05 m/cell`), and `amcl` confirmed receiving it. Worked around by verifying localization through `/particle_cloud` and `/amcl_pose` topic data via terminal instead of the RViz visual.

- **`ParticleCloud` display shows "No description" in RViz** — same root cause as above (rendering-environment limitation), not a message-type mismatch; `ros2 topic info /particle_cloud` confirmed the correct type (`nav2_msgs/msg/ParticleCloud`). Worked around the same way, via terminal topic inspection.

- **Failed initial push to GitHub (`fetch first` / `non-fast-forward` / `refusing to merge unrelated histories`)** — occurred because the GitHub repo was created with initial content while the local repo had a separate, unrelated commit history. Resolved with:
  ```bash
  git pull origin main --no-rebase --allow-unrelated-histories
  git push -u origin main
  ```
