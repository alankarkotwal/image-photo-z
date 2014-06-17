from get_images import *

for i in ['180.5 45.5']:
	get_image_lists(i, 1, 1)
	parse_image_lists(i)
	download_images(i, 1)
