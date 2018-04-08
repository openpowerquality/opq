# Deploy View

There are two steps to deploying OPQView: building the production bundle on a development machine, then running the bundle on the server.

### Build the production bundle

In general, you will build the production bundle from the master branch of OPQView. 

In your development environment, change directories into the `view/app/` directory, then invoke `meteor npm run build`:

```
$ meteor npm run build

> opqview@ build /Users/philipjohnson/github/openpowerquality/opq/view/app
> meteor build ../deploy --architecture os.linux.x86_64

Node#moveTo was deprecated. Use Container#append.
```

Now the contents of the `view/deploy/` directory will contain two files:

  * app.tar.gz: A 45 MB file containing the production version of the app. 
  * deploy-run.sh:  A script for running the deployment.
  
Finally, commit the master branch of OPQ, which 
 
 
 

