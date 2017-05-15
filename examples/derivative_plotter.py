import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from fpctoolkit.io.file import File



data_file = File("C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/data/derivative_plot_data")


def get_plot(file_lines):
	x_data = []
	y_data = []

	header_line = file_lines[0]

	header_data = header_line.split(' ') #SrTiO3 a=3.79 encut=600eV kpoints=3x3x3M disp_step=0.01A u2 Energy

	title_string = header_data[0] + ' ' + header_data[1]
	right_title_string = header_data[2] + ' ' + header_data[3] + ' ' + header_data[4]

	x_label_string = header_data[5]
	y_label_string = header_data[6]

	for i in range(1, len(file_lines)):
		line = file_lines[i].strip()

		x_data.append(float(line.split(' ')[0]))
		y_data.append(float(line.split(' ')[1]))

	

	# ax = plt.gca()
	# ax.get_yaxis().get_major_formatter().set_scientific(True)

	plt.title(right_title_string, loc='right', size=8)
	plt.title(title_string)

	plt.xlabel(x_label_string, size=16)
	plt.ylabel(y_label_string, size=16)

	fitting_parameters = np.polyfit(x_data, y_data, 4)

	f = lambda x: fitting_parameters[0]*x**4.0 + fitting_parameters[1]*x**3.0 + fitting_parameters[2]*x**2.0 + fitting_parameters[3]*x + fitting_parameters[4]

	fit_x_data = []

	start_x = min(x_data)
	end_x = max(x_data)
	step = (max(x_data)-min(x_data))/500.0

	x = start_x
	while x <= end_x:
		fit_x_data.append(x)
		x += step

	fit_y_data = [f(x) for x in fit_x_data]


	fit_string = get_fit_string(fitting_parameters)
	plt.suptitle(fit_string)

	plt.plot(x_data, y_data, 'ro')
	plt.plot(fit_x_data, fit_y_data)

	plt.show()

def get_fit_string(fitting_parameters):

	fit_string = ''

	order = len(fitting_parameters) - 1

	for index in range(order+1):
		exp = order-index

		if exp > 1:
			exp_string = "*x^" + str(exp)
		elif exp == 1:
			exp_string = "*x"
		else:
			exp_string = ""


		fit_string += str(round(fitting_parameters[index], 3)) + exp_string + " + "


	return fit_string[:-2]



start_index = 0
end_index = None

for i, line in enumerate(data_file):
	if line.strip() == '':
		end_index = i



		get_plot(data_file[start_index:end_index])

		start_index = end_index+1