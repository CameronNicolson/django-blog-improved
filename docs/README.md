# Django Blog Improved documentation

The pages you see online can also be viewed locally from your computer.

Roughly, docs contains instructions on how to use DJ BIM. 

## Run the docs locally

```
cd _build/html
```

```
python -m http.server 3000
```

Go to [http://0.0.0.0:3000/](http://0.0.0.0:3000/) to read the docs.

## Build the docs

Static site Built with Markdown, Sphinx, and Read the Docs.

```
pip install -r requirements.txt
```

```
make html
``` 
