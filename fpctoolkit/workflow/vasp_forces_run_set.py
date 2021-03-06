#from fpctoolkit.workflow.vasp_forces_run_set import VaspForcesRunSet

import numpy as np

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

class VaspForcesRunSet(VaspRunSet):
	"""
	Represents a set of static force calculations in vasp. Forces are calculated for each of the structures in the input structures_list argument.
	"""

	def __init__(self, path, structures_list, vasp_run_inputs_dictionary, wavecar_path=None):
		"""
		path should be the main path of the calculation set

		structures_list should be the set of structures for which forces are calculated.

		vasp_run_inputs_dictionary should look like:

		vasp_run_inputs_dictionary = {
			'kpoint_scheme': 'Monkhorst',
			'kpoint_subdivisions_list': [4, 4, 4],
			'encut': 800,
			'npar': 1 (optional)
		}

		wavecar_path should be the wavecar of a similar structure to the input structures of the structures_list.
		"""

		for structure in structures_list:
			Structure.validate(structure)

		self.path = path
		self.structures_list = structures_list
		self.vasp_run_inputs = vasp_run_inputs_dictionary
		self.wavecar_path = wavecar_path

		Path.make(path)

		self.initialize_vasp_runs()


	def initialize_vasp_runs(self):
		"""
		Creates any force calculation vasp runs (static force calculations at .../0, .../1, ...) that do not already exist.
		"""

		if Path.exists(self.get_extended_path('0')): #we don't want to write more runs if any already exist
			return

		for i, structure in enumerate(self.structures_list):
			run_path = self.get_extended_path(str(i))

			if not Path.exists(run_path):
				self.create_new_vasp_run(run_path, structure)


	def create_new_vasp_run(self, path, structure):
		"""
		Creates a static force calculation at path using structure as the initial structure and self.vasp_run_inputs as the run inputs.
		"""

		kpoints = Kpoints(scheme_string=self.vasp_run_inputs['kpoint_scheme'], subdivisions_list=self.vasp_run_inputs['kpoint_subdivisions_list'])
		incar = IncarMaker.get_accurate_forces_incar()
		incar['encut'] = self.vasp_run_inputs['encut']

		if 'npar' in self.vasp_run_inputs:
			incar['npar'] = self.vasp_run_inputs['npar']
			auto_change_npar = False
		else:
			auto_change_npar = True

		input_set = VaspInputSet(structure, kpoints, incar, auto_change_lreal=False, auto_change_npar=auto_change_npar)

		vasp_run = VaspRun(path=path, input_set=input_set, wavecar_path=self.wavecar_path)

	def update(self):
		"""
		Runs update on all force calculations until they are all complete. 
		"""

		if not self.complete:
			for vasp_run in self.vasp_run_list:
				vasp_run.update()


	@property
	def vasp_run_list(self):
		return [VaspRun(path=run_path) for run_path in self.get_run_paths_list()]

	@property
	def complete(self):
		for vasp_run in self.vasp_run_list:
			if not vasp_run.complete:
				return False

		return True

	def get_run_paths_list(self):
		"""
		Returns the a list of paths containing the vasp (static) force calculation run paths, i.e. [.../0, .../1, ...]
		"""

		run_paths_list = []

		i = 0
		while Path.exists(self.get_extended_path(str(i))):
			run_path = self.get_extended_path(str(i))

			run_paths_list.append(run_path)

			i += 1


		return run_paths_list

	def get_xml_file_paths_list(self):
		"""
		Returns list of paths to all completed xml files. If any force run is not complete, None is returned instead.
		"""

		return [Path.join(run_path, 'vasprun.xml') for run_path in self.get_run_paths_list()] if self.complete else None