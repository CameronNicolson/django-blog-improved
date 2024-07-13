# Django Blog Improved

A free web-based engine for creating and managing blogs.

### Highlights 
* User-friendly interface to upload and manage your blogs
* Share posts online for the world to see
* Made to look great on mobile, tablet, and desktops
* Supports both Non-JavaScript and JavaScript browsers 
* Minimal Python
* Django framework support
* Tech-friendly Docs

## Table of contents

* Introduction
  * [Prerequisites](#prerequisites)
* Installation
  * [Install](#install)
  * [Testing](#testing)
* Contribute
  * [Getting Involved](#getting-involved)
  * [License](#license)

## Prerequisites

* `Python 3.10` or greater

* `PIP` most versions work 

## Install 

### Compile from source
Gain a copy of the source code.
```
# download via git
git clone https://github.com/CameronNicolson/django-blog-improved

# when done, move inside directory
cd django-blog-improved

# compile source code
pip install -e .

```
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

If a test fails, please consider reporting: [Report an Issue](https://github.com/CameronNicolson/django-blog-improved/issues).

Read the documentation: [Docs website](https://cameronnicolson.github.io/django-blog-improved/).

## Getting involved
Any questions or queries, please contact: github.cameron@nicolson.scot

### How to contribute?

See what's planned on the project's roadmap: [roadmap website](https://cameronnicolson.github.io/django-blog-improved/dev/roadmap.html), essentially that is my Todo / hopeful wishes.

You are invited to assign yourself to a task!

### Credits

Upon receiving your shared code. You retain your own copyright to all code submissions. Your credits also appear alongside the changes.

This is typical practice, perhaps obvious to some, but I want to emphasis that -- anyone wanting to help will be treated with utmost respect.

# License

![GPLv3 Logo](https://www.gnu.org/graphics/gplv3-with-text-136x68.png "AGPLv3 Logo")

All files are copyright of 2023-2024 Cameron Nicolson, unless stated otherwise.

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
