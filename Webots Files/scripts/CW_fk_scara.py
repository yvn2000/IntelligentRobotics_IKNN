import math


def fk_scara(q1, q2, q4):
    """
    Forward kinematics for the SCARA robot.

    Parameters:
        q1 : base_arm_motor angle (radians)
        q2 : arm_motor angle (radians)
        q4 : shaft_linear_motor position (metres)

    Returns:
        (x, y, z) TCP position in the ARM frame.
    """

    # Joint 1 -> Joint 2
    x1 = 0.310
    y1 = 0.005
    z1 = -0.004

    # Joint 2 -> TCP
    x2 = 0.2545
    y2 = -0.005
    z2 = q4 - 0.034

    # Rotate Joint 2 -> TCP by q2
    x2_rot = x2 * math.cos(q2) - y2 * math.sin(q2)
    y2_rot = x2 * math.sin(q2) + y2 * math.cos(q2)

    # Combine the two sections
    x_arm = x1 + x2_rot
    y_arm = y1 + y2_rot
    z_arm = z1 + z2

    # Rotate the whole arm by q1
    x_rot = x_arm * math.cos(q1) - y_arm * math.sin(q1)
    y_rot = x_arm * math.sin(q1) + y_arm * math.cos(q1)

    # Add the base -> Joint 1 translation
    x = 0.060 + x_rot
    y = 0.000 + y_rot
    z = 0.220 + z_arm

    return x, y, z


def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2 +
        (p1[2] - p2[2]) ** 2
    )


tests = [
    # q1, q2, q4, measured TCP from Webots
    (0.0,  0.0, 0.0,   (0.6245,  0.0000, 0.1819)),

    # q1 tests
    (0.5,  0.0, 0.0,   (0.5554,  0.2706, 0.1820)),
    (-0.5, 0.0, 0.0,   (0.5554, -0.2706, 0.1819)),

    # q2 tests
    (0.0,  0.2, 0.0,   (0.6204,  0.0507, 0.1819)),
    (0.0,  0.83, 0.0,  (0.5454,  0.1894, 0.1819)),

    # q4 tests
    (0.0,  0.0, -0.1,  (0.6245,  0.0000, 0.0819)),
    (0.0,  0.0, -0.15, (0.6245,  0.0000, 0.0319)),
    #q4 = -0.175, -0.200 have been deliberately left out so that it doesn't mess with it
]


for q1, q2, q4, measured in tests:

    predicted = fk_scara(q1, q2, q4)
    error = distance(predicted, measured)

    print(f"q1={q1:.3f}, q2={q2:.3f}, q4={q4:.3f}")
    print(
        f"FK:      x={predicted[0]:.4f}, "
        f"y={predicted[1]:.4f}, "
        f"z={predicted[2]:.4f}"
    )
    print(
        f"Webots:  x={measured[0]:.4f}, "
        f"y={measured[1]:.4f}, "
        f"z={measured[2]:.4f}"
    )
    print(f"Error: {error:.6f} m")
    print()