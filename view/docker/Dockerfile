# Pull base Node image. Be sure that this Node version matches that of the Meteor bundle.
FROM node:8.11.4

# Create and set working directory for the container
WORKDIR /view

# Copy all files in current directory into container's /view directory.
# Since this Dockerfile is intended to be used by the docker-build.sh script,
# this effectively copies the generated Meteor app bundle into the container.
COPY . /view

# Install the Meteor application's packages.
# Note that the cd is temporary here and reverts back to WORKDIR after the
# RUN is complete, not dissimilar to a subshell invocation.
RUN cd /view/programs/server && npm install --unsafe-perm

EXPOSE 80

EXPOSE 8888

CMD ["node", "main.js"]