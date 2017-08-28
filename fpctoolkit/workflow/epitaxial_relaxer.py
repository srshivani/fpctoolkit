#from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer

import numpy as np
import copy
from collections import OrderedDict

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.workflow.vasp_polarization_run_set import VaspPolarizationRunSet

class EpitaxialRelaxer(object):
	"""
	Calculates the minimum energy structures across a series of (100) misfit strains.
	"""

	def __init__(self, path, initial_structures_directory_path, inputs_dictionaries, polarization_reference_structure, calculate_polarizations=False):
		"""
		path should be the main path of the calculation set

		initial_structures should be in path/initial_structures, each named according to its structure tag

		reference structure can have any lattice but its atom positions must be in direct coords as the positions to compare polarizations to (choose a centrosymmetric structure if possible)

		inputs_dictionaries should look something like:
		value for tag: ['structure_afm'] = 
		{
			'external_relaxation_count': 4,
			'kpoint_schemes_list': ['Gamma'],
			'kpoint_subdivisions_lists': [[1, 1, 1], [1, 1, 2], [2, 2, 4]],
			'submission_script_modification_keys_list': ['100', 'standard', 'standard_gamma'], #optional - will default to whatever queue adapter gives
			'submission_node_count_list': [1, 2],
			'ediff': [0.001, 0.00001, 0.0000001],
			'encut': [200, 400, 600, 800],
			'isif' : [5, 2, 3],
			'supercell_dimensions_list': [2, 2, 1],
			'misfit_strains_list': [-0.04, -0.03, ...],
			'reference_lattice_constant': 3.91,
			'number_of_trials': 3,
			'max_displacement_magnitude': 0.1 #in angstroms
			#any other incar parameters with value as a list
		}
		value for tag: ['structure_fm'] = ...

		reference_lattice_constant should be the lattice constant a0 which, when multiplied by the list of misfit strains, generates the new in-plane lattice constant at those strains.

		For each lattice constant and each structure, a relaxation is performed. Then, the lowest energy structures at each misfit strain can be determined, and a convex hull results.
		"""

		self.path = path
		self.input_dictionaries = input_dictionaries

		self.polarization_reference_structure = polarization_reference_structure
		self.calculate_polarizations = calculate_polarizations

		Path.make(path)

		self.initialize_vasp_relaxations()


	def initialize_vasp_relaxations(self):
		"""
		"""

		for structure_tag, input_dictionary in self.input_dictionaries.items():
			misfit_strains_list = input_dictionary.pop('misfit_strains_list')
			reference_lattice_constant = input_dictionary.pop('reference_lattice_constant')
			number_of_trials = input_dictionary.pop('number_of_trials')
			supercell_dimensions_list = input_dictionary.pop('supercell_dimensions_list')
			max_displacement_magnitude = input_dictionary.pop('max_displacement_magnitude')

			for misfit_strain in misfit_strains_list:
				misfit_path = Path.join(self.path, str(misfit_strain).replace('-', 'n'))
				Path.make(misfit_path)

				relaxations_set_path = Path.join(misfit_path, structure_tag)
				Path.make(relaxations_set_path)

				lattice_constant = reference_lattice_constant*(1.0+misfit_strain)

				for i in range(number_of_trials):
					relaxation_path = Path.join(relaxations_set_path, 'trial_' + str(i))

					initial_structure_path = Path.join(self.path, 'initial_structures', structure_tag)
					initial_structure = Structure(initial_structure_path)

					if abs(initial_structure.lattice[0][1]) > 0.0 or abs(initial_structure.lattice[0][2]) > 0.0 or abs(initial_structure.lattice[1][0]) > 0.0 or abs(initial_structure.lattice[1][2]) > 0.0:
						raise Exception("Current lattice is incompatible with (100) epitaxy: ", str(initial_structure.lattice))

					initial_structure.lattice[0][0] = lattice_constant*supercell_dimensions_list[0]
					initial_structure.lattice[1][1] = lattice_constant*supercell_dimensions_list[1]

					initial_structure.randomly_displace_sites(max_displacement_magnitude=max_displacement_magnitude)

					


			for i, initial_structure in enumerate(self.initial_structures_list):

				#if self.structure_is_duplicate(initial_structure, misfit_path): #####################FIX THIS AND PUT BACK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				#	print "Duplicate structure found - skipping"
				#	continue

				structure = copy.deepcopy(initial_structure)

				if abs(structure.lattice[0][1]) > 0.0 or abs(structure.lattice[0][2]) > 0.0 or abs(structure.lattice[1][0]) > 0.0 or abs(structure.lattice[1][2]) > 0.0:
					raise Exception("Current lattice is incompatible with (100) epitaxy: ", str(structure.lattice))

				structure.lattice[0][0] = lattice_constant*self.supercell_dimensions_list[0]
				structure.lattice[1][1] = lattice_constant*self.supercell_dimensions_list[1]

				#break symmetry
				structure.randomly_displace_sites(max_displacement_magnitude=0.01)


				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					print "Initializing epitaxial relaxation at " + relax_path

				relaxation = VaspRelaxation(path=relax_path, initial_structure=structure, input_dictionary=self.vasp_relaxation_inputs_dictionary)

				initial_structure.to_poscar_file_path(Path.join(relax_path, 'original_initial_structure'))


	def structure_is_duplicate(self, structure, misfit_path):
		"""
		Returns true if this has been the initial structure for any previous relaxation
		"""

		for i in range(10000):
			relax_path = Path.join(misfit_path, 'structure_' + str(i))

			if not Path.exists(relax_path):
				return False
			else:
				comparison_structure = Structure(file_path=Path.join(relax_path, 'original_initial_structure'))

				if structure.is_equivalent_to_structure(comparison_structure):
					print "FOUND DUPLICATE in epitaxial_relaxer.py"
					return True


	def update(self):

		for misfit_strain in self.misfit_strains_list:

			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			for i in range(10000):
				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					break

				
				relaxation = VaspRelaxation(path=relax_path)

				relaxation.update()

				print "Updating Epitaxial Relax run at " + relax_path + "  Status is " + relaxation.get_status_string()

				if self.calculate_polarizations and relaxation.complete:
					self.update_polarization_run(relaxation)

	@property
	def complete(self):
		for misfit_strain in self.misfit_strains_list:
			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			for i in range(10000):
				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					return True
				else:
					relaxation = VaspRelaxation(path=relax_path)

					if not relaxation.complete:
						return False

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def update_polarization_run(self, relaxation):

		if not relaxation.complete:
			return

		path = relaxation.path
		polarization_reference_structure = self.polarization_reference_structure
		distorted_structure = relaxation.final_structure
		polarization_reference_structure.lattice = copy.deepcopy(distorted_structure.lattice)
		vasp_run_inputs_dictionary = {
			'kpoint_scheme': relaxation.kpoint_schemes[100],
			'kpoint_subdivisions_list': relaxation.kpoint_subdivisions_lists[100],
			'encut': relaxation.incar_modifier_lists_dictionary['encut'][100],
			'lreal': False,
			'ediff': 1e-8,
			'isym': 0
		}


		polarization_run = VaspPolarizationRunSet(path, polarization_reference_structure, distorted_structure, vasp_run_inputs_dictionary)

		polarization_run.update()

		return polarization_run.get_change_in_polarization()

	def get_data_dictionaries_list(self, get_polarization=False):
		"""
		Starts at most negative misfit runs and goes to larger misfits finding the minimum energy data set. To encourage continuity, if two or more relaxations are within a small energy threshold of each other, the 
		structure that is closest to the last chosen structure is chosen.

		The output of this function looks like [[-0.02, energy_1, [polarization_vector_1]], [-0.015, energy_2, [polarization_vector_2]], ...]
		"""

		output_data_dictionaries = []
		spg_symprecs = [0.1, 0.05, 0.04, 0.03, 0.02, 0.01, 0.001]

		for misfit_strain in self.misfit_strains_list:
			# print str(misfit_strain)
			data_dictionary = OrderedDict()
			data_dictionary['misfit_strain'] = misfit_strain

			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			minimum_energy = 10000000000
			minimum_energy_relaxation = None
			for i in range(10000):
				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					break

				relaxation = VaspRelaxation(path=relax_path)

				if not relaxation.complete:
					continue

				energy = relaxation.get_final_energy(per_atom=False)
				# print 'structure_' + str(i), energy
				
				if energy < minimum_energy:
					minimum_energy = energy
					minimum_energy_relaxation = relaxation

			# print 
			# print "minimum E " + str(minimum_energy)
			# print 
			
			if minimum_energy_relaxation == None:
				data_dictionary['structure'] = None
				data_dictionary['energy'] = None
				data_dictionary['polarization_vector'] = None

				for symprec in spg_symprecs:
					data_dictionary['spg_' + str(symprec)] = None

				data_dictionary['path'] = None
			else:				

				structure = copy.deepcopy(minimum_energy_relaxation.final_structure)

				if get_polarization:
					polarization_vector = self.update_polarization_run(minimum_energy_relaxation)
				else:
					polarization_vector = None

				data_dictionary['structure'] = structure
				data_dictionary['energy'] = minimum_energy
				data_dictionary['polarization_vector'] = polarization_vector

				for symprec in spg_symprecs:
					data_dictionary['spg_' + str(symprec)] = structure.get_spacegroup_string(symprec)

				data_dictionary['path'] = Path.join(minimum_energy_relaxation.path, 'static')

			output_data_dictionaries.append(data_dictionary)

		return output_data_dictionaries