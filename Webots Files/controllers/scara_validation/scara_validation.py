from controller import Robot

"""
This is just for giving pre defined join values and
manually noting down their resulting TCP position values
using the supervisor.
"""

robot = Robot()

timestep = int(robot.getBasicTimeStep())

shoulder = robot.getDevice("base_arm_motor")
elbow = robot.getDevice("arm_motor")
shaft_rotation = robot.getDevice("shaft_rotation_motor")
shaft_linear = robot.getDevice("shaft_linear_motor")


#fixed configuration
q1 = 0.0
q2 = 0.0    #q2 > 0: +ve
q4 = -0.1

shoulder.setPosition(q1)
elbow.setPosition(q2)
shaft_rotation.setPosition(0.0)
shaft_linear.setPosition(q4)

#similar to scara_simple except it breaks
for _ in range(100):
    if robot.step(timestep) == -1:
        break

print("Robot reached test configuration:")
print(f"q1 = {q1:.4f} rad")
print(f"q2 = {q2:.4f} rad")
print(f"q4 = {q4:.4f} rad")



"""
VALIDATION TESTS:

q1:

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.0000 rad
q4 = 0.0000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in world frame: x=0.624, y=0.000, z=0.182
TCP in ARM frame: x=0.6245, y=0.0000, z=0.1819

Robot reached test configuration:
q1 = 0.5000 rad
q2 = 0.0000 rad
q4 = 0.0000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in world frame: x=0.555, y=0.271, z=0.182
TCP in ARM frame: x=0.5554, y=0.2706, z=0.1820

Robot reached test configuration:
q1 = -0.5000 rad
q2 = 0.0000 rad
q4 = 0.0000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in ARM frame: x=0.5554, y=-0.2706, z=0.1819
TCP in world frame: x=0.555, y=-0.271, z=0.182


q2:

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.2000 rad
q4 = 0.0000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in world frame: x=0.620, y=0.051, z=0.182
TCP in ARM frame: x=0.6204, y=0.0507, z=0.1819

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.8300 rad
q4 = 0.0000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in world frame: x=0.545, y=0.189, z=0.182
TCP in ARM frame: x=0.5454, y=0.1894, z=0.1819


q4:

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.0000 rad
q4 = -0.2000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in ARM frame: x=0.6245, y=0.0000, z=0.0093
TCP in world frame: x=0.625, y=0.000, z=0.009

Robot reached test configuration:
q1 = 0.0000 rad
q2 = 0.0000 rad
q4 = -0.1000 rad
INFO: 'scara_validation' controller exited successfully.
TCP in ARM frame: x=0.6245, y=-0.0000, z=0.0819
TCP in world frame: x=0.624, y=-0.000, z=0.082

"""