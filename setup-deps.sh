# Setup script for image-photo-z. Assuming a Debian-like operating system.

# Get latest definitions and install packages
sudo apt-get update
sudo apt-get upgrade python
sudo apt-get -qy install python-dev
sudo apt-get -qy install alien
sudo apt-get -qy install wget
sudo apt-get -qy install python-matplotlib
sudo apt-get -qy install gfortran
sudo apt-get -qy install openmpi-bin openmpi-doc libopenmpi-dev

# Get pip in order to install python packages well.
sudo apt-get -qy install python-pip

# Install necessary python packages using pip
sudo pip install numpy
sudo pip install astropy
sudo pip install healpy
sudo pip install f2py
sudo pip install pyfits
sudo pip install mpi4py
sudo pip install MLZ
sudo pip install scikit-learn

# Install SExtractor
mkdir sextractor
cd sextractor
wget http://www.astromatic.net/download/sextractor/sextractor-2.19.5-1.x86_64.rpm
sudo alien sextractor-2.19.5-1.x86_64.rpm
sudo dpkg -i sextractor_2.19.5-2_amd64.deb
cd ..
rm -rf sextractor/

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
rm -rf montage_temp/

# Install the python wrapper
sudo pip install montage_wrapper
