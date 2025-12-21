import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/imrcmini2/ros2_ws/src/ros_pad_cmd_vel/install/imrc_pad_cmd_vel'
