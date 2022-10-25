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
## Host on Codeberg Pages 

This instruction is specific [Codeberg](https://codeberg.org)'s configuration. Codeberg hosts your files by looking for a directory called `pages`.

Sphinx likes to place html inside `_build`, this is not ideal for Codeberg. But we can change this behavior with the following, make sure you are in the root of docs.

```
sphinx-build . pages
```

[Read more about Codeberg Pages on their website](https://codeberg.page/)
