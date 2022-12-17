# Django Blog Improved
[![Chat on Matrix](docs/_static/chat-on-matrix.svg "Chat on Matrix")](https://matrix.to/#/#djangoblog:one.ems.host)

A blog application, with popular features. Build a blog with Django framework.

![screenshot of blog homepage](docs/_static/screenshot.gif "screenshot of homepage of blog")

## Table of contents

* Introduction
  * [Features](#features)
  * [Prerequisites](#prerequisites)
* Installation
  * [Install](#install)
  * [Testing](#testing)
* Contribute
  * [Getting Involved](#getting-involved)
  * [Notes](#notes)
  * [License](#license)

## Features 

* **Navigation bar** - Auto-generate your site's navigation. It includes an accessory tag called `{{ navigation }}` for granular access

* **Breadcrumbs** - visualise the hierarchical structure of pages with a breadcrumb tag

* **Featured posts** - Enable posts as featured to apply new behaviour and create eye-catching properties

* **Categories** - Comes with a useful system for categorising and filtering content

* **Contact options** - Show/edit contact details across the entire site with one easy template tag

* **Request Callback** - Allow visitors to request a telephone call

* **Collaboration link** - Enable an edit link that directs to your git server

* **CV template** - Stylish way to show off your work

**And more**
* Wysiwyg editor 
* Sitemap
* ATOM, RSS Feeds
* Static assets 

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
### Download
Gain a copy of the project.
```
git clone https://codeberg.org/spongycake/django-blog-improved
```
[Direct Download](https://codeberg.org/spongycake/django-blog-improved/archive/master.zip)


### Step 1: Gather dependencies 
```
cd django-blog-improved
```
 Then run the install command
```
pip install -r requirements/base.txt
```
### Step 2: Security key 
Inside `config/settings.py` needs a secret key.

You can make your own or use this command:

```
python -c 'from django.core.management.utils import get_random_secret_key; \
            print(get_random_secret_key())'
```
```
sed -i 's/SECRET_KEY =/SECRET_KEY = "above output inside double speech marks"/g' config/settings.py
```
### Step 3: Connect a database
```
python manage.py makemigrations blog \

python manage.py migrate blog
```
SQLite is the default. Please read the official Django [documentation about databases](https://docs.djangoproject.com/en/4.1/ref/databases/).

### Step 4: Start the server

```
python manage.py runserver
```
Point to `http://127.0.0.1:8000` with a Web Browser.

### All Done

Want the next moves? Jump into the [docs](https://spongycake.codeberg.page/django-blog-improved/@master/docs/pages/).

## Testing
Install the testing tools using pip: 
```
pip install -r requirements/local.txt
```
Run this script to populate the blog with dummy data. 
```
python populate_tests.py
```
Check blog is functioning correctly with:
```
python manage.py test
```
Browse a testserver with mock articles and pages.

```
python manage.py collectstatic
# use to pull the demo images
```
Start the server:
```
python manage.py testserver blog/fixtures/*.yaml
```
If a test fails, please consider [reporting the issue](https://codeberg.org/spongycake/django-blog-improved/issues) on the project's bug tracker. The next step is to press `New Issue` after loading the webpage.

## Getting involved
I personally enjoy software that has a collective effort attached. So please consider sharing your ideas and improvements.

Discussion in Matrix [#djangoblog:one.ems.host](https://matrix.to/#/#djangoblog:one.ems.host).

### How to contribute?

The challenge is to bring Django Blog Improved into a state where end-users  are protected from learning python and can pick-up and use easily.

Look at the [roadmap kanban](https://codeberg.org/spongycake/django-blog-improved/projects), essentially that is my Todo / hopeful wishes.

You are invited to assign yourself to a task. We can use the project board to organise ourselves.

### Credits

Upon receiving your shared code. You retain your own copyright to all code submissions. Your credits also appear alongside the changes.

This is typical practice, perhaps obvious to some, but I want to emphasis that -- anyone wanting to help will be treated with utmost respect.

## Notes

### Rigid Styles
The style sheets & JavaScript elements are "hard-linked" to Spongy Frontend. 

In other words, if you wish for Twitter Bootstrap, you will need to apply extra work to incorporate that design.

### Commenting system
You cannot comment on posts. Why? Though, the code remains inside the program (you are free to enable) it is unreachable upon install. 

Think of the risks; the current comment system is simple and holds no protection, akin to paper armour. Spam and bots could exploit this situation.

Web authors looking for comments and protection should look to "battle-tested" solutions and deploy them alongside the program.  

# License

![AGPLv3 Logo](https://www.gnu.org/graphics/agplv3-155x51.png "AGPLv3 Logo")

All files are copyright of 2022 SpongyCake, unless stated otherwise.

Django Blog Improved is released under AGPLv3. 

We conventionally placed the license in a file called [LICENSE.txt](./LICENSE.txt). 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).
