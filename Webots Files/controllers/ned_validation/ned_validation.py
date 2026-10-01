from controller import Robot

"""
This is just for giving pre defined join values and
manually noting down their resulting TCP position values
using the supervisor.
"""

robot = Robot()

timestep = int(robot.getBasicTimeStep())


joint_1 = robot.getDevice("joint_1")
joint_2 = robot.getDevice("joint_2")
joint_3 = robot.getDevice("joint_3")

#fixed configuration
q1 = 0.0
q2 = 0.0
q3 = 0.2    #q3 > 0

#set the fixed config
joint_1.setPosition(q1)
joint_2.setPosition(q2)
joint_3.setPosition(q3)

#similar to ned_simple except it breaks
for _ in range(100):
    if robot.step(timestep) == -1:
        break

print("Robot reached test configuration:")
print(f"q1 = {q1:.4f} rad")
print(f"q2 = {q2:.4f} rad")
print(f"q3 = {q3:.4f} rad")

"""
VALIDATION TESTS:

q1:

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.0000 rad
q3 = 0.5000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in world frame: x=0.000, y=0.229, z=0.310
TCP in ARM frame: x=0.0001, y=0.2291, z=0.3101

Robot reached test configuration:
q1 = 0.5000 rad
q2 = 0.0000 rad
q3 = 0.5000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in world frame: x=-0.110, y=0.201, z=0.310
TCP in ARM frame: x=-0.1097, y=0.2011, z=0.3101

Robot reached test configuration:
q1 = -0.5000 rad
q2 = 0.0000 rad
q3 = 0.5000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in world frame: x=0.110, y=0.201, z=0.310
TCP in ARM frame: x=0.1099, y=0.2010, z=0.3101



q2:

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.3000 rad
q3 = 0.5000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in world frame: x=0.000, y=0.260, z=0.236
TCP in ARM frame: x=0.0001, y=0.2599, z=0.2362

Robot reached test configuration:
q1 = 0.0000 rad
q2 = -0.3000 rad
q3 = 0.5000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in ARM frame: x=0.0002, y=0.1779, z=0.3717
TCP in world frame: x=0.000, y=0.178, z=0.372



q3:       q3>0

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.0000 rad
q3 = 0.8000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in world frame: x=0.000, y=0.195, z=0.250
TCP in ARM frame: x=0.0001, y=0.1951, z=0.2497

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.0000 rad
q3 = 0.2000 rad
INFO: 'ned_validation' controller exited successfully.
TCP in ARM frame: x=0.0002, y=0.2437, z=0.3780
TCP in world frame: x=0.000, y=0.244, z=0.378

"""