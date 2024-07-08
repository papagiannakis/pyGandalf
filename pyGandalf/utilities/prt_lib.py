import random
import math
import imageio
import numpy as np
from OpenGL.GL import *

from pyGandalf.utilities.definitions import TEXTURES_PATH


class OBJLoader:
    """
    Class responsible for loading an .obj file for processing by the PRT algorithm.
    """
    def __init__(self):
        """
        Initializes the OBJLoader with empty lists for vertices, faces, and normals.
        """
        self.vertices = []
        self.faces = []
        self.normals = []

    def get_vertices(self):
        """
        Returns the vertices of the loaded .obj file.

        Returns:
            np.ndarray: A numpy array of the vertices with dtype 'float32'.
        """
        return np.array(self.vertices, dtype='float32')

    def get_faces(self):
        """
        Returns the faces of the loaded .obj file.

        Returns:
            np.ndarray: A numpy array of the faces with dtype 'int32'.
        """
        return np.array(self.faces, dtype='int32')

    def get_normals(self):
        """
        Returns the normals of the loaded .obj file.

        Returns:
            np.ndarray: A numpy array of the normals with dtype 'float32'.
        """
        return np.array(self.normals, dtype='float32')

    def load_model(self, filename, auto_calculate_normals=False):
        """
        Main function for loading the model from a .obj file.

        Args:
            filename (str): The path to the .obj file to be loaded.
            auto_calculate_normals (bool): If True, normals will be automatically calculated if they are not present in the file.
        """
        with open(filename) as file:
            for line in file:
                if line.startswith('v '):
                    # Vertex data
                    parts = line.split()
                    vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                    self.vertices.append(vertex)
                elif line.startswith('f '):
                    # Face data
                    parts = line.split()
                    face = [int(part.split('/')[0]) - 1 for part in parts[1:]]
                    self.faces.append(face)
                elif line.startswith('vn ') and not auto_calculate_normals:
                    # Normal data
                    parts = line.split()
                    normal = [float(parts[1]), float(parts[2]), float(parts[3])]
                    self.normals.append(normal)
            
            if auto_calculate_normals:
                self.calculate_normals()

    def calculate_normals(self):
        """
        Calculates normals for the loaded model if they are not provided in the .obj file.
        This function computes vertex normals as the average of the normals of the faces that meet at each vertex.
        """
        # Initialize normals
        self.normals = np.zeros((len(self.vertices), 3), dtype='float32')

        # Calculate face normals
        face_normals = []
        for face in self.faces:
            v0 = np.array(self.vertices[face[0]])
            v1 = np.array(self.vertices[face[1]])
            v2 = np.array(self.vertices[face[2]])
            normal = np.cross(v1 - v0, v2 - v0)
            if np.linalg.norm(normal) != 0:
                normal = normal / np.linalg.norm(normal)  # Normalize the vector
            face_normals.append(normal)

            # Accumulate face normals to the vertices
            self.normals[face[0]] += normal
            self.normals[face[1]] += normal
            self.normals[face[2]] += normal

        # Normalize the accumulated vertex normals
        self.normals = np.array([n / np.linalg.norm(n) for n in self.normals], dtype='float32')


class HDRI_frame:
    """
    Class responsible for loading an HDR/Cross-HDR image.
    """
    def __init__(self):
        """
        Initializes the HDRI_frame with default dimensions and an empty cubemap.
        """
        self.dimx = 0
        self.dimy = 0
        self.cubemap = [None] * 6

    def read_hdr(self, filename):
        """
        Reads an HDR image file and loads it into the class.

        Args:
            filename (str): The path to the HDR image file to be loaded.

        Returns:
            hdrResult: An object containing the loaded HDR image data.
        """
        self.hdrResult = HDRLoader.load(filename)
        self.dimx = self.hdrResult.width
        self.dimy = self.hdrResult.height

        return self.hdrResult

    def create_cube_map_faces(self, hdrResult):
        """
        Creates cubemap faces from the loaded HDR image.

        Args:
            hdrResult: The HDR image data from which to create the cubemap faces.
        """
        h = self.dimx // 4
        w = self.dimy // 3

        for i in range(6):
            self.cubemap[i] = np.zeros((h, w, 3), dtype=np.uint8)

        self.cubemap[2][:,:,:] = hdrResult.cols[0:h, w:2*w,  :]
        self.cubemap[3][:,:,:] = hdrResult.cols[2*h:3*h, w:2*w,  :]
        self.cubemap[0][:,:,:] = hdrResult.cols[h:2*h, 2*w:3*w,  :]
        self.cubemap[1][:,:,:] = hdrResult.cols[h:2*h, 0:w,  :]
        self.cubemap[4][:,:,:] = hdrResult.cols[h:2*h, w:2*w,  :]
        self.cubemap[5][:,:,:] = hdrResult.cols[3*h:4*h, w:2*w,  :][::-1, :, :]

