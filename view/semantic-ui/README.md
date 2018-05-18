# view/semantic-ui

Holds the semantic-ui distribution used to make the custom theme for OPQ view.

This distribution of semantic-ui was installed using NPM. See [Semantic UI, Getting Started](http://semantic-ui.com/introduction/getting-started.html) for more details.

## Current theme customizations

Here is a summary of the modifications:

src/site/globals/site.variables

  * Define fonts: make Open Sans the default font and Lobster for the brand.
  * Define the color palette. Using a 'key lime pie' aesthetic. Also ICE Colors.
  
## Installation
  
If you are downloading this from GitHub, the node_modules directory needs to be built.  You do this by cd'ing into the view/semantic-ui directory and invoking:

```sh
$ npm install semantic-ui --save
```
  
To update to a new release of semantic-ui, try:

```
$ npm update
```

### Building a theme (semantic-ui repo only)
  
To build a new theme, from the view/semantic-ui directory, invoke:
 
```
$ cd semantic
$ gulp build
```

This will build the theme. You can display it by retrieving the index.html file.

### Build a theme (install into OPQ View)

To build a new theme *and* install it into the view application, invoke:

```
$ cd semantic
$ ./install-dist.sh
```

