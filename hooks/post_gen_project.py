# Copyright 2023 NREL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import glob
import os
import requests
# import numpy as np
import shutil
# import json
from zipfile import ZipFile

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


# def convert_ipynb_to_py(filepath):
#     if not ".ipynb" in filepath:
#         raise UserWarning("Invalid file type.")

#     indentation = ""
#     code = json.load(open(filepath))
#     py_file = open(filepath.replace(".ipynb", ".py"), "w+")

#     # Find line number where we finish imports
#     first_20_lines = np.hstack([c["source"] for c in code['cells']])[0:20]
#     ln_imports = np.where([(c[0:6] == "import") or (c[0:4] == "from") for c in first_20_lines])[0][-1] + 1

#     # Cycle through lines
#     ln = 0
#     for cell in code['cells']:
#         if cell['cell_type'] == 'code':
#             #py_file.write('# -------- code --------\n')
#             for line in cell['source']:
#                 # Apply manipulations, if necessary
#                 if (ln == ln_imports):
#                     py_file.write("\n")
#                     py_file.write('if __name__ == "__main__":\n')
#                     indentation = "    "
#                 else:
#                     line = line.replace("os.getcwd()", "os.path.dirname(os.path.abspath(__file__))")

#                 py_file.write("{:s}{:s}".format(indentation, line))
#                 ln += 1
#             py_file.write("\n\n")
#         elif cell['cell_type'] == 'markdown':
#             for line in cell['source']:
#                 py_file.write("{:s}{:s} {:s}".format(indentation, "#", line))
#             py_file.write("\n")
#             ln += 1
#     py_file.close()


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def remove_directory(filepath):
    shutil.rmtree(os.path.join(PROJECT_DIRECTORY, filepath))


def remove_lines_in_python_file(filepath, substr_start=None, substr_end=None):
    root_path = os.path.dirname(os.path.abspath(__file__))
    write_lines = (substr_start is not None)
    with open(filepath, "rt") as fin:
        tmp_file = os.path.join(root_path, "tmp", "_tmp.txt")
        with open(tmp_file, "wt") as fout:
            for line in fin:
                if write_lines:
                    if substr_start in line:
                        write_lines = False
                
                if write_lines:
                    fout.write(line)

                if not write_lines and substr_end is not None:
                    if substr_end in line:
                        write_lines = True

    # Replace file with temporary file
    os.remove(filepath)
    os.rename(tmp_file, filepath)

def replace_str_in_python_file(filepath, str_old, str_new):
    root_path = os.path.dirname(os.path.abspath(__file__))
    with open(filepath, "rt") as fin:
        tmp_file = os.path.join(root_path, "tmp", "_tmp.txt")
        with open(tmp_file, "wt") as fout:
            for line in fin:
                fout.write(line.replace(str_old, str_new))

    # Replace file with temporary file
    os.remove(filepath)
    os.rename(tmp_file, filepath)