class HDRLoader:
    """
    Class responsible for loading an HDR/Cross-HDR image.
    """
    @staticmethod
    def load(file_name):
        """
        Loads an HDR image from the specified file.

        Args:
            file_name (str): The path to the HDR image file to be loaded.

        Returns:
            HDRLoaderResult: An object containing the loaded HDR image data.

        Raises:
            SystemExit: If the image cannot be loaded or is not in the cross HDRI format.
        """
        result = imageio.imread(file_name)
        
        if result is None:
            print("Cross HDRI image not found.")
            exit(0)
        
        x, y, n = result.shape
        
        if x == y:
            print("Image must be cross HDRI format.")
            exit(0)
        
        width = x
        height = y
        
        res = HDRLoaderResult(width, height, result)
        
        print("\nLoading cross HDRI successful.\n")

        return res

class HDRLoaderResult:
    """
    Class to hold the results of loading an HDR image.
    """
    def __init__(self, width, height, cols):
        """
        Initializes the HDRLoaderResult with the given dimensions and image data.

        Args:
            width (int): The width of the loaded HDR image.
            height (int): The height of the loaded HDR image.
            cols (ndarray): The image data of the loaded HDR image.
        """
        self.width = width
        self.height = height
        self.cols = cols

class Sample:
    """
    Class responsible for keeping the information of a PRT sample.
    """
    def __init__(self):
        """
        Initializes the Sample with default spherical and cartesian coordinates,
        and sets the spherical harmonics functions to None.
        """
        self.spherical_coord = (0, 0)  # (theta, phi)
        self.cartesian_coord = (0, 0, 0)  # (x, y, z)
        self.sh_functions = None  # Spherical harmonics functions

class Sampler:
    """
    Class responsible for keeping the information of the PRT sampler.
    """
    def __init__(self, N):
        """
        Initializes the Sampler with an empty list of samples and sets the number of samples to zero.
        """
        self.samples = []
        self.number_of_samples = 0
        self.generate_samples(N)

    def generate_samples(self, N):
        """
        Generates N x N samples and stores them in the samples list. Each sample's spherical and
        cartesian coordinates are calculated based on stratified sampling.

        Args:
            N (int): The square root of the number of samples to generate.
        """
        self.samples = [Sample() for _ in range(N * N)]
        self.number_of_samples = N * N

        for i in range(N):
            for j in range(N):
                a = (i + random.random() / 32767) / N
                b = (j + random.random() / 32767) / N
                theta = 2 * math.acos(math.sqrt(1 - a))
                phi = 2 * math.pi * b
                x = math.sin(theta) * math.cos(phi)
                y = math.sin(theta) * math.sin(phi)
                z = math.cos(theta)
                
                k = i * N + j

                self.samples[k].spherical_coord = (theta, phi)
                self.samples[k].cartesian_coord = (x, y, z)
                self.samples[k].sh_functions = None  # Placeholder for spherical harmonics functions

