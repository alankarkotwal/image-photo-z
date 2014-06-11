from get_images import *

for i in ['NGC4']:
	get_image_lists(i, 1, 1, survey='2mass', bands=['j', 'h', 'k'])
	get_image_lists(i, 1, 1)
	parse_image_lists(i, bands=['u','g','r','i','z', 'j', 'h', 'k'])
	download_images(i, 1, bands=['u','g','r','i','z', 'j', 'h', 'k'])