def download_flasc_examples(branch: str = "main", subfolder: str = "examples_artificial_data", chunk_size=120):
    if branch == "main":
        url = r"https://github.com/NREL/flasc/archive/refs/heads/main.zip"
    elif branch == "develop":
        url = r"https://github.com/NREL/flasc/archive/refs/heads/develop.zip"
    else:
        raise UserWarning("Unfamiliar branch specified.")

    # Create tmp directory
    r = requests.get(url, stream=True)
    root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_path = os.path.join(root_path, "tmp")
    os.makedirs(tmp_path, exist_ok=True)

    # Download file
    filename = os.path.join(tmp_path, "flasc_repository.zip")
    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    print(f"Finished downloading '{filename}'.")

    # Unzip the file
    with ZipFile(filename) as zipfile:
        zipfile.extractall(tmp_path)
    
    # Specify where the files live
    print("Importing FLASC example scripts and customizing to this repository...")
    src_path = os.path.join(tmp_path, f"flasc-{branch}", subfolder)

    # Now replace certain strings in all Python and Python Notebook files
    py_files = [
        *glob.glob(os.path.join(src_path, "*.py")),
        *glob.glob(os.path.join(src_path, "*.ipynb")),
        *glob.glob(os.path.join(src_path, "**", "*.py")),
        *glob.glob(os.path.join(src_path, "**", "*.ipynb"))
    ]

    if subfolder == "examples_artificial_data":
        # Format artificial data processing files into FCT format
        for fn in py_files:
            replace_str_in_python_file(fn, "from flasc.examples.models import load_floris_artificial as load_floris", "from {{cookiecutter.project_slug}}.models import load_floris")

        # Now move raw data file to 'common_windfarm_information' folder
        shutil.move(
            os.path.join(src_path, "raw_data_processing", "data", "raw_artificial_data.zip"),
            os.path.join(root_path, "..", "{{cookiecutter.project_slug}}", "common_windfarm_information", "raw_artificial_data.zip"),
            copy_function=shutil.copy2
        )

        # Replace where we load the raw data file from, since now the file has been moved
        replace_str_in_python_file(
            os.path.join(src_path, "raw_data_processing", "filter_ws_power_curves.ipynb"),
            'source_path = os.path.join(root_path, \\"data\\")',
            'source_path = os.path.join(root_path, \\"..\\", \\"..\\", \\"common_windfarm_information\\")'
        )

        replace_str_in_python_file(
            os.path.join(src_path, "raw_data_processing", "filter_ws_power_curves.ipynb"),
            'zipfile.extractall(\\"data\\")',
            'zipfile.extractall(source_path)'
        )
    else:
        # Format Smarteole data processing files into FCT format
        subdir = os.path.join(src_path, "experiment_analysis")
        os.makedirs(subdir, exist_ok=True)
        for fn in py_files:
            replace_str_in_python_file(
                fn,
                "from flasc.examples.models import load_floris_smarteole as load_floris",
                "from {{cookiecutter.project_slug}}.models import load_floris"
            )
            shutil.move(fn, os.path.join(subdir, os.path.basename(fn)))

    # Now move remaining Python files to correct directory
    for subpath in glob.glob(os.path.join(src_path, "*")):
        shutil.move(
            subpath,
            os.path.join(root_path, "..", "{{cookiecutter.project_slug}}", "python"),
            copy_function=shutil.copy2
        )

    # Update models.py to fit in FCT format
    fn = os.path.join(src_path, "..", "flasc", "examples", "models.py")
    if subfolder == "examples_artificial_data":
        replace_str_in_python_file(
            filepath=fn,
            str_old="load_floris_artificial",
            str_new="load_floris"
        )
        replace_str_in_python_file(
            filepath=fn,
            str_old="floris_input_artificial",
            str_new="floris_inputs"
        )
        remove_lines_in_python_file(
            fn,
            substr_start="def load_floris_smarteole(",
            substr_end="return (fi, turbine_weights)"
        )
        remove_lines_in_python_file(
            fn,
            substr_start="# Load and time the Smarteole FLORIS model",
            substr_end="plot_floris_layout(fi,"
        )
        shutil.move(
            os.path.join(src_path, "..", "flasc", "examples", "floris_input_artificial"),
            os.path.join(root_path, "..", "{{cookiecutter.project_slug}}", "python", "{{cookiecutter.project_slug}}", "floris_inputs"),
            copy_function=shutil.copy2
        )

    else:
        replace_str_in_python_file(
            fn,
            str_old="load_floris_smarteole",
            str_new="load_floris"
        )
        replace_str_in_python_file(
            filepath=fn,
            str_old="floris_input_smarteole",
            str_new="floris_inputs"
        )
        remove_lines_in_python_file(
            fn,
            substr_start="def load_floris_artificial(",
            substr_end="return (fi, turbine_weights)"
        )
        remove_lines_in_python_file(
            fn,
            substr_start="# Load and time the artificial FLORIS model",
            substr_end="plot_floris_layout(fi,"
        )

        shutil.move(
            os.path.join(src_path, "..", "flasc", "examples", "floris_input_smarteole"),
            os.path.join(root_path, "..", "{{cookiecutter.project_slug}}", "python", "{{cookiecutter.project_slug}}", "floris_inputs"),
            copy_function=shutil.copy2
        )

    # Now copy models.py and input files from flasc/examples/models.py
    shutil.move(
        os.path.join(src_path, "..", "flasc", "examples", "models.py"),
        os.path.join(root_path, "..", "{{cookiecutter.project_slug}}", "python", "{{cookiecutter.project_slug}}", "models.py"),
        copy_function=shutil.copy2
    )
    
    # Remove 'tmp' directory
    shutil.rmtree(tmp_path)

if __name__ == '__main__':
    # Force it now
    # download_flasc_examples(branch='develop', subfolder="examples_artificial_data")
    download_flasc_examples(branch='develop', subfolder="examples_smarteole")

    # Populate repository with examples, if necessary
    if '{{ cookiecutter.populate_with_examples }}' == "Artificial SCADA data analysis examples from the 'flasc/main' branch":
        download_flasc_examples(branch='main')
    elif '{{ cookiecutter.populate_with_examples }}' == "Artificial SCADA data analysis examples from the 'flasc/develop' branch":
        download_flasc_examples(branch='develop')
    elif '{{ cookiecutter.populate_with_examples }}' == "Smarteole wake steering campaign analysis examples from the 'flasc/main' branch":
        download_flasc_examples(branch='main')
    elif '{{ cookiecutter.populate_with_examples }}' == "Smarteole wake steering campaign analysis examples from the 'flasc/develop' branch":
        download_flasc_examples(branch='develop')

    # # Remove example directories
    # if '{{ cookiecutter.populate_with_examples }}' != 'y':
    # # if '{{ cookiecutter.populate_with_examples }}' != 'y':
    #     remove_directory('python/export_energyratios_to_table')
    #     # remove_directory('_legacy')
    #     remove_directory('python/raw_data_processing')
    #     remove_directory('python/visualize_energy_ratios')
    #     remove_file(os.path.join("common_windfarm_information", "demo_dataset_metmast_600s.csv"))
    #     remove_file(os.path.join("common_windfarm_information", "demo_dataset_scada_600s.csv"))
    
    # else:
    #     convert_ipynb_to_py('python/raw_data_processing/filter_ws_power_curves.ipynb')
    #     convert_ipynb_to_py('python/raw_data_processing/northing_calibration.ipynb')