class SphericalHarmonics:
    """
    Class responsible for the computation of Spherical Harmonics for the PRT algorithm.
    """
    def __init__(self, bands):
        """
        Initializes the SphericalHarmonics object with the given number of bands.
        
        Args:
            bands (int): The number of spherical harmonics bands to use.
        """
        self.bands = bands
        self.coeffs = None
        self.image = None
        self.lightCoeffs = None
        
    @staticmethod
    def legendre(l, m, x):
        """
        Computes the associated Legendre polynomial P_l^m(x).

        Args:
            l (int): Degree of the polynomial.
            m (int): Order of the polynomial.
            x (float): Input value.

        Returns:
            float: The value of the associated Legendre polynomial.
        """
        if l == m + 1:
            return x * (2 * m + 1) * SphericalHarmonics.legendre(m, m, x)
        elif l == m:
            return math.pow(-1, m) * SphericalHarmonics.double_factorial(2 * m - 1) * math.pow((1 - x * x), m / 2)
        else:
            return (x * (2 * l - 1) * SphericalHarmonics.legendre(l - 1, m, x) - (l + m - 1) * SphericalHarmonics.legendre(l - 2, m, x)) / (l - m)

    @staticmethod
    def double_factorial(n):
        """
        Computes the double factorial of n (n!!).

        Args:
            n (int): The input value.

        Returns:
            int: The double factorial of n.
        """
        if n <= 1:
            return 1
        else:
            return n * SphericalHarmonics.double_factorial(n - 2)

    @staticmethod
    def spherical_harmonic(l, m, theta, phi):
        """
        Computes the spherical harmonic Y_l^m(theta, phi).

        Args:
            l (int): Degree of the harmonic.
            m (int): Order of the harmonic.
            theta (float): Polar angle.
            phi (float): Azimuthal angle.

        Returns:
            float: The value of the spherical harmonic.
        """
        if m > 0:
            result = math.sqrt(2) * SphericalHarmonics.k(l, m) * math.cos(m * phi) * SphericalHarmonics.legendre(l, m, math.cos(theta))
        elif m < 0:
            result = math.sqrt(2) * SphericalHarmonics.k(l, m) * math.sin(-m * phi) * SphericalHarmonics.legendre(l, -m, math.cos(theta))
        else:
            result = SphericalHarmonics.k(l, m) * SphericalHarmonics.legendre(l, 0, math.cos(theta))
        
        return result if abs(result) > 0 else 0.0

    @staticmethod
    def k(l, m):
        """
        Computes the normalization constant for the spherical harmonic.

        Args:
            l (int): Degree of the harmonic.
            m (int): Order of the harmonic.

        Returns:
            float: The normalization constant.
        """
        if m == 0:
            return math.sqrt((2 * l + 1) / (4 * math.pi))

        num = (2 * l + 1) * SphericalHarmonics.factorial(l - abs(m))
        denom = 4 * math.pi * SphericalHarmonics.factorial(l + abs(m))
        return math.sqrt(num / denom)

    @staticmethod
    def factorial(n):
        """
        Computes the factorial of n (n!).

        Args:
            n (int): The input value.

        Returns:
            int: The factorial of n.
        """
        if n <= 1:
            return 1
        else:
            return n * SphericalHarmonics.factorial(n - 1)
        
    def precompute_sh_functions(self, sampler, bands):
        """
        Precomputes the spherical harmonic functions for the given samples and bands.

        Args:
            sampler (Sampler): The sampler containing the samples.
            bands (int): The number of bands.
        """
        for i in range(len(sampler.samples)):
            sampler.samples[i].sh_functions = np.zeros(bands * bands, dtype=np.float32)
            theta, phi = sampler.samples[i].spherical_coord
            for l in range(bands):
                for m in range(-l, l + 1):
                    j = l * (l + 1) + m
                    sampler.samples[i].sh_functions[j] = SphericalHarmonics.spherical_harmonic(l, m, theta, phi)

    def light_probe_access(self, imageName, direction):
        """
        Accesses the light probe and retrieves the color for a given direction.

        Args:
            imageName (str): The name of the image file.
            direction (tuple): The direction vector.

        Returns:
            np.ndarray: The color value retrieved from the light probe.
        """
        if self.image is None:
            self.image = imageio.imread(imageName)
        width, height, _ = self.image.shape

        d = math.sqrt(direction[0] * direction[0] + direction[1] * direction[1])
        r = (0.0 if d == 0 else (1.0 / math.pi / 2.0) * math.acos(direction[2]) / d)
        tex_coord = [0.5 + direction[0] * r, 0.5 + direction[1] * r]
        pixel_coord = [int(tex_coord[0] * width), int(tex_coord[1] * height)]
        return self.image[pixel_coord[0], pixel_coord[1], :3]
    
    def project_light_function(self, sampler, light, bands):
        """
        Projects the light function onto the spherical harmonics basis.

        Args:
            sampler (Sampler): The sampler containing the samples.
            light (str): The path to the light probe image.
            bands (int): The number of bands.
        """
        self.lightCoeffs = np.zeros((bands * bands, 3), dtype=np.float32)
        
        self.precompute_sh_functions(sampler, bands)

        for i in range(sampler.number_of_samples):
            direction = sampler.samples[i].cartesian_coord
            color = self.light_probe_access(light, direction)
            for j in range(bands * bands):
                sh_function = sampler.samples[i].sh_functions[j]
                self.lightCoeffs[j] += color * sh_function

        weight = 4.0 * math.pi
        scale = weight / sampler.number_of_samples
        self.lightCoeffs *= scale

    def ProjectUnshadowed(self, sampler, vertices, normals, bands):
        """
        Projects the unshadowed irradiance for the given vertices and normals.

        Args:
            sampler (Sampler): The sampler containing the samples.
            vertices (np.ndarray): The vertices of the mesh.
            normals (np.ndarray): The normals of the vertices.
            bands (int): The number of bands.

        Returns:
            np.ndarray: The resulting colors for each vertex.
        """
        self.coeffs = np.zeros((len(vertices), bands * bands, 3), dtype=np.float32)
        self.project_light_function(sampler, TEXTURES_PATH / 'skybox' / 'campus_probe.hdr', bands)
        progress = 0.00
        for i in range(len(vertices)):
            for j in range(sampler.number_of_samples):
                sample = sampler.samples[j]
                cosine_term = max(np.dot(normals[i], sample.cartesian_coord), 0.0)
                for k in range(bands * bands):
                    sh_function = sample.sh_functions[k]
                    progress = (i/len(vertices)) * 100
                    print(f"Computing coefficients....  {progress:.2f}%", end="\r")
                    self.coeffs[i][k] += 0.2 * sh_function * cosine_term

        print(f"Computing coefficients....  100.00%", end="\r")
        weight = 4.0 * math.pi
        scale = weight / sampler.number_of_samples
        self.coeffs *= scale

        colors = np.zeros((len(vertices), 3), dtype=np.float32)
        for i in range(len(vertices)):
            for j in range(9):
                colors[i] += self.lightCoeffs[j] * self.coeffs[i][j]

        return colors / 255

    def ProjectShadowed(self, sampler, vertices, normals, bands, indices):
        """
        Projects the shadowed irradiance for the given vertices and normals.

        Args:
            sampler (Sampler): The sampler containing the samples.
            vertices (np.ndarray): The vertices of the mesh.
            normals (np.ndarray): The normals of the vertices.
            bands (int): The number of bands.
            indices (np.ndarray): The indices of the mesh triangles.

        Returns:
            np.ndarray: The resulting colors for each vertex.
        """
        self.coeffs = np.zeros((len(vertices), bands * bands, 3), dtype=np.float32)
        self.project_light_function(sampler, TEXTURES_PATH / 'skybox' / 'campus_probe.hdr', bands)

        for i in range(len(vertices)):
            for j in range(sampler.number_of_samples):
                sample = sampler.samples[j]
                progress = (i/len(vertices)) * 100
                print(f"Computing coefficients....  {progress:.2f}%", end="\r")
                if self.Visibility(vertices, i, sample.cartesian_coord, indices):
                    cosine_term = max(np.dot(normals[i], sample.cartesian_coord), 0.0)
                    for k in range(bands * bands):
                        sh_function = sample.sh_functions[k]
                        self.coeffs[i][k] += 0.2 * sh_function * cosine_term

        print(f"Computing coefficients....  100.00%", end="\r")
        weight = 4.0 * math.pi
        scale = weight / sampler.number_of_samples
        self.coeffs *= scale

        colors = np.zeros((len(vertices), 3), dtype=np.float32)
        for i in range(len(vertices)):
            for j in range(9):
                colors[i] += self.lightCoeffs[j] * self.coeffs[i][j]

        return colors / 255
    
    @staticmethod
    def ray_intersects_triangle(p, d, v0, v1, v2):
        """
        Checks whether the ray intersects with the face created by vertices v0, v1, and v2.

        Args:
            p (np.ndarray): The origin of the ray.
            d (np.ndarray): The direction of the ray.
            v0 (np.ndarray): First vertex of the triangle.
            v1 (np.ndarray): Second vertex of the triangle.
            v2 (np.ndarray): Third vertex of the triangle.

        Returns:
            bool: True if the ray intersects the triangle, False otherwise.
        """
        e1 = v1 - v0
        e2 = v2 - v0
        h = np.cross(d, e2)
        a = np.dot(e1, h)
        if -0.00001 < a < 0.00001:
            return False
        f = 1.0 / a
        s = p - v0
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            return False
        q = np.cross(s, e1)
        v = f * np.dot(d, q)
        if v < 0.0 or u + v > 1.0:
            return False
        t = np.dot(e2, q) * f
        if t < 0.0:
            return False
        return True

    @staticmethod
    def Visibility(vertices, vertexidx, direction, indices):
        """
        Checks the visibility of a vertex in a given direction.

        Args:
            vertices (np.ndarray): The vertices of the mesh.
            vertexidx (int): The index of the vertex.
            direction (np.ndarray): The direction vector.
            indices (np.ndarray): The indices of the mesh triangles.

        Returns:
            bool: True if the vertex is visible in the given direction, False otherwise.
        """
        visible = True
        p = vertices[vertexidx]
        for i in range(0, len(indices), 3):
            if vertexidx not in indices[i:i+3]:
                v0 = vertices[indices[i]]
                v1 = vertices[indices[i+1]]
                v2 = vertices[indices[i+2]]
                if SphericalHarmonics.ray_intersects_triangle(p, direction, v0, v1, v2):
                    visible = False
                    break
        return visible

    @staticmethod
    def barycentric(pc, p):
        """
        Calculate the barycentric coordinates of a point pc with respect to a triangle defined by points p.

        Args:
            pc (np.ndarray): The point for which to find barycentric coordinates.
            p (list of np.ndarray): A list of three points defining the triangle.

        Returns:
            tuple: Barycentric coordinates (u, v, w).
        """
        v0 = p[1] - p[0]
        v1 = p[2] - p[0]
        v2 = pc - p[0]
        
        d00 = np.dot(v0, v0)
        d01 = np.dot(v0, v1)
        d11 = np.dot(v1, v1)
        d20 = np.dot(v2, v0)
        d21 = np.dot(v2, v1)
        denom = d00 * d11 - d01 * d01
        
        if abs(denom) < 1e-6:
            return 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0
        
        inv_denom = 1.0 / denom
        v = (d11 * d20 - d01 * d21) * inv_denom
        w = (d00 * d21 - d01 * d20) * inv_denom
        u = 1.0 - v - w
        return u, v, w
    
    def interreflections(self, bvh, band2, sampler, vertices, normals, indices, bounces):
        """
        Computes the interreflected irradiance for the given vertices and normals.

        Args:
            bvh (BVH): The bounding volume hierarchy for intersection tests.
            band2 (int): The number of bands squared.
            sampler (Sampler): The sampler containing the samples.
            vertices (np.ndarray): The vertices of the mesh.
            normals (np.ndarray): The normals of the vertices.
            indices (np.ndarray): The indices of the mesh triangles.
            bounces (int): The number of interreflection bounces.

        Returns:
            np.ndarray: The resulting colors for each vertex.
        """
        self.ProjectShadowed(sampler, vertices, normals, int(math.sqrt(band2)), indices)
        zeroVector = [np.zeros((band2, 3), dtype=np.float32) for _ in range(len(vertices))]

        sample_number = len(sampler.samples)
        interReflect = [self.coeffs] + [[] for _ in range(bounces)]
        weight = 4.0 * math.pi / sample_number

        for k in range(bounces):
            interReflect[k + 1] = [[] for _ in range(len(vertices))]

            for i in range(len(vertices)):
                normal = normals[i]
                for j in range(sample_number):
                    stemp = sampler.samples[j]
                    rtemp = Ray(vertices[i], stemp.cartesian_coord)

                    if not bvh.intersect(rtemp):
                        continue

                    H = np.maximum(np.dot(rtemp._dir, normal), 0.0)

                    triIndex = 3 * rtemp._index
                    voffset = np.zeros(3, dtype=np.int32)
                    p = np.zeros((3, 3), dtype=np.float32)
                    SHTrans = [None for _ in range(3)]

                    for m in range(3):
                        voffset[m] = int(indices[triIndex + m])
                        SHTrans[m] = interReflect[k][voffset[m]]
                        voffset[m] *= 3
                        p[m] = vertices[voffset[m]]

                    pc = rtemp._o + rtemp._t * rtemp._dir
                    u, v, w = SphericalHarmonics.barycentric(pc, p)

                    SHtemp = [np.zeros(3, dtype=np.float32) for _ in range(band2)]
                    for m in range(band2):
                        SHtemp[m] = u * SHTrans[0][m] + v * SHTrans[1][m] + w * SHTrans[2][m]
                        zeroVector[i][m] += H * np.array([0.2, 0.2, 0.2]) * SHtemp[m]

            for i in range(len(vertices)):
                interReflect[k + 1][i] = [np.zeros(3, dtype=np.float32) for _ in range(band2)]
                for j in range(band2):
                    zeroVector[i][j] *= weight
                    interReflect[k + 1][i][j] = interReflect[k][i][j] + zeroVector[i][j]

        self.coeffs = interReflect[bounces]
        print("Interreflected transfer vector generated.")

        colors = np.zeros((len(vertices), 3), dtype=np.float32)
        for i in range(len(vertices)):
            cr, cg, cb = 0, 0, 0
            for j in range(9):
                cr += self.lightCoeffs[j][0] * self.coeffs[i][j][0]
                cg += self.lightCoeffs[j][1] * self.coeffs[i][j][1]
                cb += self.lightCoeffs[j][2] * self.coeffs[i][j][2]

            colors[i] = (cr / 255, cg / 255, cb / 255)
        
        return colors

