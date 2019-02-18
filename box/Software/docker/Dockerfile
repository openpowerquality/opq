FROM piersfinlayson/build

RUN sudo apt-get update
RUN sudo apt-get upgrade -y
RUN sudo apt-get install -y g++-arm-linux-gnueabihf g++-arm-linux-gnueabi


RUN wget https://github.com/zeromq/libzmq/archive/v4.3.1.tar.gz
RUN tar xf v4.3.1.tar.gz
RUN cd libzmq-4.3.1 && ./autogen.sh && ./configure --host=arm-none-linux-gnueabi CC=arm-linux-gnueabi-gcc CXX=arm-linux-gnueabi-g++ && make && sudo make install

