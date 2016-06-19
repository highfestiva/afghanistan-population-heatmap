#!/usr/bin/env python3

'''Hard-coded hack to generate JSON population coordinate files from input image.
   Could be refactored to handle a more generic case.'''


from glob import glob
from os import remove
from os.path import exists
from PIL import Image
from crd import *


def map_adjust(p):
	''' to real-world geographic coordinates.'''
	return (p-country_center)*map_adjust_scale + country_center + map_adjust_offset

def map_inverse_adjust(p):
	'''Inverts map_adjust(), i.e. moves from geographic map space to generator map space.'''
	return (p-map_adjust_offset-country_center) / map_adjust_scale + country_center

def clamp_range(maxend, start, end, step):
	return range(max(min(maxend,start)-step,0), max(min(maxend,end)-step,0), step)

def get_pixel_color(x, y, size):
	if size <= 1:	# Optimization for one pixel resolution.
		return pixels[x,y]
	# Average color over several pixels.
	r,g,b = 0,0,0
	for yy in range(y,y+size):
		for xx in range(x,x+size):
			u,v,w = pixels[xx,yy]
			r += u
			g += v
			b += w
	irr = 1 / (size*size)
	return r*irr,g*irr,b*irr

def color2weight(col):
	'''Ignore grayscale colors, as that constitutes the background, text and lines.
	   Yellow means low weight, red means higher weight and highest is dark red.'''
	i = 1/255
	r,g,b = col[0]*i,col[1]*i,col[2]*i
	weight = (g-b) + (r-g)*2 + max(r-b-g,0)*(1-r)*5	# Yellow > red > dark red.
	return weight/3

def create_heat_patch(zoom_level, map_center, map_scale, img_center, img_scale, patch_overlap):
	'''zoom_level is same as Google Maps' definition. We only create patches for even zoom levels.
	   patch_overlap should be large enough that we don't show blank parts as we pan close to the
	   border of the patch. Is recursive and will write patch files to disk.'''
	if zoom_level > 12:	# Don't recurse infinitely.
		return
	fname = '%g_%g_%g_popdata.json' % (zoom_level, map_center.lat(), map_center.lng())
	if exists(fname):	# Don't redo patches.
		return

	json = []
	img_size = img_width if img_width>img_height else img_height
	# Adjust X and Y pixels so map_adjust() won't put the points outside of the patch.
	pixel_adjust = (map_inverse_adjust(map_center) - map_center) * (img_scale*img_size/map_scale)
	img_adjusted_center = img_center + pixel_adjust
	# Reduce required weight somewhat as zoom levels increase.
	population_weight_limit = 0.45 - (zoom_level-6)/120
	image_patch_size = int(img_size*img_scale*patch_overlap)
	xo,yo = int(img_adjusted_center.x-image_patch_size/2),int(img_adjusted_center.y-image_patch_size/2)
	# Scale factor from image pixels to map (optimization for inner-most loop).
	img2map_scale = map_scale / (img_size*img_scale)
	# Increase pixel-to-map resolution in higher zoom.
	pixel_resolution = int(23/zoom_level)
	# Loop through the image and store relevant heat points.
	for y in clamp_range(img_height, yo, yo+image_patch_size, pixel_resolution):
		for x in clamp_range(img_width, xo, xo+image_patch_size, pixel_resolution):
			col = get_pixel_color(x, y, pixel_resolution)
			population_weight = color2weight(col)	# Convert pixel color to weight.
			if population_weight > population_weight_limit:
				img_rel_crd = crd(x,y) - img_center
				map_crd = img_rel_crd * img2map_scale + map_center
				p = map_adjust(map_crd)
				json += ['[%3.3f,%3.3f,%3.3f]' % (p.lat(),p.lng(),10**population_weight)]
	if json:
		json = '[' + ','.join(json) + ']'
		print('%s: %i bytes.' % (fname, len(json)))
		open(fname, 'w').write(json)
	# Create sub-patches for each quadrant.
	m_quad_f,i_quad_f = map_scale/4,img_size*img_scale/4
	create_heat_patch(zoom_level+2, map_center+crd(-m_quad_f,-m_quad_f), map_scale/2, img_center+crd(-i_quad_f,-i_quad_f), img_scale/2, patch_overlap)
	create_heat_patch(zoom_level+2, map_center+crd(+m_quad_f,-m_quad_f), map_scale/2, img_center+crd(+i_quad_f,-i_quad_f), img_scale/2, patch_overlap)
	create_heat_patch(zoom_level+2, map_center+crd(-m_quad_f,+m_quad_f), map_scale/2, img_center+crd(-i_quad_f,+i_quad_f), img_scale/2, patch_overlap)
	create_heat_patch(zoom_level+2, map_center+crd(+m_quad_f,+m_quad_f), map_scale/2, img_center+crd(+i_quad_f,+i_quad_f), img_scale/2, patch_overlap)


# Drop all previously generated .json patch files.
[remove(f) for f in glob('*.json')]

# Setup data and load image.
country_center = latlng(32,64)	# ~Afghanistan.
img = Image.open('af_population.png')
pixels = img.load()
img_width,img_height = img.size
map_center,map_scale = country_center,32
img_center,img_scale = crd(img_width/2,img_height/2),1
patch_overlap = 3	# Some overlapping is required, or you'll see gaps when panning the map.
zoom_level = 6
# Hard-coded transformation parameters of arbitrarily chosen center and scale, including
# compensation for center of the image not being exactly center of the country.
map_adjust_scale = 0.46173564
map_adjust_offset = latlng(1.9564,3.546)
# Generate the heat patches recursively. Will create files on disk.
create_heat_patch(zoom_level, map_center, map_scale, img_center, img_scale, patch_overlap)