class Triangle:
    """
    Represents a triangle in 3D space using three vertices.
    """
    def __init__(self, v0, v1, v2):
        """
        Initializes a Triangle object with three vertices.

        Args:
            v0 (np.ndarray): The first vertex of the triangle.
            v1 (np.ndarray): The second vertex of the triangle.
            v2 (np.ndarray): The third vertex of the triangle.
        """
        self._v0 = np.array(v0)
        self._v1 = np.array(v1)
        self._v2 = np.array(v2)

class Ray:
    """
    Represents a ray in 3D space with an origin and a direction.
    """
    def __init__(self, origin, direction):
        """
        Initializes a Ray object with an origin and a direction.

        Args:
            origin (np.ndarray): The origin of the ray.
            direction (np.ndarray): The direction of the ray.
        """
        self._o = np.array(origin)
        self._dir = np.array(direction)
        self._inv = 1.0 / self._dir
        self._tmin = 0.0
        self._tmax = np.inf
        self._t = 0.0
        self._index = 0

class BBox:
    """
    Represents an axis-aligned bounding box (AABB) in 3D space.
    """
    def __init__(self, pMin=None, pMax=None, triangle=None, triangle_list=None):
        """
        Initializes a BBox object using either min/max points, a triangle, or a list of triangles.

        Args:
            pMin (np.ndarray, optional): The minimum corner of the bounding box.
            pMax (np.ndarray, optional): The maximum corner of the bounding box.
            triangle (Triangle, optional): A triangle to compute the bounding box from.
            triangle_list (list of Triangle, optional): A list of triangles to compute the bounding box from.
        """
        if pMin is not None and pMax is not None:
            self._v = [np.array(pMin), np.array(pMax)]
        elif triangle is not None:
            self._v = [np.zeros(3), np.zeros(3)]
            self._v[0][0] = min(triangle._v0[0], triangle._v1[0], triangle._v2[0])
            self._v[0][1] = min(triangle._v0[1], triangle._v1[1], triangle._v2[1])
            self._v[0][2] = min(triangle._v0[2], triangle._v1[2], triangle._v2[2])
            self._v[1][0] = max(triangle._v0[0], triangle._v1[0], triangle._v2[0])
            self._v[1][1] = max(triangle._v0[1], triangle._v1[1], triangle._v2[1])
            self._v[1][2] = max(triangle._v0[2], triangle._v1[2], triangle._v2[2])
        elif triangle_list is not None:
            assert len(triangle_list) > 0
            self._v = [triangle_list[0]._v0.copy(), triangle_list[0]._v0.copy()]
            for tri in triangle_list:
                btemp = BBox(triangle=tri)
                for j in range(3):
                    self._v[0][j] = min(self._v[0][j], btemp._v[0][j])
                    self._v[1][j] = max(self._v[1][j], btemp._v[1][j])
        else:
            self._v = [np.zeros(3), np.zeros(3)]
        
        self._center = self.set_center()

    def set_center(self):
        """
        Computes the center of the bounding box.

        Returns:
            np.ndarray: The center of the bounding box.
        """
        self._center = (self._v[0] + self._v[1]) / 2.0
        return self._center

    def ray_intersect(self, ray):
        """
        Checks whether a ray intersects the bounding box.

        Args:
            ray (Ray): The ray to check for intersection.

        Returns:
            bool: True if the ray intersects the bounding box, False otherwise.
        """
        tmin, tmax, tymin, tymax, tzmin, tzmax = 0, 0, 0, 0, 0, 0

        if ray._dir[0] >= 0:
            tmin = (self._v[0][0] - ray._o[0]) * ray._inv[0]
            tmax = (self._v[1][0] - ray._o[0]) * ray._inv[0]
        else:
            tmin = (self._v[1][0] - ray._o[0]) * ray._inv[0]
            tmax = (self._v[0][0] - ray._o[0]) * ray._inv[0]

        if ray._dir[1] >= 0:
            tymin = (self._v[0][1] - ray._o[1]) * ray._inv[1]
            tymax = (self._v[1][1] - ray._o[1]) * ray._inv[1]
        else:
            tymin = (self._v[1][1] - ray._o[1]) * ray._inv[1]
            tymax = (self._v[0][1] - ray._o[1]) * ray._inv[1]

        if np.any(tmin > tymax) or np.any(tymin > tmax):
            return False
        if tymin > tmin:
            tmin = tymin
        if tymax < tmax:
            tmax = tymax

        if ray._dir[2] >= 0:
            tzmin = (self._v[0][2] - ray._o[2]) * ray._inv[2]
            tzmax = (self._v[1][2] - ray._o[2]) * ray._inv[2]
        else:
            tzmin = (self._v[1][2] - ray._o[2]) * ray._inv[2]
            tzmax = (self._v[0][2] - ray._o[2]) * ray._inv[2]

        if (tmin > tzmax) or (tzmin > tmax):
            return False
        if tzmin > tmin:
            tmin = tzmin
        if tzmax < tmax:
            tmax = tzmax

        return (tmin < ray._tmax) and (tmax > ray._tmin)

    def area(self):
        """
        Computes the surface area of the bounding box.

        Returns:
            float: The surface area of the bounding box.
        """
        diff = self._v[1] - self._v[0]
        return 2.0 * (diff[0] * diff[1] + diff[0] * diff[2] + diff[1] * diff[2])

    def volume(self):
        """
        Computes the volume of the bounding box.

        Returns:
            float: The volume of the bounding box.
        """
        diff = self._v[1] - self._v[0]
        return diff[0] * diff[1] * diff[2]
    
    def extract_vertices(self):
        """
        Extracts the vertices and edges of the bounding box.

        Returns:
            list: A list of vertices that form the edges of the bounding box.
        """
        min_corner = self._v[0]
        max_corner = self._v[1]

        x_min, y_min, z_min = min_corner
        x_max, y_max, z_max = max_corner

        # Define the 8 vertices of the cube
        vertices = [
            [x_min, y_min, z_min],  # Vertex 0: bottom-front-left
            [x_max, y_min, z_min],  # Vertex 1: bottom-front-right
            [x_max, y_max, z_min],  # Vertex 2: top-front-right
            [x_min, y_max, z_min],  # Vertex 3: top-front-left
            [x_min, y_min, z_max],  # Vertex 4: bottom-back-left
            [x_max, y_min, z_max],  # Vertex 5: bottom-back-right
            [x_max, y_max, z_max],  # Vertex 6: top-back-right
            [x_min, y_max, z_max]   # Vertex 7: top-back-left
        ]


        # Define the 12 edges of the bounding box by specifying the order of vertices to be connected
        edges = [
            # Bottom face
            vertices[0], vertices[1],
            vertices[1], vertices[3],
            vertices[3], vertices[2],
            vertices[2], vertices[0],
            # Top face
            vertices[4], vertices[5],
            vertices[5], vertices[7],
            vertices[7], vertices[6],
            vertices[6], vertices[4],
            # Side edges
            vertices[0], vertices[4],
            vertices[1], vertices[5],
            vertices[2], vertices[6],
            vertices[3], vertices[7]
        ]
        
        return edges

