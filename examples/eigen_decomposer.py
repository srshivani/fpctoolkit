from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.structure_prediction.taylor_expansion.variable import Variable
from fpctoolkit.structure_prediction.taylor_expansion.expansion_term import ExpansionTerm
from fpctoolkit.structure_prediction.taylor_expansion.taylor_expansion import TaylorExpansion
from fpctoolkit.structure_prediction.taylor_expansion.derivative_evaluator import DerivativeEvaluator
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure_prediction.taylor_expansion.minima_relaxer import MinimaRelaxer
from fpctoolkit.io.file import File
from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.structure.lattice import Lattice

import sys
import numpy as np
import copy


fex = np.array([
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	0.11823, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.26651, 0.0, 0.0, 
	-0.22606, 0.0, 0.0, 
	-0.26651, 0.0, 0.0
	])

fey = np.array([
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, 0.11823, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.26651, 0.0, 
	0.0, -0.22606, 0.0, 
	0.0, -0.26651, 0.0
	])


fez = np.array([
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.0, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, 0.11823, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.26651, 
	0.0, 0.0, -0.22606, 
	0.0, 0.0, -0.26651
	])


# for i in range(len(fez)):
# 	if i%3 == 2:
# 		fez[i] -= 0.12796

# 		print str(fez[i-2]) + ', ' + str(fez[i-1]) + ', ' + str(fez[i]) + ', '

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


eigen_basis_vectors_list = [aminus, bminus, cminus, aplus, bplus, cplus, fex, fey, fez]




# print np.dot(fex, bplus)

# print
# print "magnitudes"

# for eig in eigs_list:
# 	print "magnitude: ", np.linalg.norm(eig)

# 	for other_eig in eigs_list:

# 		print "dot:", np.dot(eig, other_eig)



if __name__ == '__main__':

	reference_structure_path = '../data/reference_structure.vasp'


	reference_structure = Structure(reference_structure_path)


	# displacement_vector = cplus

	# displacement_vector *= 0.7

	# distorted_structure = DisplacementVector.displace_structure(reference_structure=reference_structure, displacement_vector=displacement_vector, displacement_coordinate_mode='Cartesian')

	# distorted_structure.to_poscar_file_path('../data/cplus.vasp')


	relaxed_structure = Structure('../data/relaxed_structure.vasp')


	relaxed_structure.lattice = copy.deepcopy(reference_structure.lattice)

	total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
			displaced_structure=relaxed_structure, coordinate_mode='Cartesian')

	total_displacement_vector = total_displacement_vector_instance.to_numpy_array()

	print "a-      b-       c-       a+      b+       c+     FEx      FEy      FEz"

	for basis_vector in eigen_basis_vectors_list:
		projection = np.dot(basis_vector, total_displacement_vector)

		print str(round(projection,4)) + '   ',

	#eigen_amplitude_analysis_hessian = Hessian(outcar=Outcar("./dfpt_outcar"))
	#eigen_amplitude_analysis_reference_structure = Structure("./reference_structure")
	#eigen_structure = EigenStructure(reference_structure=eigen_amplitude_analysis_reference_structure, hessian=eigen_amplitude_analysis_hessian)

	#eigen_structure.set_strains_and_amplitudes_from_distorted_structure(relaxed_structure)
	#relaxed_eigen_chromosome =  eigen_structure.get_list_representation()


	#print " ".join(str(round(x, 3)) for x in relaxed_eigen_chromosome[:20])


def print_labels():
	print "a-      b-       c-       a+      b+       c+     FEx      FEy      FEz"
	

def get_nine_common_amplitudes(reference_structure, distorted_structure):


	distorted_structure.lattice = copy.deepcopy(reference_structure.lattice)

	total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
			displaced_structure=distorted_structure, coordinate_mode='Cartesian')

	total_displacement_vector = total_displacement_vector_instance.to_numpy_array()


	for basis_vector in eigen_basis_vectors_list:
		projection = np.dot(basis_vector, total_displacement_vector)

		print str(round(projection,4)) + '   ',