from controller import Robot

WAIST = -0.7854
SHOULDER = 0.3504
ELBOW = 0.3554

robot = Robot()
timestep = int(robot.getBasicTimeStep())

waist = robot.getDevice("joint_1")
shoulder = robot.getDevice("joint_2")
elbow = robot.getDevice("joint_3")

waist.setPosition(WAIST)
shoulder.setPosition(SHOULDER)
elbow.setPosition(ELBOW)

while robot.step(timestep) != -1:
    pass