class BVHNode:
    """
    Represents a node in a Bounding Volume Hierarchy (BVH) for efficient ray tracing.
    """
    def __init__(self, t1=None, t2=None):
        """
        Initializes a BVHNode object. It can either be a leaf node containing one or two triangles
        or an internal node with children nodes.

        Args:
            t1 (Triangle, optional): The first triangle.
            t2 (Triangle, optional): The second triangle.
        """
        self.set_null()
        if t1 is not None and t2 is None:
            self._bbox = BBox(triangle=t1)
            self._tri0 = t1
            self._leaf = True
        elif t1 is not None and t2 is not None:
            self._bbox = merge(BBox(triangle=t1), BBox(triangle=t2))
            self._tri0 = t1
            self._tri1 = t2
            self._leaf = True

    def hit(self, ray):
        """
        Checks whether the ray intersects any triangle within this BVH node or its children.

        Args:
            ray (Ray): The ray to check for intersections.

        Returns:
            bool: True if the ray intersects a triangle, False otherwise.
        """
        if not self._bbox.ray_intersect(ray):
            return False
        if self._leaf:
            if SphericalHarmonics.ray_intersects_triangle(ray._o, ray._dir, self._tri0._v0, self._tri0._v1, self._tri0._v2):
                return True
            if self._tri1 is None:
                return False
            return SphericalHarmonics.ray_intersects_triangle(ray._o, ray._dir, self._tri1._v0, self._tri1._v1, self._tri1._v2)
        return (self._left.hit(ray) or self._right.hit(ray))

    def set_null(self):
        """
        Resets the BVHNode to a non-leaf state with no children or triangles.
        """
        self._leaf = False
        self._left = self._right = None
        self._tri0 = self._tri1 = None

