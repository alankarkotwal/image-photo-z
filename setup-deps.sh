# Setup script for image-photo-z. Assuming a Debian-like operating system.

# Get root permissions
sudo sudo > /dev/null

# Get latest definitions
sudo apt-get update
sudo apt-get upgrade python
sudo apt-get install python-dev

# Get pip in order to install python packages well.
sudo apt-get -qy install python-pip

# Install necessary python packages using pip
sudo pip install numpy
sudo pip install astropy
sudo pip install pysex

# Install libcfitsio
sudo apt-get install libcfitsio*

# Install Montage
mkdir montage_temp
cd montage_temp
wget http://montage.ipac.caltech.edu/download/Montage_v3.3.tar.gz
gunzip Montage_v3.3.tar.gz
tar -xvf Montage_v3.3.tar
cd Montage_v3.3
make
sudo cp bin/* /bin/
cd ../../
rm -rf montage_temp

# Install the python wrapper
sudo pip install montage_wrapper
