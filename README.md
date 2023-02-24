# flasc_cookiecutter_template
This repository hosts a Cookiecutter template for wind farm analysis projects using FLASC and FLORIS. It also includes a set of example scripts either with which to learn FLASC, or upon which to base your actual analysis scripts. To open a new project, you will need [Cruft](https://cruft.github.io/cruft/) (recommended) or Cookiecutter.

flasc_cookiecutter_template is developed and maintained by NREL, with community and industry support from, among others, Bart Doekemeijer (Shell Global Solutions International B.V.). Initial code architecture by Bart Doekemeijer.


## Creating your own package from this template
Cookiecutter is the standard and most widely used tool to create packages from templates such as this repository. In contrary to Cruft, Cookiecutter will create a standalone copy of this template that you can modify and add to as you please. Any updates in the upstream Cookiecutter template can not be pulled into your repository, and hence newer functionalities will not be easily available to your package. To keep your package in sync with the template, we suggest you to use Cruft.

To use Cruft, use
```
pip install cruft
cruft create https://github.com/Bartdoekemeijer/flasc_cookiecutter_template
pip install -e <new_package_name>/python
```

To use Cookiecutter, use
```
pip install cookiecutter
cookiecutter https://github.com/Bartdoekemeijer/flasc_cookiecutter_template
pip install -e <new_package_name>/python
```

And follow the interactive menus. If you use `cruft`, you can pull any future updates from this template into your package using
```
cruft check
cruft update
```

# License

Copyright 2023 NREL

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

