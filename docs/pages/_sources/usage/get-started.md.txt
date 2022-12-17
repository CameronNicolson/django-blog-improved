# Get Started 

Get started has basic installation and blog management guides. 

Following along with ___get started___ should give you a blog application that you can start using.

```{contents}
:depth: 3
```

## Installation

This section contains documentation on installing a new Django Blog Improved deployment.

### Requirements

To build DJ BIM you need: 

* `Python 3.6` or any version above

* `PIP` most versions work 

Check that these tools are available to your system. Open a terminal program for the following.

```
python --version; pip --version
```

If both versions print to screen then you have satisfied the requirements. 

### Download
First we want a copy of DJ BIM for our computer/server. You have 2 options available to you. 

Git or direct download. 

#### 1. Using git

Git is DJ BIM's chosen versioning control. It can keep the software up-to-date even after the intial download and much more.

```
git clone https://codeberg.org/spongycake/django-blog-improved
```

Upon completion, list the files in your current directory and you should find a folder named django-blog-improved.

#### 2. Direct Download

Direct download link. Open in Web Browser.
[https://codeberg.org/spongycake/django-blog-improved/archive/master.zip](https://codeberg.org/spongycake/django-blog-improved/archive/master.zip)

#### Or using the command line:
```
wget https://codeberg.org/spongycake/django-blog-improved/archive/master.zip
```

### Starting the install

#### Step 1: Gather dependencies 
DJ BIM is made of different parts, one such part is Django, so we need to pull those extra bits. 

Move inside the DJ BIM folder or whatever you named the download to.

```
cd django-blog-improved
```

```{note} We recommend starting a Python virtual environment, to prevent any package clashing. 
Not sure? check out djangogirls' [useful tutorial](https://tutorial.djangogirls.org/en/installation/#virtualenv).

python -m venv myvenv \ 

source ./myvenv/bin/activte 
```

Next up, PIP is going to help us bring the right dependencies to our project. Typically we only need to use the `pip install` command once in awhile.

```
pip install -r requirements/base.txt
```
The state of PIP is typically reflected in the terminal with progress bars and messages. 

When things arrive at completion, you may verify Django is ready for you.

```
python manage.py shell
```

### Step 2: Security key 
Inside `config/settings.py` reads the following
```
SECRET_KEY# <place your secret key here>
```
Obtaining a secret key is part of your website's security. It must be unique to you. 

Generate a unique key using this helpful shell command (optional). Or place your own key instead.

```
python -c 'from django.core.management.utils import get_random_secret_key; \
            print(get_random_secret_key())'
```
Then transfer the output into `config/settings.py`. For example:

If the install is happening on a *nix machine, __optional__ `sed -i 's/SECRET_KEY =/SECRET_KEY = "replace with your code"/g' config/settings.py` will edit the line for you.

Your settings now should look similar to the example below.

```
SECRET_kEY = "+mh)7c$31h4rp=dkdo!not-copy/this(%q&p^gb*)em%k#-$=06=zs(*"
```
 
### Step 3: Connect a database

Databases are meant to store the blog posts, user details, among other things. We need to tell Django which database technology we intend to use.

By default SQLite is used. There are options for other databases too, like Postgres and MariaDB and require additional configuration.

If you are happy with the default database then proceed with the following command.

```
python manage.py makemigrations \

python manage.py migrate 
```
Other database options will require you to update your `config/settings.py`. Please read the official Django [documentation about databases](https://docs.djangoproject.com/en/4.1/ref/databases/).

### Step 4: Start the server

```
python manage.py runserver
```
The server will try and attach itself to port `8000`.

Point to `http://127.0.0.1:8000` with a Web Browser. A website should appear without warnings.

## Testing

There is test data provided already. Testing is useful for checking the health of your blog.

Running these tests does not interfere with your production database. 

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
### Demo site

The demo component gives an impression of what DJ BIM blog can look like after content is supplied.

Start the demo on the development web server. Then locally browse entries of blog posts and media.

```{note}
Demo looks better with images!

A static files location must be generated in order for the Webserver to know the correct directory to make public to visitors. Directories marked `media` may be available to Django and hidden from visitors. For example, uploaded pictures wait for safety approval before going live.  The development server has a media directory, however we still need a static too. 
```

Command for static files and sample images:

```
python manage.py collectstatic
```

#### Start the demo server
Start the demo:
```
python manage.py testserver blog/fixtures/*.yaml
```

If a test fails, please consider [reporting the issue](https://codeberg.org/spongycake/django-blog-improved/issues) on the project's bug tracker. The next step is to press `New Issue` after loading the webpage.

## Blog management 

### Creating posts

You can create posts from within the admin portal. The admin page begin at subpath `/admin/` e.g. [http://127.0.0.1/admin/](https://fsf.org).

```{image} ../_static/django-admin-login.jpg
:alt: Django admin login page
:class: .screenshot
```

Once logged in, navigate to the `Blog` module inside the admin home. 

```{image} ../_static/django-admin-find-blog.jpg
:alt: Admin homepage, orange arrow denotes where the blog module is resides
:class: .screenshot
```
```{note} Alternatively, [http:127.0.0.1/admin/blog/](http://127.0.0.1/admin/blog/) takes you to the same options.
```
If you want to write a post then choose one of the three types:

1. {ref}`post`
2. {ref}`post-with-git`
3. {ref}`post-redirect`

You can then click the __(+) Add__ button to proceed. You will be directed towards a creation page and can begin filling out the fields.

The save button guarantees your posts are written in storage, it is located at the bottom of the creation page.

#### Status and visibility

There is a difference between creating drafted and published works. For example, drafts will not appear in public scenes, instead drafts are kept for the admin portal only. 

If you have decided your work is ready to be displayed on parts of your website, then change status value to `status: publish`. These values can be toggled at any point. 

(post)=
#### Post
Post are just normal posts that you would expect on any other blogging platform. You can set titles, author, content.

(post-with-git)=
#### Post with Git

Post with Git is identical to {ref}`post` with an extra attribute, adding a page source feature. The attribute is named `associated git repository`. 

This is useful in scenarios when we accept writer collaboration and invite readers to view the source code of your article / tutorial / list.

Git repository takes a URL as a value. After entering a git repo, you will now see a link at the bottom of the post `Edit`.

(post-redirect)=
#### Post Redirect

Redirect is useful for linking to resources other than a typical blog post. Redirect share a likeness to normal posts i.e. appears in the blog, except it contains a URL option. When a URL is set, the user can expect to be taken to locations that are not blog related.

For example, let's say you want to promote your YouTube channel. You create a post redirect "My first video". After publish, a user clicking is taken to YouTube.com. 