class BVHTree:
    """
    A Bounding Volume Hierarchy (BVH) tree for efficient ray tracing.
    The BVH tree is built from a set of triangles and can be used to quickly test
    for intersections between rays and triangles.
    """
    def __init__(self):
        """
        Initializes the BVHTree object.
        Sets up the list of triangles, the list of triangles in nodes, and the root of the tree.
        """
        self._triangles = []  # List to hold triangles in the BVH
        self._node_tri = []  # List to keep track of triangles associated with nodes
        self._root = None  # Root of the BVH tree

    def build(self, vertices, indices):
        """
        Builds the BVH tree from the given vertices and indices.

        Args:
            vertices (list of tuples): The list of vertex positions.
            indices (list of int): The list of triangle vertex indices.

        Prints:
            - "BVHTree: Start building" when the build process starts.
            - "BVHTree: Building done" when the build process is complete.
        """
        print("BVHTree: Start building")
        face_number = len(indices)
        self._triangles.clear()  # Clear the list of triangles

        # Construct triangles from vertex indices
        for i in range(0, face_number, 3):
            if (indices[i] >= len(vertices)) or (indices[i+1] >= len(vertices)) or (indices[i+2] >= len(vertices)):
                continue  # Skip invalid triangles

            v = (vertices[indices[i]], vertices[indices[i+1]], vertices[indices[i+2]])
            self._triangles.append(Triangle(v[0], v[1], v[2]))

        # Initialize the root of the BVH tree
        if len(self._triangles) == 1:
            self._root = BVHNode(self._triangles[0])
        elif len(self._triangles) == 2:
            self._root = BVHNode(self._triangles[0], self._triangles[1])
        else:
            self._root = BVHNode()

        # Create the bounding box for the entire set of triangles
        self._root._bbox = BBox(self._triangles)
        pivot = self._root._bbox._center  # Calculate the center of the bounding box

        # Split the triangles and recursively build the BVH
        mid_point = self.split(0, len(self._triangles), pivot[0], 0)
        self._root._left = self.recursive_build(0, mid_point, 1, face_number)
        self._root._right = self.recursive_build(mid_point, len(self._triangles) - mid_point, 1, face_number)
        print("BVHTree: Building done")

    def intersect(self, ray):
        """
        Tests for intersections between a ray and the triangles in the BVH tree.

        Args:
            ray (Ray): The ray to test for intersections.

        Returns:
            bool: True if the ray intersects a triangle in the BVH, False otherwise.
        """
        if self._root is None:
            return False
        return self._root.hit(ray)

    def split(self, start, size, pivot, axis):
        """
        Splits the triangles along the specified axis based on the pivot value.

        Args:
            start (int): The start index for the split.
            size (int): The number of triangles to consider.
            pivot (float): The value along the axis to split the triangles.
            axis (int): The axis to split along (0 = x, 1 = y, 2 = z).

        Returns:
            int: The index where the split occurs.
        """
        index = 0
        for i in range(start, start + size):
            btemp = BBox(triangle=self._triangles[i])
            centroid = btemp._center[axis]

            if centroid < pivot:
                # Swap triangles to ensure correct partitioning
                self._triangles[i], self._triangles[start + index] = self._triangles[start + index], self._triangles[i]
                index += 1

        # Ensure that we don't end up with empty partitions
        if index == 0 or index == size:
            index = size // 2
        return index

    def recursive_build(self, start, size, axis, face_number):
        """
        Recursively builds the BVH tree by creating nodes and partitioning triangles.

        Args:
            start (int): The start index for the current partition of triangles.
            size (int): The number of triangles in the current partition.
            axis (int): The axis to split along (0 = x, 1 = y, 2 = z).
            face_number (int): The total number of faces.

        Returns:
            BVHNode: The root of the subtree built from the current partition of triangles.
        """
        assert size >= 1  # Ensure there is at least one triangle

        if size == 1:
            return BVHNode(self._triangles[start])
        if size == 2:
            return BVHNode(self._triangles[start], self._triangles[start + 1])

        # Create a bounding box encompassing all triangles in the current partition
        btemp = BBox(self._triangles[start])
        for i in range(start + 1, start + size):
            btemp = merge(btemp, BBox(self._triangles[i]))

        pivot = btemp._center
        mid_point = self.split(start, size, pivot[axis], axis)  # Split the triangles

        result = BVHNode()
        result._bbox = btemp
        next_axis = (axis + 1) % 3  # Move to the next axis

        # Recursively build the left and right subtrees
        result._left = self.recursive_build(start, mid_point, next_axis, face_number)
        result._right = self.recursive_build(start + mid_point, size - mid_point, next_axis, face_number)

        return result

    def collect_bounding_boxes(self):
        """
        Collects all bounding boxes from the BVH tree.

        Returns:
            list of BBox: A list of bounding boxes from the BVH tree.
        """
        bounding_boxes = []
        if self._root is not None:
            self._collect_boxes_recursive(self._root, bounding_boxes)
        return bounding_boxes

    def _collect_boxes_recursive(self, node, bounding_boxes):
        """
        Recursively collects bounding boxes from the BVH tree.

        Args:
            node (BVHNode): The current node in the BVH tree.
            bounding_boxes (list of BBox): The list to append the collected bounding boxes to.
        """
        if node is None:
            return

        if node._leaf:
            # Add the bounding box of a leaf node
            bounding_boxes.append(node._bbox)
        else:
            # Recursively collect bounding boxes from child nodes
            self._collect_boxes_recursive(node._left, bounding_boxes)
            self._collect_boxes_recursive(node._right, bounding_boxes)

    @staticmethod
    def computeBVHTree(vertices, indices):
        """
        Constructs a BVHTree and collects the bounding boxes of the tree's nodes.

        Args:
            vertices (list of tuples): The list of vertex positions.
            indices (list of int): The list of triangle vertex indices.

        Returns:
            tuple: (BVHTree, np.ndarray) - The BVHTree object and an array of bounding box vertices.
        """
        bvh = BVHTree()
        bvh.build(vertices, indices)  # Build the BVH tree
        bboxes = bvh.collect_bounding_boxes()  # Collect the bounding boxes

        bvhVertices = []
        for bbox in bboxes:
            edges = bbox.extract_vertices()  # Extract edges from each bounding box
            bvhVertices.extend(edges)

        bvhVertices = np.array(bvhVertices, dtype=np.float32)  # Convert list of vertices to numpy array

        return bvh
    
