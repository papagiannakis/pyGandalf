import numpy as np
from scipy.spatial.transform import Rotation as R_scipy
from pyGandalf.utilities.GA.GAutils import matrix_to_motor
def multivector_to_vector32(mv):
    return np.array([float(mv[i]) for i in range(2**5)], dtype=np.float32)

def build_motor_from_vertex_normal(vertex, normal):
    # Normalize the normal vector
    normal = np.asarray(normal, dtype=np.float64)
    vertex = np.asarray(vertex, dtype=np.float64)
    if np.isnan(normal).any():
        normal = np.array([0.0, 1.0, 0.0], dtype=np.float64)  # default up vector
    else:
        # Flip Y if negative
        if normal[1] < 0:
            normal[1] *= -1

        # Normalize safely
        norm = np.linalg.norm(normal)
        if norm < 1e-6:
            normal = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        else:
            normal = normal / norm
        
    # Rotation: (0,1,0) -> normal
    source = np.array([0, 1, 0])
    rot, _ = R_scipy.align_vectors([normal], [source])
    R = rot.as_matrix()

    # SE(3) transformation matrix
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = vertex

    motor = matrix_to_motor(M, method = 'CGA')
    return multivector_to_vector32(motor)
