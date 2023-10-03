# Django Blog Improved

A free web-based engine for creating and managing blogs.

## Table of contents

* Introduction
  * [Features](#highlights)
  * [Prerequisites](#prerequisites)
* Installation
  * [Install](#install)
  * [Testing](#testing)
* Contribute
  * [Getting Involved](#getting-involved)
  * [License](#license)

## Highlights 
* User-friendly interface to upload and manage your blogs
* Share posts online for the world to see
* Made to look great on mobile, tablet, and desktops
* Supports both Non-JavaScript and JavaScript browsers 
* Minimal Python
* Django framework support
* Tech-friendly Docs

## Prerequisites
Things you will need before you begin. 

* `Python 3.6` or any version above

* `PIP` most versions work 

Check that these tools are available to your system.
```
python --version; pip --version
```

When successful, you are ready for the install guides.

## Install 

This section contains install instructions. Check out the [detailed docs for more](https://spongycake.codeberg.page/django-blog-improved/@master/docs/pages/usage/get-started.html#installation).

### Compile from source
Gain a copy of the project.
```
# download via git
git clone https://codeberg.org/spongycake/django-blog-improved

# when done, move inside directory
cd django-blog-improved

# compile source code
pip install -e .
```
Or with your web browser -
[Direct Download from Codeberg.org](https://codeberg.org/spongycake/django-blog-improved/archive/master.zip)

## Testing
Install the testing tools using pip: 
```
pip install -r requirements/local.txt
```
(optional) If you want lorem ipsum text, this script can expand dummy data. 
```
python populate_tests.py
```
Run all blog tests with:
```
python -m django test --setting "tests.settings"
```

If a test fails, please consider [reporting the failure](https://codeberg.org/spongycake/django-blog-improved/issues) on the project's issue tracker. 

Want the next moves? Jump into the [docs](https://spongycake.codeberg.page/django-blog-improved/@master/docs/pages/).

## Getting involved
I personally enjoy software that has a collective effort attached. So please consider sharing your ideas and improvements.

* Discussion in Matrix [#djangoblog:one.ems.host](https://matrix.to/#/#djangoblog:one.ems.host).

### How to contribute?

The challenge is to bring Django Blog Improved into a state where end-users  are protected from learning python and can pick-up and use easily.

Look at the [roadmap kanban](https://codeberg.org/spongycake/django-blog-improved/projects), essentially that is my Todo / hopeful wishes.

You are invited to assign yourself to a task. We can use the project board to organise ourselves.

### Credits

Upon receiving your shared code. You retain your own copyright to all code submissions. Your credits also appear alongside the changes.

This is typical practice, perhaps obvious to some, but I want to emphasis that -- anyone wanting to help will be treated with utmost respect.

# License

![GPLv3 Logo](https://www.gnu.org/graphics/gplv3-with-text-136x68.png "AGPLv3 Logo")

All files are copyright of 2023 Spongycake, unless stated otherwise.

Django Blog Improved is released under GPLv3. 
We conventionally placed the license in a file called [LICENSE](./LICENSE).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).
