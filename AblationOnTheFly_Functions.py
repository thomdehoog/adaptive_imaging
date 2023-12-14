import sys
import math
from operator import itemgetter
from timeit import default_timer as timer
from datetime import timedelta

def getPixelForAblation(skip):

	def bresenham(x0, y0, x1, y1):
		dx = x1 - x0
		dy = y1 - y0

		xsign = 1 if dx > 0 else -1
		ysign = 1 if dy > 0 else -1

		dx = abs(dx)
		dy = abs(dy)
		if dx > dy:
			xx, xy, yx, yy = xsign, 0, 0, ysign
		else:
			dx, dy = dy, dx
			xx, xy, yx, yy = 0, ysign, xsign, 0
		
		D = 2*dy - dx
		y = 0
		for x in range(dx + 1):
			yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
			if D >= 0:
				y += 1
				D -= 2*dx
			D += 2*dy

	def getPixels_line(skip):
	
		#Get coordinates of the line
		points, xArray, yArray = VV.Window.Regions.Active.CoordinatesToArrays()
		x0 = xArray[0]
		y0 = yArray[0]
		x1 = xArray[1]
		y1 = yArray[1]
	
		bres = list(bresenham(x0,y0,x1,y1))
		x = [item[0] for item in bres]
		y = [item[1] for item in bres]
	
		new_x = []
		new_y = []
		select = skip+1;
		counter = 0;
			
		for i in range(0, len(x)):
			if counter == 0:
				new_x.append(x[i])
				new_y.append(y[i])
				counter = counter + 1
			elif counter == select:
				new_x.append(x[i])
				new_y.append(y[i])
				counter = 0
			else:
				counter = counter + 1

		return new_x, new_y
	
	def getPixels_rectangle(skip):
		
		#Get coordinates of the line
		points, xArray, yArray = VV.Window.Regions.Active.CoordinatesToArrays()
		x0 = xArray[0]
		y0 = yArray[0]
		x1 = xArray[1]
		y1 = yArray[2]
	
		x = range(x0, x1)
		y = range(y0, y1)
				
		new_x = []
		select = skip+1;
		counter = 0;
		for i in range(0, len(x)):
			if counter == 0:
				new_x.append(x[i])
				counter = counter + 1
			elif counter == select:
				new_x.append(x[i])
				counter = 0
			else:
				counter = counter + 1

		new_y = []
		select = skip+1;
		counter = 0;
		for i in range(0, len(y)):
			if counter == 0:
				new_y.append(y[i])
				counter = counter + 1
			elif counter == select:
				new_y.append(y[i])
				counter = 0
			else:
				counter = counter + 1

		final_x = []
		final_y = []
		for i in range(0,len(new_y)):
			final_x.append(new_x)
			final_y.append([new_y[i]] * len(new_x))

		#reverse every odd entry in the x list for speed
		for i in range(len(final_x)):
			if(i % 2 == 1):				
				final_x[i] = list(reversed(final_x[i]))
				
		final_x = [item for sublist in final_x for item in sublist]
		final_y = [item for sublist in final_y for item in sublist] 	

		return final_x, final_y
	
	def getPixels_circle():
		#Get coordinates and radius of the circle
		points, xArray, yArray = VV.Window.Regions.Active.CoordinatesToArrays()
		x0 = min(xArray)
		y0 = min(yArray)
		x1 = max(xArray)
		y1 = max(yArray)
		radius = int(round((x1 - x0)/2))
		x_center = int(x1-radius)
		y_center = int(y1-radius)		
		
		def mirror_points_8(x, y):
			return [( x,  y),
    		        ( y,  x),
    		        (-x,  y),
    		        (-y,  x),
    		        ( x, -y),
    		        ( y, -x),
    		        (-x, -y),
    		        (-y, -x)]

		def bresenham_circle(r):
			points = []
			x = 0
			y = -r
			F_M = 1 - r
			d_e = 3
			d_ne = -(r << 1) + 5
			points.extend(mirror_points_8(x, y))
			while x < -y:
				if F_M <= 0:
					F_M += d_e
				else:
					F_M += d_ne
					d_ne += 2
					y += 1
				d_e += 2
				d_ne += 2
				x += 1
				points.extend(mirror_points_8(x, y))
			return points
	
		#reformat
		circle_xy = bresenham_circle(radius)
		x_null = [item[0] for item in circle_xy]
		y_null = [item[1] for item in circle_xy]

		#center circle properly
		x_place = [x+x_center for x in x_null]
		y_place = [x+y_center for x in y_null]
		
		y_sorted = sorted(set(y_place))
		
		#for i in range(y_sorted)
		circle_x = []
		circle_y = []
		
		for i in range(len(y_sorted)):
			indices  = [j for j in range(len(y_place)) if y_place[j] == y_sorted[i] ]
			temp = itemgetter(*indices)(x_place)
			
			temp_max = max(temp)
			temp_min = min(temp)
			temp_range_x = range(temp_min, temp_max)
			temp_range_y = [y_sorted[i]] * len(temp_range_x) 
			circle_x.append(temp_range_x)
			circle_y.append(temp_range_y)
					
		print(circle_y[1])
		
		index_y = []
		select = skip+1;
		counter = 0;
		for i in range(0, len(circle_y)):
			if counter == 0:
				index_y.append(i)
				counter = counter + 1
			elif counter == select:
				index_y.append(i)
				counter = 0
			else:
				counter = counter + 1

		circle_x_skip = []
		circle_y_skip = []
		#for loop over the xes
		for i in range(len(index_y)):
		
			temp_x = []
			select = skip+1
			counter = 0
			for j in range(0, len(circle_x[index_y[i]]) ):
				if counter == 0:
					temp_x.append(circle_x[index_y[i]][j])
					counter = counter + 1
				elif counter == select:
					temp_x.append(circle_x[index_y[i]][j])
					counter = 0
				else:
					counter = counter + 1
				
			circle_x_skip.append(temp_x)
			temp_y = [circle_y[index_y[i]][1]] * len(temp_x)
			circle_y_skip.append(temp_y)
		
		print(circle_x_skip)
		print(circle_y_skip)
		
		#reverse every odd entry in the x list for speed
		for i in range(len(circle_x_skip)):
			if(i % 2 == 1):				
				circle_x_skip[i] = list(reversed(circle_x_skip[i]))
		
		final_x = [item for sublist in circle_x_skip for item in sublist]
		final_y = [item for sublist in circle_y_skip for item in sublist]
	
		return final_x, final_y	
		
	def getPixels_polygon():
		print("Polygon is not build yet")
		
	def getPixels_polyline():
		print("Polyline is not build yet")
	
	# VisiView Macro
	VV.Window.Selected.Handle = VV.Window.Active.Handle
	VV.Window.Regions.Active.IsValid = True
		
	#Get pixels coordinate corresponding to the line
	if(VV.Window.Regions.Active.Type == 'Line'):
		poi = getPixels_line(skip)
	elif(VV.Window.Regions.Active.Type == 'Rectangle'):
		poi = getPixels_rectangle(skip)
	elif(VV.Window.Regions.Active.Type == 'Circle'):
		poi = getPixels_circle()
	elif(VV.Window.Regions.Active.Type == 'Polygon'):
		poi = getPixels_polygon()
	elif(VV.Window.Regions.Active.Type == 'PolyLine'):
		poi = getPixels_polyline()
		
	return poi
