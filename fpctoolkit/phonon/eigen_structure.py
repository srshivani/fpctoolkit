#from fpctoolkit.phonon.eigen_structure import EigenStructure

import numpy as np
import copy

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.phonon.eigen_component import EigenComponent

class EigenStructure(object):
	"""
	Represents a structure whose displacements are relative to a reference structure in terms of six strains (Voigt) and N displacement modes, where N is the number
	of atoms in the reference structure. The displacement modes are the eigen vectors of the hessian matrix for the reference structure.

	The representation is covered by two lists. One list is the engineering strains [eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy]. The other is the set of
	amplitudes representing degree of displacement along each normal mode. This set is stored as a list of EigenComponent instances, which store amplitudes and EigenPair
	instances.

	We can think of a eigenchromosome storing all of an eigenstructure's data looking like:

	[eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N], where A_1 is the amplitude of the displacement eigen-vector with the lowest eigenvector and A_N
	is the amplitude of the displacement eigen-vector with the highest eigenvalue.

	If e_1, e_2, ..., e_N is the set of eigen-vectors, the total displacement is given by:

	U = A_1*e_1 + A_2*e_2 + ... + A_N*e_N



	When distorting a structure, displacements are always applied first (so they're in Lagrangian coordinates) and then strains are applied.
	When recovering the strains and eigen_component amplitudes from a structure, strains are removed first, then displacement amplitudes are determined.

	Note: if exx = 0.0, these means no strain in xx direction.
	"""

	def __init__(self, reference_structure, hessian, distorted_structure=None):
		"""
		If distorted_structure is inputted, then this will be used to seed the strain vector and eigen_component amplitudes.
		"""

		Structure.validate(reference_structure)

		eigen_pairs = hessian.get_sorted_hessian_eigen_pairs_list()


		self.voigt_strains_list = [0.0]*6

		self.eigen_components_list = []

		for eigen_pair in eigen_pairs:
			eigen_component = EigenComponent(eigen_pair, amplitude=0.0)

			self.eigen_components_list.append(eigen_component)

		if len(self.eigen_components_list) != 3*reference_structure.site_count:
			raise Exception("Number of eigen components", len(self.eigen_components_list), "and number of degrees of freedom in reference structure", 3*reference_structure.site_count, "are not equal.")


		self.reference_structure = reference_structure


		if distorted_structure:
			self.set_strains_and_amplitudes_from_distorted_structure(distorted_structure)



	def set_translational_eigen_component_amplitudes_to_zero(self):
		for eigen_component in self.eigen_components_list:
			if eigen_component.is_translational_mode():
				eigen_component.amplitude = 0.0




	def get_distorted_structure(self):
		"""
		Apply the strains in voigt strains list and the displacements in the eigen_components list to the reference structure and return the new structure.
		"""

		total_displacement_vector = np.asarray([0.0]*3*self.reference_structure.site_count)

		for eigen_component in self.eigen_components_list:
			total_displacement_vector += eigen_component.get_displacement_vector()


		distorted_structure = DisplacementVector.displace_structure(reference_structure=self.reference_structure, displacement_vector=total_displacement_vector, displacement_coordinate_mode='Cartesian')

		distorted_structure.lattice.strain(self.get_strain_tensor())

		return distorted_structure


	def get_strain_tensor(self):
		"""
		Converts voigt strains stored in self.voigt_strains_list to a 3x3 tensor and returns this tensor.
		Upper triangle form is used.
		"""

		e = self.voigt_strains_list

		strain_tensor = [[1.0+e[0], e[5], e[4]], 
						 [0.0, 1.0+e[1], e[3]], 
						 [0.0, 0.0, 1.0+e[2]]]

		return strain_tensor




	def set_strains_and_amplitudes_from_distorted_structure(self, distorted_structure):
		"""
		Modifies the passed in voigt strains and eigen_components list such that the strains and amplitudes would reproduce the input distorted_structure if 
		get_distorted_structure were called.
		"""

		total_displacement_vector_instance = DisplacementVector.get_instance_from_distorted_structure_relative_to_reference_structure(reference_structure=self.reference_structure, 
			distorted_structure=distorted_structure, coordinate_mode='Cartesian')

		total_displacement_vector = total_displacement_vector_instance.to_numpy_array()

		for eigen_component in self.eigen_components_list:
			basis_vector = eigen_component.eigenvector

			projection = np.dot(basis_vector, total_displacement_vector)

			if abs(projection) < 1e-10:
				projection = 0.0

			eigen_component.amplitude = projection


		strain_tensor = distorted_structure.lattice.get_strain_tensor_relative_to_reference(reference_lattice=self.reference_structure.lattice)

		print strain_tensor


	def get_list_representation(self):
		"""
		Returns list of strains and distortion amplitudes like:
		[eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N]
		"""

		return self.voigt_strains_list + [eigen_component.amplitude for eigen_component in self.eigen_components_list]





	def print_eigen_components(self):
		for i, eigen_component in enumerate(self.eigen_components_list):
			print "Index: " + str(i) + "   " + str(eigen_component)


	def __str__(self):
		voigt_strings = ['exx', 'eyy', 'ezz', 'eyz', 'exz', 'exy']
		return_string = "["

		return_string += ", ".join(voigt_strings[i] + '=' + str(strain) for i, strain in enumerate(self.voigt_strains_list)) 

		for i, eigen_component in enumerate(self.eigen_components_list):
			return_string += ", " + 'A' + str(i) + '=' + str(eigen_component.amplitude)

			if eigen_component.is_translational_mode():
				return_string += '*'

		return_string += "]"

		return return_string

	def __len__(self):
		return len(self.get_list_representation())

	def __getitem__(self, index):
		list_representation = self.get_list_representation()

		basic_validators.validate_sequence_index(index, len(list_representation))

		return list_representation[index]

	def __setitem__(self, index, value):
		list_representation = self.get_list_representation()

		basic_validators.validate_real_number(value)

		basic_validators.validate_sequence_index(index, len(list_representation))

		if index <= 5:
			self.voigt_strains_list[index] = value
		else:
			self.eigen_components_list[index-6].amplitude = value