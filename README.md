Plug-and-play blogging for your Django project.

# Django Blog Improved

A collection of django template tags which supports a blogging platform underneath. This modular design allows developers to use only the blogging elements they need without scarifying a preexisting setup. 

### Highlights 
* Common blogging class models (Post, Categories, Media, User Profile)
* _postlist_ tag 
* configure pages - author and author group pages

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

* `PIP 23.0` or greater 

* `Django 4.2` or greater

## Install 

### Compile from source
Get a copy of the source code.
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
pip install -r tests/requirements.txt
```

Run all blog tests with:
```
python runtests.py
```

If a test fails, please consider reporting: [Report an Issue](https://github.com/CameronNicolson/django-blog-improved/issues).

Read the documentation: [Docs website](https://cameronnicolson.github.io/django-blog-improved/).

### How to contribute?

See what's planned on the project's roadmap: [roadmap website](https://cameronnicolson.github.io/django-blog-improved/roadmap.html), essentially that is my Todo / hopeful wishes.

You are invited to assign yourself to a task!

# License

![GPLv3 Logo](https://www.gnu.org/graphics/gplv3-with-text-136x68.png "AGPLv3 Logo")

All files are copyright of 2023-2025 Cameron Nicolson, unless stated otherwise.

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
