#!/usr/bin/env python3

'''Generates some .json heatpoint files from the input image.'''

from glob import glob
from os import remove
from os.path import exists
from PIL import Image
from crd import *

afghanistan = latlng(32,64)
img = Image.open('af_population.png')
pixels = img.load()
img_width,img_height = img.size

def map_adjust(p):
	'Hard-coded retrofit of the approximate coord to actual coord.'
	return (p-afghanistan)*0.2915228*0.997 + afghanistan + latlng(1.9464+0.009,3.607-0.052)

def clamp_range(size, start, end, step):
	return range(max(min(size,start)-step,0), max(min(size,end)-step,0), step)

def get_col(x, y, size):
	if size <= 1:
		return pixels[x,y]
	r,g,b = 0,0,0
	for yy in range(y,y+size):
		for xx in range(x,x+size):
			u,v,w = pixels[xx,yy]
			r += u
			g += v
			b += w
	irr = 1 / (size*size)
	return r*irr,g*irr,b*irr

def col2weight(col):
	i = 1/255
	r,g,b = col[0]*i,col[1]*i,col[2]*i
	weight = (g-b) + (r-g)*2 + max(r-b-g,0)*(1-r)*5	# Yellow > red > dark red.
	return weight/3

# print(col2weight((136,1,3)))
# print(col2weight((0,0,0)))
# import sys
# sys.exit()

def create_level(zoom_level, map_center, map_scale, img_center, img_scale, patch_overlap):
	if zoom_level > 8:
		return
	fname = '%g_%g_%g_popdata.json' % (zoom_level, map_center.lat(), map_center.lng())
	if not exists(fname):
		print(fname)
		json = []
		weight_limit = 0.35 - (zoom_level-6)/100
		pixel_scale = int(img_height*img_scale*patch_overlap)
		xo,yo = int(img_center.x-pixel_scale/2),int(img_center.y-pixel_scale/2)
		pixel_res = int(24/zoom_level)
		print('img X range:', xo, xo+pixel_scale)
		print('img Y range:', yo, yo+pixel_scale)
		for y in clamp_range(img_height, yo, yo+pixel_scale, pixel_res):
			for x in clamp_range(img_width, xo, xo+pixel_scale, pixel_res):
				col = get_col(x, y, pixel_res)
				weight = col2weight(col)
				if weight > weight_limit:
					rel_crd = (crd(x,y) - img_center)
					map_rel_crd = rel_crd * (map_scale/(img_height*img_scale))
					p = map_adjust(map_rel_crd + map_center)
					json += ['[%3.3f,%3.3f,%3.3f]' % (p.lat(),p.lng(),10**weight)]
					# print('json=', json)
					# print('p=', p.x, p.y)
					# print('y=', y)
					# print('x=', x)
					# print('rel.y=', rel_crd.y)
					# print('rel.x=', rel_crd.x)
					# print('map_scale=', map_scale)
					# import sys
					# sys.exit()
		if json:
			print(' - writing')
			f = open(fname, 'w')
			print('[' + ','.join(json) + ']', file=f)
		else:
			print(' - skipping - no content')
		print('   |', xo, yo, pixel_scale, img_center.x, img_center.y, img_scale)
	m_quad_f,i_quad_f = map_scale/4,img_height*img_scale/4
	create_level(zoom_level+2, map_center+crd(-m_quad_f,-m_quad_f), map_scale/2, img_center+crd(-i_quad_f,-i_quad_f), img_scale/2, patch_overlap)
	create_level(zoom_level+2, map_center+crd(+m_quad_f,-m_quad_f), map_scale/2, img_center+crd(+i_quad_f,-i_quad_f), img_scale/2, patch_overlap)
	create_level(zoom_level+2, map_center+crd(-m_quad_f,+m_quad_f), map_scale/2, img_center+crd(-i_quad_f,+i_quad_f), img_scale/2, patch_overlap)
	create_level(zoom_level+2, map_center+crd(+m_quad_f,+m_quad_f), map_scale/2, img_center+crd(+i_quad_f,+i_quad_f), img_scale/2, patch_overlap)


[remove(f) for f in glob('*.json')]
map_center,map_scale = afghanistan,32
img_center,img_scale = crd(img_width/2,img_height/2),1
patch_overlap = 3
zoom_level = 6
create_level(zoom_level, map_center, map_scale, img_center, img_scale, patch_overlap)
