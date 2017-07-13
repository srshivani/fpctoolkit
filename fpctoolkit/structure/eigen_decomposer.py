#import fpctoolkit.structure.eigen_decomposer as eig_dec

from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.perovskite import Perovskite

import sys
import numpy as np
import copy


fex = np.array([
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000
	 ])

fey = np.array([
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000
	])

fez = np.array([
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.12796,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  0.24619,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.13855,
	0.00000,  0.00000,  -0.09810,
	0.00000,  0.00000,  -0.13855
	])

aminus = np.array([
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000
	  ])

bminus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000
	 ])

cminus = np.array([
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000
	])

aplus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000
	 ])

bplus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000, -0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000, -0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000, -0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000, -0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000
	 ])

cplus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000
	 ])

fex *= 1.0/(np.linalg.norm(fex))
fey *= 1.0/(np.linalg.norm(fey))
fez *= 1.0/(np.linalg.norm(fez))

cplus *= -1.0


translational_vector_x = []
translational_vector_y = []
translational_vector_z = []


for i in range(120):
	if i%3 == 0:
		translational_vector_x.append(1.0)
		translational_vector_y.append(0.0)
		translational_vector_z.append(0.0)
	if i%3 == 0:
		translational_vector_x.append(0.0)
		translational_vector_y.append(1.0)
		translational_vector_z.append(0.0)
	if i%3 == 0:
		translational_vector_x.append(0.0)
		translational_vector_y.append(0.0)
		translational_vector_z.append(1.0)

translational_vector_x = np.array(translational_vector_x)
translational_vector_y = np.array(translational_vector_y)
translational_vector_z = np.array(translational_vector_z)

translational_vector_x /= np.linalg.norm(translational_vector_x)
translational_vector_y /= np.linalg.norm(translational_vector_y)
translational_vector_z /= np.linalg.norm(translational_vector_z)


eigen_basis_vectors_list = [aminus, bminus, cminus, aplus, bplus, cplus, fex, fey, fez]#, translational_vector_x, translational_vector_y, translational_vector_z]




print np.dot(fex, bplus)

print
print "magnitudes"

for eig in eigen_basis_vectors_list:
	print "magnitude: ", np.linalg.norm(eig)

	for other_eig in eigen_basis_vectors_list:

		print "dot:", np.dot(eig, other_eig)



if __name__ == '__main__':
	pass
	# reference_structure_path = '../data/reference_structure.vasp'


	# reference_structure = Structure(reference_structure_path)


	# displacement_vector = cplus

	# displacement_vector *= 0.7

	# distorted_structure = DisplacementVector.displace_structure(reference_structure=reference_structure, displacement_vector=displacement_vector, displacement_coordinate_mode='Cartesian')

	# distorted_structure.to_poscar_file_path('../data/cplus.vasp')


	# relaxed_structure = Structure('../data/relaxed_structure.vasp')


	# relaxed_structure.lattice = copy.deepcopy(reference_structure.lattice)

	# total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
	# 		displaced_structure=relaxed_structure, coordinate_mode='Cartesian')

	# total_displacement_vector = total_displacement_vector_instance.to_numpy_array()

	# print "a-      b-       c-       a+      b+       c+     FEx      FEy      FEz"

	# for basis_vector in eigen_basis_vectors_list:
	# 	projection = np.dot(basis_vector, total_displacement_vector)

	# 	print str(round(projection,4)) + '   ',

	#eigen_amplitude_analysis_hessian = Hessian(outcar=Outcar("./dfpt_outcar"))
	#eigen_amplitude_analysis_reference_structure = Structure("./reference_structure")
	#eigen_structure = EigenStructure(reference_structure=eigen_amplitude_analysis_reference_structure, hessian=eigen_amplitude_analysis_hessian)

	#eigen_structure.set_strains_and_amplitudes_from_distorted_structure(relaxed_structure)
	#relaxed_eigen_chromosome =  eigen_structure.get_list_representation()


	#print " ".join(str(round(x, 3)) for x in relaxed_eigen_chromosome[:20])


def print_labels():
	print "a-      b-       c-       a+      b+       c+     FEx      FEy      FEz"


def get_nine_common_amplitudes(distorted_structure):


	reference_structure = Perovskite(supercell_dimensions=[2, 2, 2], lattice = distorted_structure.lattice, species_list=distorted_structure.get_species_list())

	total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
			displaced_structure=distorted_structure, coordinate_mode='Cartesian')

	total_displacement_vector = total_displacement_vector_instance.to_numpy_array()


	for basis_vector in eigen_basis_vectors_list:
		projection = np.dot(basis_vector, total_displacement_vector)

		print str(round(projection,4)) + '   ',