def merge(b1, b2):
    """
    Merges two bounding boxes into one that encompasses both.

    Args:
        b1 (BBox): The first bounding box.
        b2 (BBox): The second bounding box.

    Returns:
        BBox: A new bounding box that covers both b1 and b2.
    
    Example:
        bbox1 = BBox(pMin=[0, 0, 0], pMax=[1, 1, 1])
        bbox2 = BBox(pMin=[1, 1, 1], pMax=[2, 2, 2])
        merged_bbox = merge(bbox1, bbox2)
    """
    # Compute the minimum and maximum corners for the new bounding box
    pMin = np.minimum(b1._v[0], b2._v[0])  # Minimum corner is the element-wise minimum of the two boxes
    pMax = np.maximum(b1._v[1], b2._v[1])  # Maximum corner is the element-wise maximum of the two boxes
    return BBox(pMin, pMax)  # Return the new bounding box that covers both

def normalize(vector):
    """
    Normalizes a vector to unit length.

    Args:
        vector (tuple or list of float): The vector to be normalized.

    Returns:
        tuple: The normalized vector.

    Example:
        vector = (1, 2, 3)
        normalized_vector = normalize(vector)  # Result: (0.267, 0.534, 0.802)
    """
    vector_np = np.array(vector)  # Convert the vector to a NumPy array
    norm = np.linalg.norm(vector_np)  # Compute the norm (magnitude) of the vector
    if norm == 0:
        return vector  # Return the original vector if its norm is zero (to avoid division by zero)
    normalized_vector = vector_np / norm  # Normalize the vector
    return tuple(normalized_vector)  # Convert the NumPy array back to a tuple and return it

def trimin(a, b, c):
    """
    Finds the minimum value among three given values.

    Args:
        a (float): First value.
        b (float): Second value.
        c (float): Third value.

    Returns:
        float: The smallest of the three values.

    Example:
        min_value = trimin(1, 2, 3)  # Result: 1
    """
    return min(a, b, c)  # Return the minimum value among a, b, and c

def trimax(a, b, c):
    """
    Finds the maximum value among three given values.

    Args:
        a (float): First value.
        b (float): Second value.
        c (float): Third value.

    Returns:
        float: The largest of the three values.

    Example:
        max_value = trimax(1, 2, 3)  # Result: 3
    """
    return max(a, b, c)  # Return the maximum value among a, b, and c