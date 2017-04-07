#from fpctoolkit.workflow.vasp_phonon_run import VaspPhononRun

from phonopy import Phonopy
from phonopy.interface.vasp import read_vasp
from phonopy.interface.vasp import parse_set_of_forces, get_force_constants_from_vasprun_xmls
from phonopy.file_IO import parse_FORCE_SETS, parse_BORN
import numpy as np

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run_set import VaspRunSet

class VaspPhononRun(VaspRunSet):

	def __init__(self, path, initial_structure):
		self.path = path

		Path.make(path)

		initial_poscar_path = self.get_extended_path("initial_phonon_structure_POSCAR")

		initial_structure.to_poscar_file_path(initial_poscar_path)

		primitive_structure = read_vasp(initial_poscar_path)
		supercell_dimensions_matrix = np.diag([2, 2, 2])
		symprec = 0.001

		displacement_distance = 0.01

		# Initialize phonon. Supercell matrix has to have the shape of (3, 3)
		phonon = Phonopy(unitcell=primitive_structure, supercell_matrix=supercell_dimensions_matrix, symprec=symprec)

		symmetry = phonon.get_symmetry() #symprec=1e-5, angle_tolerance=-1.0
		print "Space group:", symmetry.get_international_table()

		phonon.generate_displacements(distance=displacement_distance)
		supercells = phonon.get_supercells_with_displacements()


		num_atoms = 40
		vasprun_xml_paths= [self.get_extended_path('vasprun_001.xml'), self.get_extended_path('vasprun_002.xml')]

		force_sets = parse_set_of_forces(num_atoms=num_atoms, forces_filenames=vasprun_xml_paths)


		#force_constants = get_force_constants_from_vasprun_xmls(vasprun_xml_paths)

		print force_sets

# def write_supercells_with_displacements(supercell,
#                                         cells_with_displacements):
#     write_vasp("SPOSCAR", supercell, direct=True)
#     for i, cell in enumerate(cells_with_displacements):
#         write_vasp('POSCAR-%03d' % (i + 1), cell, direct=True)

#     _write_magnetic_moments(supercell)
