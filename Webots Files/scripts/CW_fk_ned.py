import math


# --------------------------------------------------
# Ned geometry
# --------------------------------------------------

# Shoulder height above the ARM frame
H = 0.1065 + 0.0650

# Shoulder -> elbow offset
A = 0.221
B = 0.012

# Elbow -> TCP offset
U = 0.0318503164
V = 0.22999994


def fk_ned(q1, q2, q3):
    """
    Forward kinematics for the first three active
    joints of ned.
    Just like the one in ik_exact.py

    Parameters:
    
    q1: Waist joint angle, radians.

    q2: Shoulder joint angle, radians.

    q3: Elbow joint angle, radians.

    Returns:
    
    x, y, z: TCP position in the Ned ARM frame, metres.
    """

    #combine the fixed shoulder to elbow offset
    #with the elbow to TCP vector rotated by q3
    wx = A + U * math.cos(q3) - V * math.sin(q3)
    wy = B + U * math.sin(q3) + V * math.cos(q3)

    #apply the shoulder rotation q2
    #r is the horizontal distance from the q1 axis.
    r = wy * math.cos(q2) + wx * math.sin(q2)
    z = H - wy * math.sin(q2) + wx * math.cos(q2)

    #apply the waist rotation q1
    #ned has q1 = 0 pointing along +Y.
    x = -r * math.sin(q1)
    y = r * math.cos(q1)

    return x, y, z
    
 
if __name__ == "__main__":
    test_data = [
    # (q1, q2, q3, Webots x, Webots y, Webots z)
    (0.0, 0.0, 0.5,  0.0000, 0.2290, 0.3100),
    (0.5, 0.0, 0.5, -0.1097, 0.2011, 0.3101),
    (-0.5, 0.0, 0.5, 0.1099, 0.2010, 0.3101),
    (0.0, 0.3, 0.5, 0.0001, 0.2599, 0.2362),
    (0.0, -0.3, 0.5, 0.0002, 0.1779, 0.3717),
    (0.0, 0.0, 0.8, 0.0001, 0.1951, 0.2497),
    (0.0, 0.0, 0.2, 0.0002, 0.2437, 0.3780),
    ]

    for q1, q2, q3, wb_x, wb_y, wb_z in test_data:

        fk_x, fk_y, fk_z = fk_ned(q1, q2, q3)

        error = math.sqrt(
            (fk_x - wb_x) ** 2 +
            (fk_y - wb_y) ** 2 +
            (fk_z - wb_z) ** 2
        )

        print(
            f"q1={q1:+.4f}, "
            f"q2={q2:+.4f}, "
            f"q3={q3:+.4f}"
        )

        print(
            f"  FK:     x={fk_x:.4f}, "
            f"y={fk_y:.4f}, "
            f"z={fk_z:.4f}"
        )

        print(
            f"  Webots: x={wb_x:.4f}, "
            f"y={wb_y:.4f}, "
            f"z={wb_z:.4f}"
        )

        print(f"  Error:  {error:.6f} m")
        print()
        
        """
        q1=+0.0000, q2=+0.0000, q3=+0.5000
          FK:     x=-0.0000, y=0.2291, z=0.3102
          Webots: x=0.0000, y=0.2290, z=0.3100
          Error:  0.000216 m
        
        q1=+0.5000, q2=+0.0000, q3=+0.5000
          FK:     x=-0.1098, y=0.2011, z=0.3102
          Webots: x=-0.1097, y=0.2011, z=0.3101
          Error:  0.000169 m
        
        q1=-0.5000, q2=+0.0000, q3=+0.5000
          FK:     x=0.1098, y=0.2011, z=0.3102
          Webots: x=0.1099, y=0.2010, z=0.3101
          Error:  0.000121 m
        
        q1=+0.0000, q2=+0.3000, q3=+0.5000
          FK:     x=-0.0000, y=0.2599, z=0.2363
          Webots: x=0.0001, y=0.2599, z=0.2362
          Error:  0.000134 m
        
        q1=+0.0000, q2=-0.3000, q3=+0.5000
          FK:     x=-0.0000, y=0.1779, z=0.3717
          Webots: x=0.0002, y=0.1779, z=0.3717
          Error:  0.000200 m
        
        q1=+0.0000, q2=+0.0000, q3=+0.8000
          FK:     x=-0.0000, y=0.1951, z=0.2497
          Webots: x=0.0001, y=0.1951, z=0.2497
          Error:  0.000100 m
        
        q1=+0.0000, q2=+0.0000, q3=+0.2000
          FK:     x=-0.0000, y=0.2437, z=0.3780
          Webots: x=0.0002, y=0.2437, z=0.3780
          Error:  0.000206 m




        """
        
