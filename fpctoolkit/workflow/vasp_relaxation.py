import collections
import cPickle

from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.workflow.parameter_list import ParameterList
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.structure.structure import Structure
from fpctoolkit.util.path import Path
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.util.queue_adapter import QueueAdapter, QueueStatus

class VaspRelaxation(VaspRunSet):
	"""
	Collection of runs that form a relaxation.

	Contcar of last run in set always become poscar of next run.
	
	Incar and kpoints at each step can be custom specified. Modification
	lists do not have to be the same length as the number of vasp runs in
	the collection - if not then the default is to apply the last modification
	in the list to all future steps. See below for example input dictionary.

	The number of relaxation steps in for this run set is fixed - if run_count is
	4, then four external relaxations (isif = 3) will be performed before running a static (5 runs total).

	If external_relaxation_count == 0, then only a static is performed

	To not have wavecars copied and used in the relaxation chain to increase performance, include WAVECAR=Flase in the
	incar modifications. If wavecar exists in previous relax step's output, it will be copied to next step.
	
	Input dicitonary should look something like:
	{
		'external_relaxation_count': 4		
		'kpoint_schemes_list': ['Gamma'],
		'kpoint_subdivisions_lists': [[1, 1, 1], [1, 1, 2], [2, 2, 4]],
		'submission_script_modification_keys_list': ['100', 'standard', 'standard_gamma'], #optional - will default to whatever queue adapter gives
		'submission_node_count_list': [1, 2],
		'ediff': [0.001, 0.00001, 0.0000001],
		'encut': [200, 400, 600, 800],
		'isif' : [21, 33, 111]
		#any other incar parameters with value as a list
	}

	"""

	external_relax_basename_string = "relax_"
	static_basename_string = "static"

	def __init__(self, path, initial_structure=None, input_dictionary=None, verbose=True):
		"""
		Cases:
		1. path does not exist or is empty ==> make the relaxation directory, enforce input file arguments all exists
		2. path exists and is non-empty
			1. If input_dictionary is None, load in old input_dictionary that was saved and use that
			2. Else, use current input_dictionary
		"""

		self.path = Path.clean(path)
		self.verbose = verbose
		#self.run_count = 0 #how many runs have been initiated
		self.vasp_run_list = []

		self.initial_structure = initial_structure



		self.vasp_run_list = []

		if not Path.exists(self.path) or Path.is_empty(self.path): #self.path is either an empty directory or does not exist
			Path.make(self.path)
		else: #self.path is a non-empty directory. See if there's an old relaxation to load
			if not input_dictionary:
				if Path.exists(self.get_save_path()):
					raise Exception("No input_dictionary given, future implementation should load it here. Not yet supported.")
					input_dictionary = {} #load input dictionary*******************************************************************
					#self.load()	
				else: #input_dictionary parameter is none, but no input_dict saved either This case is not yet supported
					raise Exception("No input_dictionary given, but also no input_dictionary saved to path. Not yet supported.")

		self.load_input_dictionary(input_dictionary)

		self.initialize_run_list()
			
		#self.save()

	def load_input_dictionary(self, input_dictionary):
		"""Takes items in input_dictionary and loads them into self."""

		self.external_relaxation_count = input_dictionary.pop('external_relaxation_count')
		self.kpoint_schemes = ParameterList(input_dictionary.pop('kpoint_schemes_list'))
		self.kpoint_subdivisions_lists = ParameterList(input_dictionary.pop('kpoint_subdivisions_lists'))

		#optional keys
		self.submission_script_modification_keys_list = ParameterList(input_dictionary.pop('submission_script_modification_keys_list')) if 'submission_script_modification_keys_list' in input_dictionary else None
		self.submission_node_count_list = ParameterList(input_dictionary.pop('submission_node_count_list')) if 'submission_node_count_list' in input_dictionary else None

		if self.external_relaxation_count < 0:
			raise Exception("Must have one or more external relaxations")

		self.incar_modifier_lists_dictionary = {}
		for key, value in input_dictionary.items():
			if not isinstance(value, collections.Sequence):
				raise Exception("Incar modifier lists in input dictionary must be given as sequences")
			else:
				self.incar_modifier_lists_dictionary[key] = ParameterList(value)

	def initialize_run_list(self):
		"""sets self.vasp_run_list based on directories present"""

		self.vasp_run_list = []

		for i in range(self.external_relaxation_count):
			run_path = self.get_extended_path(VaspRelaxation.external_relax_basename_string + str(i+1))
			if Path.exists(run_path):
				self.vasp_run_list.append(VaspRun(run_path), verbose=self.verbose)
			else:
				return

		static_path = self.get_extended_path(VaspRelaxation.static_basename_string)
		if Path.exists(static_path):
			self.vasp_run_list.append(VaspRun(static_path), verbose=self.verbose)

	@property
	def complete(self):
		return (self.run_count == self.external_relaxation_count + 1) and self.get_current_vasp_run().complete

	@property
	def run_count(self):
		"""Counts through the directories created that represent runs"""

		return len(self.vasp_run_list)

	@property
	def final_energy(self, per_atom=False):
		"""Returns static energy if static is complete, else returns None"""

		if self.complete:
			return self.get_current_vasp_run().final_energy(per_atom)
		else:
			return None

	@property
	def total_time(self, in_cpu_hours=True):
		"""Defaults to cpu*hours for now (best measure of total resources used)"""

		return sum([run.total_time for run in self.vasp_run_list if run.complete])

	def inner_update(self):

		if self.complete:
			return True
		elif self.run_count == 0 or self.get_current_vasp_run().complete:
			self.create_next_run()

		self.get_current_vasp_run().update()

		#delete all wavecars when finished or if True is returned

	def update(self):
		completed = self.inner_update()
		self.save()
		return completed

	def create_next_run(self):
		run_path = self.get_next_run_path()


		structure = self.get_next_structure()
		kpoints = Kpoints(scheme_string=self.kpoint_schemes[self.run_count], subdivisions_list=self.kpoint_subdivisions_lists[self.run_count])
		incar = self.get_next_incar()

		submission_script_file = None
		if self.submission_script_modification_keys_list:
			submission_script_file = QueueAdapter.modify_submission_script(QueueAdapter.get_submission_file(), self.submission_script_modification_keys_list[self.run_count])

		input_set = VaspInputSet(structure, kpoints, incar, submission_script_file=submission_script_file)

		#Override node count in submission script over the auto generated count based on atom count
		if self.submission_node_count_list:
			input_set.set_node_count(self.submission_node_count_list[self.run_count])


		vasp_run = VaspRun(run_path, input_set=input_set, verbose=self.verbose, wavecar_path=self.get_wavecar_path(), verbose=self.verbose)

		#self.run_count += 1 #increment at end - this tracks how many runs have been created up to now
		self.vasp_run_list.append(vasp_run)

	def get_next_incar(self):
		"""
		Returns the incar corresponding to the next run in the relaxation set
		"""

		incar_modifications_dict = {} #will look like {'ediff':base_ediff, 'encut':encut, ...}
		for key, value_list in self.incar_modifier_lists_dictionary.items():
			incar_modifications_dict[key] = value_list[self.run_count]

		if self.run_count < self.external_relaxation_count:
			incar = IncarMaker.get_external_relaxation_incar(incar_modifications_dict)
		else:
			incar = IncarMaker.get_static_incar(incar_modifications_dict)

		return incar
	
	def get_wavecar_path(self):
		"""
		If lwave of current run is true, returns path to wavecar of current run, else None
		"""
		if self.run_count == 0:
			return None

		current_run = self.get_current_vasp_run()
		if current_run.incar['lwave']:
			wavecar_path = current_run.get_extended_path('WAVECAR')

		return wavecar_path if Path.exists(wavecar_path) else None

	def get_next_structure(self):
		"""If first relax, return self.initial_structure, else, get the contcar from the current run"""

		if self.run_count == 0:
			return self.initial_structure

		current_contcar_path = self.get_current_vasp_run().get_extended_path('CONTCAR')
		print current_contcar_path
		if not Path.exists(current_contcar_path):
			raise Exception("Method get_next_structure called, but Contcar for current run doesn't exist")
		elif not self.get_current_vasp_run().complete:
			raise Exception("Method get_next_structure called, but current run is not yet complete")

		return Structure(current_contcar_path)

	def get_next_run_path_basename(self):
		"""
		Returns relax_1 if no relaxes, returns relax_4 if three other relaxes exist, 
		returns static if self.run_count == self.external_relaxation_count
		"""

		if self.run_count == self.external_relaxation_count:
			return VaspRelaxation.static_basename_string
		else:
			return VaspRelaxation.external_relax_basename_string + str(self.run_count + 1)

	def get_next_run_path(self):
		return self.get_extended_path(self.get_next_run_path_basename())


	def get_current_run_path_basename(self):
		if self.run_count == self.external_relaxation_count:
			return 'static'
		else:
			return 'relax_' + str(self.run_count)

	def get_current_run_path(self):
		return self.get_extended_path(self.get_current_run_path_basename())


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".relaxation_pickle")

	def get_current_vasp_run(self):
		if self.run_count == 0:
			raise Exception("No runs have been created yet - no current run exists")
		else:
			return self.vasp_run_list[self.run_count-1]



	def save(self):
		"""
		Saves class to pickled file at {self.path}/.relaxation_pickle

		Saves all attributes except vasp_run_list - this list is recreated
		later by saving all runs now and loading them later from the run directories. 
		"""
		return #********************************************************
		save_path = self.get_save_path()

		#save_dictionary = {key: value for key, value in self.__dict__.items() if not key == 'vasp_run_list'}
		save_dictionary = {'run_count': self.__dict__['run_count']} #############################################need to think about what to save!

		file = open(save_path, 'w')
		file.write(cPickle.dumps(save_dictionary))
		file.close()

		for run in self.vasp_run_list:
			run.save()

	def load(self, load_path=None):
		previous_path = self.path
		previous_verbose = self.verbose

		if not load_path:
			load_path = self.get_save_path()

		if not Path.exists(load_path):
			self.log("Load file path does not exist: " + load_path, raise_exception=True)

		file = open(load_path, 'r')
		data_pickle = file.read()
		file.close()

		load_dictionary = cPickle.loads(data_pickle) #need to think about what to save
		self.__dict__['run_count'] = load_dictionary['run_count']

		self.verbose = previous_verbose #so this can be overridden upon init
		self.path = previous_path #in case relaxation is moved

		saved_run_count = self.run_count

		self.vasp_run_list = []
		self.run_count = 0

		for count in range(saved_run_count):
			self.vasp_run_list.append(VaspRun(path=self.get_next_run_path()))

			self.run_count += 1


	def view(self, files_to_view=['Potcar', 'Kpoints', 'Incar', 'Poscar', 'Contcar', 'Submit.sh', '_JOB_OUTPUT.txt']):
		"""
		See printing of actual text input files written in run directories, not internally stored input files.
		Useful for validating runs.

		files_to_view list is case insensitive - it will find 'POSCAR' file if you input 'poscar' for instance
		"""

		extend_count = 200

		print "\n"*5
		print "-"*extend_count
		print "-"*extend_count
		print "-"*extend_count
		print "           Relaxation Run at " + self.path
		print "-"*extend_count
		print "-"*extend_count
		print "-"*extend_count

		for run_count, run in enumerate(self.vasp_run_list):
			run_str = ""

			if run_count == self.external_relaxation_count:
				run_str = "Static Run"
			else:
				run_str = "Relax_" + str(run_count + 1)

			print "\n"
			print "V"*80 + "__  " + run_str + "  __" + "V"*80
			print "\n"*3
			run.view(files_to_view)
			print "\n"*3
			print "^"*80 + "__  END " + run_str + "  __" + "^"*80
			print "\n"

		print "o"*extend_count
		print "          END Relaxation Run at " + self.path
		print "o"*extend_count

		print "\n"*2