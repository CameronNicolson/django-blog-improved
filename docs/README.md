# Django Blog Improved documentation

Learn how to use django blog improved by reading the docs.

The HTML version is the recommended way to view from running a local http server from your computer. The instructions to do so are as follows. 

## Run the docs locally

```
cd build
```

```
python -m http.server 3000
```

Go to [http://0.0.0.0:3000/](http://0.0.0.0:3000/) to read the docs.

## Build the docs

Static site built with Sphinx.

```
pip install -r requirements.txt
```

```
sphinx-build source build
``` 

