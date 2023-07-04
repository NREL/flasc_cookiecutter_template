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
import numpy as np
import shutil
import json
from zipfile import ZipFile

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
    shutil.rmtree(os.path.join(PROJECT_DIRECTORY, filepath))

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
    print("done")
    

def download_flasc_examples(branch: str = "main", chunk_size=120):
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
    
    # Move all example files over
    print("Importing FLASC example scripts and customizing to this repository...")
    src_path = os.path.join(tmp_path, f"flasc-{branch}", "examples_artificial_data")

    # Now replace certain strings in all files
    py_files = glob.glob(os.path.join(src_path, "**", "*.py"))
    for fn in py_files:
        replace_str_in_python_file(fn, "from flasc.examples.models import load_floris_artificial as load_floris", "from {{cookiecutter.project_slug}}.models import load_floris")

    # Now move files to correct directory
    for subpath in glob.glob(os.path.join(src_path, "*")):
        shutil.move(
            subpath,
            os.path.join(root_path, "..", "{{cookiecutter.project_slug}}", "python"),
            copy_function=shutil.copy2
        )



    # Remove 'tmp' directory
    os.rmdir(tmp_path)

if __name__ == '__main__':
    # Download file
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
