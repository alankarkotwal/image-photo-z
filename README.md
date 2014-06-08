Image Photo-Z
=============

_Pixel-level estimation of photometric redshifts for astronomical images._


####Requirements:
* A computer running a Debian-like operating system, preferably Ubuntu 12.04 or higher.
* Python support and administrator access
* Software dependencies:
  * Python 2.7 or higher (installed with the python-dev package)
  * Numpy
  * Astropy
  * libcfitsio
  * Montage Image Mosaic Software for Astronomers
  * montage_wrapper package for Python

####Install Instructions:  
The setup-* scripts take care of the installation of the package.  
Install dependencies first by running the setup-deps script this way:

    cd <package path> 
    sudo chmod +x setup-deps.sh
    ./setup-deps.sh

Install the package by running

    sudo chmod +x setup.sh
    ./setup.sh

####Instructions For Use:  
* **image_registration module**: This contains _image-registration.py_ which contains most function definitions.  
  * **register_reproject(dirname)** uses the reproject function in the IPAC Montage toolkit to align images. Dirname is the name of the directory that the images are stored in. Output images are put into the same directory.
  * **reg_check_diff(image, ref, out)** outputs a difference image to check the registration. The _image_ is the input, the _ref_ is the reference image and the _out_ is the output image name.  
  The _main.py_ file here has an application example.

####Miscellaneous Notes:  
All code has been written and tested on Ubuntu 12.04 LTS.  

####Contact:
Alankar Kotwal  
_alankarkotwal13@gmail.com_
