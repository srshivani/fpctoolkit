import random
import copy

from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.structure_prediction.individual import Individual
from fpctoolkit.workflow.parameter_list import ParameterList
from fpctoolkit.util.random_selector import RandomSelector

class GADriver(object):
	"""
	Abstract parent class defining the specifics of the GA search, including operators and how 
	individual calculation sets are defined
	"""

	def __init__(self, ga_input_dictionary, calculation_set_input_dictionary):
		"""
		At minimum, ga_input_dictionary looks like:

		{
			'max_number_of_generations': 15,
			'individuals_per_generation': [50, 40, 30], (flexible param list)
			'random_fractions_list': [1.0, 0.3, 0.2, ...],
			'mate_fractions_list': [0.0, 0.7, 0.8, ...]
		}

		Can also contain species lists, constraints, etc.
		"""

		self.ga_input_dictionary = ga_input_dictionary
		self.calculation_set_input_dictionary = calculation_set_input_dictionary

		self.individuals_per_generation = ParameterList(self.ga_input_dictionary['individuals_per_generation'])
		self.ga_input_dictionary = ga_input_dictionary
		self.calculation_set_input_dictionary = calculation_set_input_dictionary

		self.random_fractions_list = ParameterList(self.ga_input_dictionary['random_fractions_list']) if 'random_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])
		self.mate_fractions_list = ParameterList(self.ga_input_dictionary['mate_fractions_list']) if 'mate_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])
		self.mutate_fractions_list = ParameterList(self.ga_input_dictionary['mutate_fractions_list']) if 'mutate_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])
		self.permute_fractions_list = ParameterList(self.ga_input_dictionary['permute_fractions_list']) if 'permute_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])

	def get_new_individual(self, individual_path, population_of_last_generation, generation_number):
		"""
		Main workhorse - supplies an individual by randomly chosen means (heredity, random, mutate, ...etc.)
		"""

		return None

	def get_structure(self, population_of_last_generation, generation_number):
		

		probabilities_list = []
		probabilities_list.append(self.random_fractions_list[generation_number-1])
		probabilities_list.append(self.mate_fractions_list[generation_number-1])
		probabilities_list.append(self.mutate_fractions_list[generation_number-1])
		probabilities_list.append(self.permute_fractions_list[generation_number-1])

		random_selector = RandomSelector(probabilities_list)
		event_index = random_selector.get_event_index()

		if event_index == 0:
			return self.get_random_structure(population_of_last_generation)
		elif event_index == 1:
			return self.get_mated_structure(population_of_last_generation)
		elif event_index == 2:
			return self.get_mutated_structure(population_of_last_generation)
		elif event_index == 3:
			return self.get_permuted_structure(population_of_last_generation)


	def get_random_structure(self, population_of_last_generation):
		return None

	def get_mated_structure(self, population_of_last_generation):
		return None

	def get_mutated_structure(self, population_of_last_generation):
		return None

	def get_permuted_structure(self, population_of_last_generation):
		return None

	def get_individuals_per_generation(self, generation_number):
		return self.ga_input_dictionary['individuals_per_generation'][generation_number-1]

	def get_max_number_of_generations(self):
		return self.ga_input_dictionary['max_number_of_generations']

	def directory_to_individual_conversion_method(self, path):
		"""Default to a vasp relaxation"""

		return Individual(calculation_set=VaspRelaxation(path=path, input_dictionary=copy.deepcopy(self.calculation_set_input_dictionary)))