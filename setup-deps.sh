# Setup script for image-photo-z. Assuming a Debian-like operating system.

# Get root permissions
sudo sudo > /dev/null

# Get latest definitions
sudo apt-get update
sudo apt-get upgrade python

# Get pip in order to install python packages well.
sudo apt-get -qy install python-pip

# Install necessary python packages using pip
sudo pip install python-numpy
sudo pip install python-astropy
sudo pip install python-numpy
