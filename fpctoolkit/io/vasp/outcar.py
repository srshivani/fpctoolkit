

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

class Outcar(File):
	
	run_complete_string = "Total CPU time used (sec):"
	ionic_step_complete_string = "aborting loop because EDIFF is reached"
	total_energy_string = "energy(sigma->0)"
	Outcar.dielectric_tensor_string = "MACROSCOPIC STATIC DIELECTRIC TENSOR (including local field effects in DFT)"

	def __init__(self, file_path=None):
		super(Outcar, self).__init__(file_path)


	def reload(self):
		"""Reloads from original file_path to refresh lines"""

		super(Outcar, self).__init__()		


	@property
	def complete(self):
		"""Searches the last few lines for the tag 'Total CPU time used (sec):'
		If this tag is present, returns True. Reverse traversing is done for
		efficiency.
		"""

		return bool(self.get_first_line_containing_string_from_bottom(Outcar.run_complete_string, stop_after=200))

	@property
	def energy(self):
		if not self.complete:
			raise Exception("Run does not have a final energy yet - not completed.")

		total_energy_line = self.get_first_line_containing_string_from_bottom(Outcar.total_energy_string)
		return float(total_energy_line.split('=')[-1].strip())


	@property
	def energy_per_atom(self):
		return self.energy / self.get_number_of_atoms()


	def get_ionic_energies(self):
		"""Returns list of energies (one for each ionic step) currently present in outcar"""

		ionic_step_data_start_line_indices = self.get_line_indices_containing_string(Outcar.ionic_step_complete_string)
		print ionic_step_data_start_line_indices
		##########unfinished

	def get_number_of_atoms(self):
		return self.get_incar_parameter_value("NIONS")


	def get_calculation_time_in_core_hours(self):
		"""In cpu*hours. Good for comparing speed up when moving from smaller to larger number of cores"""

		total_cpu_time = self.get_total_cpu_time()
		number_of_cores = self.get_number_of_cores()

		if (not total_cpu_time) or (not number_of_cores):
			return None
			
		cpu_hours = (total_cpu_time * number_of_cores) / 3600.0
		
		return round(cpu_hours, 2)

	def get_number_of_cores(self):
		"""Returns number of cores recorded in outcar"""

		core_count_line = self.get_first_line_containing_string_from_top("total cores") #may be fenrir specific!

		if not core_count_line:
			return None

		core_count_line = su.remove_extra_spaces(core_count_line)

		return int(core_count_line.split(' ')[2])

	def get_total_cpu_time(self):
		"""Returns number after Total CPU time used (sec): string"""

		cpu_time_line = self.get_first_line_containing_string_from_bottom("Total CPU time used (sec):")

		if not cpu_time_line:
			return None

		cpu_time_line = su.remove_extra_spaces(cpu_time_line).strip()

		return float(cpu_time_line.split(' ')[5])


	def get_incar_parameter_value(self, key):
		"""
		Key is some parameter that will be found in the outcar, such as NIONS or ISIF.
		Returns the value as string or numerical value if possible. Returns none if nothing
		found in outcar. Looks for first thing with spaces around it after the key name.
		"""

		containing_lines = self.get_lines_containing_string(key)

		if len(containing_lines) == 0:
			return None

		line = containing_lines[0]
		line = su.remove_extra_spaces(line).strip() #'bla bla NIONS = 40 bla bla bla'
		line = line.split(key)[1].strip() #get everything after key '= 40 bla bla bla'
		value = line.split(" ")[1]

		if su.string_represents_integer(value):
			return int(value)
		elif su.string_represents_float(value):
			return float(value)
		else:
			return value



	def get_dielectric_tensor(self):
		if not self.complete:
			raise Exception("Run does not yet have a dielectric tensor - not completed")

		tensor_start_indices = self.get_line_indices_containing_string(Outcar.dielectric_tensor_string)

		if len(tensor_start_indices == 0):
			raise Exception("No dielectric tensor found in completed outcar file")

		tensor_start_index = tensor_start_indices[-1] + 2

		dielectric_tensor = []

		for line in self.lines[tensor_start_index:tensor_start_index+3]:
			dielectric_tensor.append(su.get_number_list_from_string(line))

		return dielectric_tensor
