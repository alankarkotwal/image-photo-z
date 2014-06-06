Image Photo-Z
=============

_Pixel-level estimation of photometric redshifts for astronomical images._


####Requirements:
* A computer running a Debian-like operating system, preferably Ubuntu 12.04 or higher.
* Python support and administrator access


####Install Instructions:  
The setup-* packages take care of the installation of the package. Please note that this is a work in progress.  
Install dependencies first by running the setup-deps script this way:

    cd <package path> 
    sudo chmod +x setup-deps.sh
    ./setup-deps.sh

Install the package by running

    sudo chmod +x setup.sh
    ./setup.sh


####Instructions For Use:  
* **image_registration module**: This contains _image-registration.py_ which contains most function definitions.  
  The general structure of a registration function is **register_<method-name>(image, ref, out).**  
  The _image_ is the input, the _ref_ is the reference image and the _out_ is the output image name.
  * **register_reproject** uses the reproject function in the IPAC Montage toolkit to align images.
  * **register_wcs** uses astrometric information in FITS headers to align images.
  * **register_sex** plans to register using SExtractor and catalog information.
  * **reg_check_diff** outputs a difference image to check the registration.
  The _main.py_ file here has an application example.

####Miscellaneous Notes:  
All code has been written and tested on Ubuntu 12.04 LTS.

####Contact:
Alankar Kotwal  
_alankarkotwal13@gmail.com_
