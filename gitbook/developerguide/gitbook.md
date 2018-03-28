# GitBook

This manual is produced using [GitBook](http://gitbook.com).

The top-level [book.json](https://github.com/openpowerquality/opq/blob/master/book.json) file provides global configuration information, and also tells GitBook that the files are all located in the gitbook/ subdirectory.

To develop GitBook documentation, you will want to [install GitBook locally](http://toolchain.gitbook.com/setup.html). Then run `gitbook install` followed by `gitbook serve` at the top-level of the radgrad repo to build a local version of the book:

```
[~/github/openpowerquality/opq]-> gitbook serve
Live reload server started on port: 35729
Press CTRL+C to quit ...

info: 8 plugins are installed 
info: 7 explicitly listed 
info: loading plugin "anchors"... OK 
info: loading plugin "livereload"... OK 
info: loading plugin "highlight"... OK 
info: loading plugin "search"... OK 
info: loading plugin "lunr"... OK 
info: loading plugin "fontsettings"... OK 
info: loading plugin "theme-default"... OK 
info: found 18 pages 
info: found 12 asset files 
info: >> generation finished with success in 6.3s ! 

Starting server ...
Serving book on http://localhost:4000
```
