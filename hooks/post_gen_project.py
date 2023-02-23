import os
import numpy as np
import shutil
import json
PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def convert_ipynb_to_py(filepath):
    if not ".ipynb" in filepath:
        raise UserWarning("Invalid file type.")

    indentation = ""
    code = json.load(open(filepath))
    py_file = open(filepath.replace(".ipynb", ".py"), "w+")

    # Find line number where we finish imports
    first_20_lines = np.hstack([c["source"] for c in code['cells']])[0:20]
    ln_imports = np.where([(c[0:6] == "import") or (c[0:4] == "from") for c in first_20_lines])[0][-1] + 1

    # Cycle through lines
    ln = 0
    for cell in code['cells']:
        if cell['cell_type'] == 'code':
            #py_file.write('# -------- code --------\n')
            for line in cell['source']:
                # Apply manipulations, if necessary
                if (ln == ln_imports):
                    py_file.write("\n")
                    py_file.write('if __name__ == "__main__":\n')
                    indentation = "    "
                else:
                    line = line.replace("os.getcwd()", "os.path.dirname(os.path.abspath(__file__))")

                py_file.write("{:s}{:s}".format(indentation, line))
                ln += 1
            py_file.write("\n\n")
        elif cell['cell_type'] == 'markdown':
            for line in cell['source']:
                py_file.write("{:s}{:s} {:s}".format(indentation, "#", line))
            py_file.write("\n")
            ln += 1
    py_file.close()


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def remove_directory(filepath):
    #os.rmdir(os.path.join(PROJECT_DIRECTORY, filepath))
    shutil.rmtree(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == '__main__':
    # Remove example directories
    if '{{ cookiecutter.populate_with_examples }}' != 'y':
        remove_directory('python/export_energyratios_to_table')
        # remove_directory('_legacy')
        remove_directory('python/raw_data_processing')
        remove_directory('python/visualize_energy_ratios')
        remove_file(os.path.join("common_windfarm_information", "demo_dataset_metmast_600s.csv"))
        remove_file(os.path.join("common_windfarm_information", "demo_dataset_scada_600s.csv"))
    
    else:
        convert_ipynb_to_py('python/raw_data_processing/filter_ws_power_curves.ipynb')
        convert_ipynb_to_py('python/raw_data_processing/northing_calibration.ipynb')
