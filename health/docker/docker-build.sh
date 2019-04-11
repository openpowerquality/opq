
# Subdirectory for src files
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir $timestamp

######################
# Build Docker Image #
######################

IMAGE_NAME=healthv2

echo "=> Copying health source files into $timestamp"

cp ../Cargo.toml ./$timestamp/
cp -r ../src ./$timestamp/
cp ./Dockerfile ./$timestamp/

cd $timestamp

echo "=> Building Docker image..."

docker build --tag=${IMAGE_NAME} .

echo "=> Deleting all temporary files..."

cd ..

rm -rf $timestamp

echo "=> Docker build complete!"
echo "=> Use the 'docker image ls' command to check that the '${IMAGE_NAME}' image was successfully generated"
