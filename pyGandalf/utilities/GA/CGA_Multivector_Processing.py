import numpy as np
from scipy.spatial.transform import Rotation as R_scipy
from pyGandalf.utilities.GA.GAutils import matrix_to_motor
def multivector_to_vector32(mv):
    """
    Παίρνει Clifford multivector (π.χ. motor) και επιστρέφει 32-διάστατο NumPy διάνυσμα.
    Η σειρά είναι βάση της εσωτερικής διάταξης των basis blades στο layout.
    """
    return np.array([float(mv[i]) for i in range(2**5)], dtype=np.float32)

def build_motor_from_vertex_normal(vertex, normal):
    """
    Δέχεται:
      - vertex: (x, y, z)
      - normal: (nx, ny, nz)
    και επιστρέφει:
      - CGA (ή PGA) motor multivector μέσω matrix_to_motor()
    """
    # Normalize the normal vector
    normal = np.asarray(normal, dtype=np.float64)
    vertex = np.asarray(vertex, dtype=np.float64)
    if(normal[1] < 0):
        normal[1] = (-1) * normal[1]
    # Handle degenerate normal
    norm = np.linalg.norm(normal)
    if norm < 1e-6:  # threshold to consider it "zero"
        normal = np.array([0.0, 1.0, 0.0], dtype=np.float64)  # default normal pointing up
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

    # Use friend's function (must be in your scope)
    motor = matrix_to_motor(M, method = 'CGA')
    return multivector_to_vector32(motor)

vertex = [1, 2, 3]
normal = [1, 0.25, 0.75]
print(build_motor_from_vertex_normal(vertex, normal))
