Image Photo-Z
=============

_Pixel-level estimation of photometric redshifts for astronomical images._

This is a bit out of date and will be updated as soon as possible.

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

####Instructions For Use: Use exactly in the same order as given below.
* **get_images module**: This gets images for a requested object, survey, band and area around the object.  
  * **get_image_lists()** gets image lists using mArchiveList. This creates a folder with the object name to put data for the object there.
  * **parse_image_lists(obj)** extracts URLs for images from the image lists and puts them in a file in the object folder.
  * **get_images(obj)** downloads images from the URLs.
  Note that the first and the third functions in the above list require connection to the internet.
* **image_registration module**: This contains _image-registration.py_ which contains most function definitions.  
  * **register_reproject(dirname)** uses the reproject function in the IPAC Montage toolkit to align images. Dirname is the name of the directory that the images are stored in. Output images are put into the same directory.
  * **reg_check_diff(image, ref, out)** outputs a difference image to check the registration. The _image_ is the input, the _ref_ is the reference image and the _out_ is the output image name.  
  The _main.py_ file here has an application example.

####Miscellaneous Notes:  
All code has been written and tested on Ubuntu 12.04 LTS.  

####Contact:
Alankar Kotwal  
_alankarkotwal13@gmail.com_
