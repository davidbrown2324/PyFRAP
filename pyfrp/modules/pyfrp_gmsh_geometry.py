#=====================================================================================================================================
#Copyright
#=====================================================================================================================================

#Copyright (C) 2014 Alexander Blaessle, Patrick Mueller and the Friedrich Miescher Laboratory of the Max Planck Society
#This software is distributed under the terms of the GNU General Public License.

#This file is part of PyFRAP.

#PyFRAP is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#===========================================================================================================================================================================
#Module Description
#===========================================================================================================================================================================

"""PyFRAP module for creating/extracting gmsh geometries for PyFRAP toolbox. Module mainly has the following classes:

	* A ``domain`` class, acting as a canvas.
	* A ``vertex`` class, substituting gmsh's *Point*.
	* A ``edge`` class, parenting all different kind of edges.
	* A ``line`` class, substituting gmsh's *Line*.
	* A ``arc`` class, substituting gmsh's *Circle*.
	
This module together with pyfrp.pyfrp_gmsh_IO_module and pyfrp.pyfrp_gmsh_module works partially as a python gmsh wrapper, however is incomplete.
If you want to know more about gmsh, go to http://gmsh.info/doc/texinfo/gmsh.html .
"""
#===========================================================================================================================================================================
#Importing necessary modules
#===========================================================================================================================================================================

#Numpy/Scipy
import numpy as np

#String
import string

#PyFRAP modules
import pyfrp_plot_module
from pyfrp_term_module import *
import pyfrp_misc_module
import pyfrp_gmsh_IO_module
import pyfrp_idx_module

#===========================================================================================================================================================================
#Module Functions
#===========================================================================================================================================================================

def getAngle(vec1,vec2):
	
		"""Returns angle between two vectors in radians.
		
		Args:
			vec1 (numpy.ndarray): Vector 1.
			vec2 (numpy.ndarray): Vector 2.
		
		Returns: 
			float: Angle.
		
		"""
		
		a=np.arccos(np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2)))
		
		if a<0:
			return getAngle(vec2,vec1)
		return a

def flipCoordinate(x,destAxis,origAxis='x',debug=False):
	
		"""Transforms coodinate from one axis to another by
		rolling the coordinates, e.g. clockwise turning the 
		point.
		
		``destAxis`` and ``origAxis`` are given as one of 
		``x,y,z``. 
		
		Args:
			x (numpy.ndarray): Coordinate to turn.
			destAxis (str): Destination axis.
			
		Keyword Args:	
			origAxis (str): Original axis.
			debug (bool): Print debugging output.
		
		Returns:
			numpy.ndarray: Transformed coordinate.
		
		"""
		
			
		# Calculate differences between axis
		axisDiff=abs(string.lowercase.index(destAxis)-string.lowercase.index(origAxis))
		
		# Roll
		xnew=np.roll(x,axisDiff)
		
		# Print debugging messages
		if debug:
			print "Transforming coordinate " , x, " from axis ", origAxis, " to axis ", destAxis , "."
			print "axisDiff = ", axisDiff
			print "xnew = ", xnew
		
		return xnew 
		
#===========================================================================================================================================================================
#Class definitions
#===========================================================================================================================================================================
	
class domain:
	
	"""Domain class storing embryo geometry entities.
	
	Args:
		edges (list): List of edges.
		vertices (list): List of vertices.
		arcs (list): List of arcs.
		lines (list): List of lines.
		lineLoops (list): List of lineLoops.
		surfaceLoops (list): List of surfaceLoops.
		ruledSurfaces (list): List of ruledSurfaces.
		volumes (list): List of volumes.
		annXOffset (float): Offset of annotations in x-direction.
		annYOffset (float): Offset of annotations in y-direction.
		annZOffset (float): Offset of annotations in z-direction.
			
	"""
	
	def __init__(self):
		
		self.edges=[]
		self.vertices=[]
		self.arcs=[]
		self.lines=[]
		self.lineLoops=[]
		self.ruledSurfaces=[]
		self.surfaceLoops=[]
		self.volumes=[]
		
		self.annXOffset=3.
		self.annYOffset=3.
		self.annZOffset=3.
		
		
	def addVertex(self,x,Id=None,volSize=None):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.vertex` instance
		at point ``x`` and appends it to ``vertices`` list.
		
		.. note:: ``volSize`` does not have any effect on the geometry itself but is simply 
		   stored in the vertex object for further usage.
		
		Args:
			x (numpy.ndarray): Coordinate of vertex.
			
		Keyword Args:
			Id (int): ID of vertex.
			volSize (float): Element size at vertex.
		
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.vertex: New vertex instance.
		
		"""
		
		newId=self.getNewId(self.vertices,Id)
		
		v=vertex(self,x,newId,volSize=volSize)
		self.vertices.append(v)	
		
		return v
	
	def addLine(self,v1,v2,Id=None):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.line` instance
		at point ``x`` and appends it to ``edges`` and ``lines`` list.
		
		Args:
			v1 (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Start vertex.
			v2 (pyfrp.modules.pyfrp_gmsh_geometry.vertex): End vertex.
			
		Keyword Args:
			Id (int): ID of line.
			
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.line: New line instance.
		
		"""
		
		newId=self.getNewId(self.edges,Id)
		
		e=line(self,v1,v2,newId)
		self.lines.append(e)
		self.edges.append(e)
		
		return e
	
	def addArc(self,vstart,vcenter,vend,Id=None):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.arc` instance
		at point ``x`` and appends it to ``edges`` and ``arcs`` list.
		
		Args:
			vstart (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Start vertex.
			vcenter (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Center vertex.
			vend (pyfrp.modules.pyfrp_gmsh_geometry.vertex): End vertex.
			
		Keyword Args:
			Id (int): ID of arc.
			
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.arc: New line instance.
		
		"""
		
		
		newId=self.getNewId(self.edges,Id)
			
		a=arc(self,vstart,vcenter,vend,newId)
		self.arcs.append(a)
		self.edges.append(a)
		
		return a
	
	def addCircleByParameters(self,center,radius,z,volSize,plane="z"):
		
		"""Adds circle to domain by given center and radius.
		
		Will create 5 new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.vertex` objects 
		``[vcenter,v1,v2,v3,v4]`` and four new `pyfrp.modules.pyfrp_gmsh_geometry.arc` objects
		[a1,a2,a3,a4] and builds circle.
		
		Circle  will be at ``z=z`` and vertices will have mesh size ``volSize``.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		>>> d.addCircleByParameters([256,256],100,50,30.)
		>>> d.addCircleByParameters([256,256],100,50,30.,plane="x")
		>>> d.addCircleByParameters([256,256],100,50,30.,plane="y")
		>>> d.draw()
		
		will generate:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addCircleByParameters.png
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		Args:
			center (numpy.ndarray): Center of circle.
			radius (float): Radius of the circle.
			z (float): Height at which circle is placed.
			volSize (float): Mesh size of vertices.
		
		Keyword Args:
			plane (str): Plane in which circle is placed.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* arcs (list): List of arcs.
		
		"""
		
		# Define coordinates
		xcenter=flipCoordinate([center[0],center[1],z],plane,origAxis="z")
		x1=flipCoordinate([center[0]+radius,center[1],z],plane,origAxis="z")
		x2=flipCoordinate([center[0],center[1]+radius,z],plane,origAxis="z")
		x3=flipCoordinate([center[0]-radius,center[1],z],plane,origAxis="z")
		x4=flipCoordinate([center[0],center[1]-radius,z],plane,origAxis="z")
		
		# Add vertices
		vcenter=self.addVertex(xcenter,volSize=volSize)
		v1=self.addVertex(x1,volSize=volSize)
		v2=self.addVertex(x2,volSize=volSize)
		v3=self.addVertex(x3,volSize=volSize)
		v4=self.addVertex(x4,volSize=volSize)
		
		# Add Arcs
		a1=self.addArc(v1,vcenter,v2)
		a2=self.addArc(v2,vcenter,v3)
		a3=self.addArc(v3,vcenter,v4)
		a4=self.addArc(v4,vcenter,v1)
		
		return [vcenter,v1,v2,v3,v4],[a1,a2,a3,a4]
	
	def addPolygonByParameters(self,coords,volSize,z=0.,plane="z"):
		
		"""Adds polygon to domain by given vertex coordinates.
		
		Will create a list of new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.vertex` objects 
		and a list of new `pyfrp.modules.pyfrp_gmsh_geometry.line` objects
		connecting the vertices.
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		.. note:: Vertices can be given either as a 
		
			* list of coordinate triples ``[[x1,y1,z1],[x2,y2,z2],...]``.
			* list of x-y-coordinates and a given z-coordinate ``[[x1,y1,z],[x2,y2,z],...]``.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		>>> d.addPolygonByParameters([[100,100,100],[200,200,100],[200,100,100]],30.)
		>>> d.addPolygonByParameters([[100,100,100],[200,200,100],[200,100,100]],30.,plane="x")
		>>> d.addPolygonByParameters([[100,100,100],[200,200,100],[200,100,100]],30.,plane="y")
		>>> d.draw()
		
		will generate:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addPolygonByParameters.png
		
		
		.. note:: Vertices are created in the order of the coordinates and connected in the same order.
		

		Args:
			coords (list): List of coordinates.
			volSize (float): Mesh size of vertices.
			
		Keyword Args:
			plane (str): Plane in which polygon is placed.
			z (float): Height at which polygon is placed.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* lines (list): List of connecting lines.
		
		"""
		
		# Define coordinates
		xs=[]
		for c in coords:
			if len(c)==3:
				xs.append(flipCoordinate([c[0],c[1],c[2]],plane,origAxis="z"))
			else:
				xs.append(flipCoordinate([c[0],c[1],z],plane,origAxis="z"))
		
		# Add vertices
		vertices=[]
		for x in xs:
			vertices.append(self.addVertex(x,volSize=volSize))
		
		# Add Arcs
		lines=[]
		for i in range(len(vertices)):
			lines.append(self.addLine(vertices[i],vertices[pyfrp_misc_module.modIdx(i+1,vertices)]))
			
		return vertices,lines
	
	def addRectangleByParameters(self,offset,sidelengthX,sidelengthY,z,volSize,plane="z"):
		
		"""Adds rectangle to domain by given offset and sidelengths.
		
		Will create a list of four :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.vertex` objects 
		and a list of four `pyfrp.modules.pyfrp_gmsh_geometry.line` objects
		connecting the vertices.
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		.. note:: The ``offset`` is defined as the bottom left corner.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		>>> d.addRectangleByParameters([256,256],100,200,50,30.)
		>>> d.addRectangleByParameters([256,256],100,200,50,30.,plane="x")
		>>> d.addRectangleByParameters([256,256],100,200,50,30.,plane="y")
		>>> d.draw()
		
		will generate:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addRectangleByParameters.png
		
		Args:
			offset (numpy.ndarray): Offset of rectangle.
			sidelengthX (float): Sidelength in x-direction.
			sidelengthY (float): Sidelength in y-direction.
			z (float): Height at which rectangle is placed.
			volSize (float): Mesh size of vertices.
			
		Keyword Args:
			plane (str): Plane in which rectangle is placed.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* lines (list): List of connecting lines.
		
		"""
		
		coords=[[offset[0],offset[1],z],[offset[0]+sidelengthX,offset[1],z],
		[offset[0]+sidelengthX,offset[1]+sidelengthY,z],[offset[0],offset[1]+sidelengthY,z]]
		
		return self.addPolygonByParameters(coords,volSize,plane=plane)
	
	def addSquareByParameters(self,offset,sidelength,z,volSize,plane="z"):
		
		"""Adds square to domain by given offset and sidelength.
		
		Will create a list of four :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.vertex` objects 
		and a list of four `pyfrp.modules.pyfrp_gmsh_geometry.line` objects
		connecting the vertices.
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		.. note:: The ``offset`` is defined as the bottom left corner.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		>>> d.addSquareByParameters([256,256],100,50,30.)
		>>> d.addSquareByParameters([256,256],100,50,30.,plane="x")
		>>> d.addSquareByParameters([256,256],100,50,30.,plane="y")
		>>> d.draw()
		
		will generate:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addSquareByParameters.png
		
		Args:
			offset (numpy.ndarray): Offset of square.
			sidelength (float): Sidelength of square.
			
			z (float): Height at which square is placed.
			volSize (float): Mesh size of vertices.
			
		Keyword Args:
			plane (str): Plane in which square is placed.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* lines (list): List of connecting lines.
		
		"""
		
		return self.addRectangleByParameters(offset,sidelength,sidelength,z,volSize,plane=plane)
	
	def addPrismByParameters(self,coords,volSize,height=1.,z=0.,plane="z",genLoops=True,genSurfaces=True,genVol=True):
		
		r"""Adds prism to domain by given vertex coordinates.
		
		Will create:
		
			* 2 new polygons, see :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.domain.addPolygonByParameters`.
			* n :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.line` objects connecting the two polyogns.
		
		If selected, will create:
			
			* n+2 :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.lineLoop` objects around the 6 surfaces.
			* n+2 corresponding :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.ruledSurface` objects.
			* 1 :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop`.
			* 1 corresponding :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.volume`.
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		.. note:: Vertices can be given either as a 
		
			* list of coordinate triples ``[[x1,y1,z1],[x2,y2,z2],...]``. Then the list of vertices needs to be of length :math:`2n`, where
			  where :math:`n` is the number of corners of the top and lower polygon. Otherwise :py:func:`addPrismByParameters` will crash.
			* list of x-y-coordinates, a given z-coordinate and height. This will place the vertices at ``[[x1,y1,z],[x2,y2,z],...]`` and 
			  ``[[x1,y1,z+height],[x2,y2,z+height],...]``.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		>>> d.addPrismByParameters([[256,256],[200,220],[200,200],[210,210],[220,200]],30.,z=50.,height=40.,plane="z",genLoops=True,genSurfaces=True,genVol=True)
		>>> d.draw()
		
		will generate:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addPrismByParameters.png
		
		.. note:: Vertices are created in the order of the coordinates and connected in the same order.
		
		Args:
			coords (list): List of coordinates.
			volSize (float): Mesh size of vertices.
			
		Keyword Args:
			plane (str): Plane in which prism is placed.
			z (float): Height at which first polygon is placed.
			height (float): Height of prism.
			genLoops (bool): Generate line loops.
			genSurfaces (bool): Generate surfaces.
			genVol (bool): Generate surface loop and corresponding volume.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* lines (list): List of lines.
				* loops (list): List of loops.
				* surfaces (list): List of surfaces.
				* surfaceLoop (pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop): Generated surface loop.
				* vol (pyfrp.modules.pyfrp_gmsh_geometry.volume): Generated volume.
		
		"""
		
		# Create upper and lower polygons
		if len(coords[0])==3:
			if np.mod(len(coords),2)!=0:
				printError("addPrismByParameters: You gave a list of 3-dimensional vertex coordinates. However,the number of coordinates is odd, will not be able to continue.")
				return
				
			vertices,lines = self.addPolygonByParameters(coords,volSize,z=0.,plane="z")
			vertices1=vertices[:len(vertices)/2]
			vertices2=vertices[len(vertices)/2:]
			lines1=lines[:len(lines)/2]
			lines2=lines[len(lines)/2:]
				
		else:	
			vertices1,lines1 = self.addPolygonByParameters(coords,volSize,z=z,plane="z")
			vertices2,lines2 = self.addPolygonByParameters(coords,volSize,z=z+height,plane="z")
			
			
		# Connect them with lines
		lines3=[]
		for i in range(len(vertices1)):
			lines3.append(self.addLine(vertices1[i],vertices2[i]))
		
		# Add loops
		loops=[]
		if genLoops:
			
			# Loops of upper and lower polygon
			loops.append(self.addLineLoop(edgeIDs=pyfrp_misc_module.objAttrToList(lines1,"Id")))
			loops.append(self.addLineLoop(edgeIDs=pyfrp_misc_module.objAttrToList(lines2,"Id")))
			
			# Loops of side faces
			for i in range(len(lines1)):
				loops.append(self.addLineLoop(edgeIDs=[-lines1[i].Id,lines3[i].Id,lines2[i].Id,-lines3[pyfrp_misc_module.modIdx(i+1,lines1)].Id]))
				
		# Add surfaces
		surfaces=[]
		if genSurfaces:
			for loop in loops:
				surfaces.append(self.addRuledSurface(lineLoopID=loop.Id))
				
		# Generate surface loop and volume
		if genVol:
			surfaceLoop=self.addSurfaceLoop(surfaceIDs=pyfrp_misc_module.objAttrToList(self.ruledSurfaces,"Id"))
			vol=self.addVolume(surfaceLoopID=surfaceLoop.Id)
		else:
			surfaceLoop=None
			vol=None		
		
		return [vertices1,vertices2],[lines1,lines2,lines3],loops,surfaces,surfaceLoop,vol
	
	def addCuboidByParameters(self,offset,sidelengthX,sidelengthY,height,volSize,plane="z",genLoops=True,genSurfaces=True,genVol=True):
		
		"""Adds Cuboid to domain by given offset, sidelengths in x- and y-direction and height.
		
		Will define vertices and then call :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.domain.addPrismByParameters.
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		
		>>> d.draw()
		
		will generate:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addCuboidByParameters.png
		
		Args:
			offset (numpy.ndarray): Offset of cuboid.
			sidelengthX (float): Sidelength in x-direction.
			sidelengthY (float): Sidelength in y-direction.
			height (float): Height of cuboid.
			volSize (float): Mesh size of vertices.
			
		Keyword Args:
			plane (str): Plane in which prism is placed.
			genLoops (bool): Generate line loops.
			genSurfaces (bool): Generate surfaces.
			genVol (bool): Generate surface loop and corresponding volume.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* lines (list): List of lines.
				* loops (list): List of loops.
				* surfaces (list): List of surfaces.
				* surfaceLoop (pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop): Generated surface loop.
				* vol (pyfrp.modules.pyfrp_gmsh_geometry.volume): Generated volume.
		
		"""
		
		# Define coordinates
		coords=[[offset[0],offset[1]],[offset[0]+sidelengthX,offset[1]],
		[offset[0]+sidelengthX,offset[1]+sidelengthY],[offset[0],offset[1]+sidelengthY]]
		
		return self.addPrismByParameters(coords,volSize,height=height,z=offset[2],plane="z",genLoops=genLoops,genSurfaces=genSurfaces,genVol=genVol)
	
	
	
	def addCylinderByParameters(self,center,radius,z,height,volSize,plane="z",genLoops=True,genSurfaces=True,genVol=True):
		
		"""Adds cylinder to domain by given center and radius and height.
		
		Will create.
		
			* 2 new circles at ``z=z`` and ``z=z+height``, see :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.domain.addCircleByParameters`.
			* 4 :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.line` objects connecting the two circles.
		
		If selected, will create:
			
			* 6 :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.lineLoop` objects around the 6 surfaces.
			* 6 corresponding :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.ruledSurface` objects.
			* 1 :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop`.
			* 1 corresponding :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.volume`.
		
		For example:
		
		>>> d=pyfrp_gmsh_geometry.domain()
		>>> d.addCylinderByParameters([256,256],100,50,100,30.,plane="z",genLoops=True,genSurfaces=True,genVol=True)
		>>> d.draw()
		
		would return:
		
		.. image:: ../imgs/pyfrp_gmsh_geometry/addCylinderByParameters.png
		
		.. note:: Plane can be given as ``"x","y","z"``. See also :py:func:`pyfrp.modules.pyfrp_gmsh_geometry.flipCoordinate`.
		
		Args:
			center (numpy.ndarray): Center of cylinder.
			radius (float): Radius of the cylinder.
			z (float): Height at which cylinder is placed.
			height (float): Height of cylinder.
			volSize (float): Mesh size of vertices.
		
		Keyword Args:
			plane (str): Plane in which cylinder is placed.
			genLoops (bool): Generate line loops.
			genSurfaces (bool): Generate surfaces.
			genVol (bool): Generate surface loop and corresponding volume.
			
		Returns:
			tuple: Tuple containing:
			
				* vertices (list): List of vertices.
				* arcs (list): List of arcs.
				* lines (list): List of lines.
				* loops (list): List of loops.
				* surfaces (list): List of surfaces.
				* surfaceLoop (pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop): Generated surface loop.
				* vol (pyfrp.modules.pyfrp_gmsh_geometry.volume): Generated volume.
		
		"""
		
		# Check input
		if genVol and not genSurfaces:
			printError("Cannot create volume when there are no surfaces.")
		if genSurfaces and not genLoops:
			printError("Cannot create surfaces when there are no loops.")
			
		# Create circles
		vertices1,arcs1=self.addCircleByParameters(center,radius,z,volSize,plane=plane)
		vertices2,arcs2=self.addCircleByParameters(center,radius,z+height,volSize,plane=plane)
		
		# Create connecting lines
		lines=[]
		lines.append(self.addLine(vertices1[1],vertices2[1]))
		lines.append(self.addLine(vertices1[2],vertices2[2]))
		lines.append(self.addLine(vertices1[3],vertices2[3]))
		lines.append(self.addLine(vertices1[4],vertices2[4]))
		
		# Generate loops
		loops=[]
		if genLoops:
			loops.append(self.addLineLoop(edgeIDs=[arcs1[0].Id,arcs1[1].Id,arcs1[2].Id,arcs1[3].Id]))
			loops.append(self.addLineLoop(edgeIDs=[arcs2[0].Id,arcs2[1].Id,arcs2[2].Id,arcs2[3].Id]))
			loops.append(self.addLineLoop(edgeIDs=[-lines[0].Id,arcs1[0].Id,lines[1].Id,-arcs2[0].Id]))
			loops.append(self.addLineLoop(edgeIDs=[-lines[1].Id,arcs1[1].Id,lines[2].Id,-arcs2[1].Id]))
			loops.append(self.addLineLoop(edgeIDs=[-lines[2].Id,arcs1[2].Id,lines[3].Id,-arcs2[2].Id]))
			loops.append(self.addLineLoop(edgeIDs=[-lines[3].Id,arcs1[3].Id,lines[0].Id,-arcs2[3].Id]))
				  
		# Generate surfaces
		surfaces=[]
		surfaceIds=[]
		if genSurfaces:
			for loop in loops:
				surfaces.append(self.addRuledSurface(lineLoopID=loop.Id))
				surfaceIds.append(surfaces[-1].Id)
				
		# Generate surface loop and volume
		if genVol:
			surfaceLoop=self.addSurfaceLoop(surfaceIDs=surfaceIds)
			vol=self.addVolume(surfaceLoopID=surfaceLoop.Id)
		else:
			surfaceLoop=None
			vol=None
		
		return [vertices1,vertices2],[arcs1,arcs2],lines,loops,surfaces,surfaceLoop,vol
			
	def checkIdExists(self,Id,objList):
		
		"""Checks if any object in ``objList`` already has ID ``Id``.
		
		Args:
			Id (int): ID to be checked.
			objList (list): List of objects, for example ``edges``.
			
		Returns:
			bool: True if any object has ID ``Id``.
		
		"""
		
		IdList=pyfrp_misc_module.objAttrToList(objList,'Id')
		if Id in IdList:
			printWarning("Object with Id " + str(Id) + " already exists.")
			return True
		return False
	
	def getNewId(self,objList,Id=None):
		
		"""Returns free ID for object type.
		
		Args:
			objList (list): List of objects, for example ``edges``.
			
		Keyword Args:
			Id (int): ID to be checked.
			
		Returns:
			int: New free ID.
		
		"""
		
		if Id==None:
			newId=self.incrementID(objList)
		else:
			if self.checkIdExists(Id,objList):
				newId=self.incrementID(objList)
			else:
				newId=Id
		
		return newId
		
	def incrementID(self,objList):
		
		"""Returns ID that is by one larger for a specific 
		object type.
		
		Args:
			objList (list): List of objects, for example ``edges``.
				
		Returns:
			int: Incremented ID.
		
		"""
		
		if len(objList)==0:
			newId=1
		else:
			IdList=pyfrp_misc_module.objAttrToList(objList,'Id')
			newId=max(IdList)+1		
		return newId
		
	def getEdgeById(self,ID):
		
		"""Returns edge with ID ``ID``.
		
		Returns ``(False,False)`` if edge cannot be found.
		
		Args:
			ID (int): ID of edge.
				
		Returns:
			tuple: Tuple containing:
				
				* e (pyfrp.modules.pyfrp_gmsh_geometry.edge): Edge.
				* i (int): Position in ``edges`` list.
		
		"""
		
		for i,e in enumerate(self.edges):
			if e.Id==ID:
				return e,i
		return False,False
	
	def getEdgeByVertices(self,v1,v2):
		
		"""Returns edge between vertex ``v1`` and ``v2``.
		
		Returns ``(False,False)`` if edge cannot be found.
		
		Args:
			v1 (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Vertex 1.
			v2 (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Vertex 2.
			
		Returns:
			tuple: Tuple containing:
				
				* e (pyfrp.modules.pyfrp_gmsh_geometry.edge): Edge.
				* i (int): Position in ``edges`` list.
		
		"""
		
		for i,e in enumerate(self.edges):
			vertices=[e.getFirstVertex(1),e.getLastVertex(1)]
		
			if v1 in vertices and v2 in vertices:
				return e,i
		return False,False	
		
	
	def getLineLoopById(self,ID):
		
		"""Returns lineLoop with ID ``ID``.
		
		Returns ``(False,False)`` if lineLoop cannot be found.
		
		Args:
			ID (int): ID of lineLoop.
				
		Returns:
			tuple: Tuple containing:
				
				* l (pyfrp.modules.pyfrp_gmsh_geometry.lineLoop): lineLoop.
				* i (int): Position in ``lineLoops`` list.
		
		"""
		
		for i,l in enumerate(self.lineLoops):
			if l.Id==ID:
				return l,i
	
		return False,False
	
	def getRuledSurfaceById(self,ID):
		
		"""Returns ruledSurface with ID ``ID``.
		
		Returns ``(False,False)`` if ruledSurface cannot be found.
		
		Args:
			ID (int): ID of ruledSurface.
				
		Returns:
			tuple: Tuple containing:
				
				* l (pyfrp.modules.pyfrp_gmsh_geometry.ruledSurface): ruledSurface.
				* i (int): Position in ``ruledSurfaces`` list.
		
		"""
		
		for i,l in enumerate(self.ruledSurfaces):
			if l.Id==ID:
				return l,i
		return False,False
	
	def getSurfaceLoopById(self,ID):
		
		"""Returns surfaceLoop with ID ``ID``.
		
		Returns ``(False,False)`` if surfaceLoop cannot be found.
		
		Args:
			ID (int): ID of surfaceLoop.
				
		Returns:
			tuple: Tuple containing:
				
				* l (pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop): surfaceLoop.
				* i (int): Position in ``surfaceLoops`` list.
		
		"""
		
		for i,l in enumerate(self.surfaceLoops):
			if l.Id==ID:
				return l,i
		return False,False
	
	def getVolumeById(self,ID):
		
		"""Returns volume with ID ``ID``.
		
		Returns ``(False,False)`` if volume cannot be found.
		
		Args:
			ID (int): ID of volume.
				
		Returns:
			tuple: Tuple containing:
				
				* l (pyfrp.modules.pyfrp_gmsh_geometry.volume): volume.
				* i (int): Position in ``volumes`` list.
		
		"""
		
		for i,l in enumerate(self.volumes):
			if l.Id==ID:
				return l,i
		return False,False
	
	def getVertexById(self,ID):
		
		"""Returns vertex with ID ``ID``.
		
		Returns ``(False,False)`` if vertex cannot be found.
		
		Args:
			ID (int): ID of vertex.
				
		Returns:
			tuple: Tuple containing:
				
				* v (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Vertex.
				* i (int): Position in ``edges`` list.
		
		"""
		
		for i,v in enumerate(self.vertices):
			if v.Id==ID:
				return v,i
		return False,False
		
	def draw(self,ax=None,color=None,ann=None):
		
		"""Draws complete domain.
		
		.. note:: If ``ann=None``, will set ``ann=False``.
		
		.. note:: If no axes is given, will create new one.
		
		Keyword Args:
			ax (matplotlib.axes): Matplotlib axes to be plotted in.
			color (str): Color of domain.
			ann (bool): Show annotations.
				
		Returns:
			matplotlib.axes: Axes.
		
		"""
		
		if ann==None:
			ann=False
		
		if color==None:
			color='k'
		
		if ax==None:
			fig,axes = pyfrp_plot_module.makeGeometryPlot()
			
			ax=axes[0]
		
		for v in self.vertices:
			v.draw(ax=ax,color=color,ann=ann)
		for e in self.edges:
			e.draw(ax=ax,color=color,ann=ann)	
		for a in self.arcs:
			a.draw(ax=ax,color=color,ann=ann)	
		
		return ax
		
	def getExtend(self):
		
		"""Returns extend of domain in all 3 dimensions.
		
		Returns: 
			tuple: Tuple containing:
				
				* minx (float): Minimal x-coordinate.
				* maxx (float): Maximal x-coordinate.
				* miny (float): Minimal y-coordinate.
				* maxy (float): Maximal y-coordinate.
				* minz (float): Minimal z-coordinate.
				* maxz (float): Maximal z-coordinate.
	
		"""
			
		x=[]
		y=[]
		z=[]
		for v in self.vertices:
			x.append(v.x[0])
			y.append(v.x[1])
			z.append(v.x[2])
		return min(x), max(x), min(y),max(y), min(z),max(z)
	
	def verticesCoordsToList(self):
		
		"""Returns list of coordinates from all vertrices.
		
		Returns:
			list: List of (x,y,z) coordinates.
		
		"""
		
		l=[]
		for v in self.vertices:
			l.append(v.x)
		return l
	
	def addLineLoop(self,Id=None,edgeIDs=[]):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.lineLoop` instance
		with given edgeIDs. 
			
		Keyword Args:
			edgeIDs (list): List of edge IDs included in line loop.
			
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.lineLoop: New lineLoop instance.
		
		"""
		
		newId=self.getNewId(self.lineLoops,Id)
		
		l=lineLoop(self,edgeIDs,newId)
		self.lineLoops.append(l)
		
		return l
	
	def addSurfaceLoop(self,Id=None,surfaceIDs=[]):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop` instance
		with given surfaceIDs. 
			
		Keyword Args:
			surfaceIDs (list): List of surface IDs included in surface loop.
			
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.surfaceLoop: New surfaceLoop instance.
		
		"""
		
		newId=self.getNewId(self.surfaceLoops,Id)
		
		l=surfaceLoop(self,surfaceIDs,newId)
		self.surfaceLoops.append(l)
		
		return l
	
	def addRuledSurface(self,Id=None,lineLoopID=None):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.ruledSurface` instance
		with given lineLoop. 
			
		Keyword Args:
			lineLoopID (ID): ID of line loop.
			
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.ruledSurface: New ruledSurface instance.
		
		"""
		
		newId=self.getNewId(self.ruledSurfaces,Id)
		
		l=ruledSurface(self,lineLoopID,newId)
		self.ruledSurfaces.append(l)
		
		return l
	
	def addVolume(self,Id=None,surfaceLoopID=None):
		
		"""Adds new :py:class:`pyfrp.modules.pyfrp_gmsh_geometry.volume` instance
		with given surfaceLoop. 
			
		Keyword Args:
			surfaceLoopID (ID): ID of surface loop.
			
		Returns:
			pyfrp.modules.pyfrp_gmsh_geometry.volume: New volume instance.
		
		"""
		
		newId=self.getNewId(self.volumes,Id)
		
		l=volume(self,surfaceLoopID,newId)
		self.volumes.append(l)
		
		return l
	
	
	def writeToFile(self,fn):
		
		"""Writes domain to file.
		
		Args:
			fn (str): File path to write to.
			
		"""
		
		with open(fn,'wb') as f:
			
			self.writeElements("vertices",f)
			self.writeElements("lines",f)
			self.writeElements("arcs",f)
			self.writeElements("lineLoops",f)
			self.writeElements("ruledSurfaces",f)
			self.writeElements("surfaceLoops",f)
			self.writeElements("volumes",f)

	def writeElements(self,element,f):
			
		"""Writes all entities of a specific element type to file.
		
		Possible elements are:
		
			* vertices
			* lines
			* arcs
			* lineLoops
			* ruledSurfaces
			* surfaceLoops
			* volumes
		
		Args:
			element (str): Element type to write.
			f (file): File to write to.
			
		"""
	
		pyfrp_gmsh_IO_module.writeComment(f,element)
		for v in getattr(self,element):
			f=v.writeToFile(f)
		f.write("\n")
	
	def incrementAllIDs(self,offset):
		
		"""Adds offset to all entity IDs.
		
		Args:
			offset (int): Offset to be added.
			
		"""
		
		self.incrementIDs(offset,"vertices")
		self.incrementIDs(offset,"lines")
		self.incrementIDs(offset,"arcs")
		self.incrementIDs(offset,"lineLoops")
		self.incrementIDs(offset,"ruledSurfaces")
		self.incrementIDs(offset,"surfaceLoops")
		self.incrementIDs(offset,"volumes")
		
	def incrementIDs(self,offset,element):
		
		"""Adds offset to all entity IDs.
		
		Possible elements are:
		
			* vertices
			* lines
			* arcs
			* lineLoops
			* ruledSurfaces
			* surfaceLoops
			* volumes
		
		Args:
			offset (int): Offset to be added.
			element (str): Element type to increment.
		
		"""
		
		for e in getattr(self,element):		
			e.Id=e.Id+offset
	
	def getMaxID(self,element):
		
		"""Returns maximum ID for a specific element.
		
		Possible elements are:
		
			* vertices
			* lines
			* arcs
			* lineLoops
			* ruledSurfaces
			* surfaceLoops
			* volumes
		
		Args:
			element (str): Element type.
			
		Returns:
			int: Maximum ID.
		"""
		
		IDs=[]
		
		for e in getattr(self,element):
			IDs.append(e.Id)
			
		return max(IDs)
	
	def getAllMaxID(self):
		
		"""Returns maximum ID over all elements.
			
		Returns:
			int: Maximum ID.
		"""
		
		IDs=[]
		
		IDs.append(self.getMaxID("vertices"))
		IDs.append(self.getMaxID("lines"))
		IDs.append(self.getMaxID("arcs"))
		IDs.append(self.getMaxID("lineLoops"))
		IDs.append(self.getMaxID("ruledSurfaces"))
		IDs.append(self.getMaxID("surfaceLoops"))
		IDs.append(self.getMaxID("volumes"))
		
		return max(IDs)
		
class vertex:
	
	"""Vertex class storing information from gmsh .geo Points.
	
	.. note:: ``volSize`` does not have any effect on the geometry itself but is simply 
		stored in the vertex object for further usage.
	
	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain vertex belongs to.
		x (numpy.ndarray): Coordinate of vertex.
		Id (int): ID of vertex.
			
	Keyword Args:
		volSize (float): Element size at vertex.
		
	"""
	
	def __init__(self,domain,x,Id,volSize=None):
		self.domain=domain
		
		self.x=np.array(x)
		self.Id=Id
		self.volSize=volSize
			
	def draw(self,ax=None,color=None,ann=None):
		
		"""Draws vertrex into axes.
		
		.. note:: If ``ann=None``, will set ``ann=False``.
		
		.. note:: If no axes is given, will create new one.
		
		Keyword Args:
			ax (matplotlib.axes): Matplotlib axes to be plotted in.
			color (str): Color of domain.
			ann (bool): Show annotations.
				
		Returns:
			matplotlib.axes: Axes.
		
		"""
		
		if ann==None:
			ann=False
		
		if ax==None:
			fig,axes = pyfrp_plot_module.makeGeometryPlot()
			ax=axes[0]
			
		ax.scatter(self.x[0],self.x[1],self.x[2],c=color)
		if ann:
			ax.text(self.x[0]+self.domain.annXOffset, self.x[1]+self.domain.annYOffset, self.x[2]+self.domain.annZOffset, "p"+str(self.Id), None)
			
		pyfrp_plot_module.redraw(ax)
		
		return ax
		
	def setX(self,x):
		
		"""Sets coordinate if vertex to ``x``.
		
		Returns:
			numpy.ndarray: New vertex coordinate.
		"""
		
		self.x=x
		return self.x
	
	def writeToFile(self,f):
		
		"""Writes vertex to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Point("+str(self.Id)+")= {" + str(self.x[0]) + ","+ str(self.x[1])+ "," + str(self.x[2]) + ',' + str(self.volSize) + "};\n" )
		
		return f
	
	
class edge:
	
	"""Edge class storing information from gmsh .geo circles and lines.
	
	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain vertex belongs to.
		Id (int): ID of edge.
		typ (int): Type of edge (1=arc/0=line).
			
	"""
	
	def __init__(self,domain,Id,typ):
		self.domain=domain
		self.Id=Id
		self.typ=typ
		
	def getDomain(self):
		
		"""Returns domain edge belongs to."""
		
		return self.domain
	
	def getId(self):
		
		"""Returns edges ID."""
		
		return self.Id
	
	def getTyp(self):
		
		"""Returns Type of edge."""
		
		return self.typ
	
	def decodeTyp(self):
		
		"""Decodes type of edge into string."""
		
		if typ==1:
			return "arc"
		elif typ==0:
			return "line"
	
class line(edge):
	
		
	"""Line class storing information from gmsh .geo lines.
	
	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain line belongs to.
		v1 (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Start vertex.
		v2 (pyfrp.modules.pyfrp_gmsh_geometry.vertex): End vertex.
		Id (int): ID of line.
		
	"""
	
	
	def __init__(self,domain,v1,v2,Id):
		
		edge.__init__(self,domain,Id,0)

		self.v1=v1
		self.v2=v2
	
	def getMiddle(self):
		
		r"""Returns midpoint of line.
		
		.. math:: m = \frac{x(v_1) + x(v_2)}{2}
		     
		Returns:
			numpy.ndarray: Midpoint.
			
		"""
		
		return (self.v1.x+self.v2.x)/2.
	
	def draw(self,ax=None,color=None,ann=None):
			
		"""Draws line into axes.
		
		.. note:: If ``ann=None``, will set ``ann=False``.
		
		.. note:: If no axes is given, will create new one.
		
		Keyword Args:
			ax (matplotlib.axes): Matplotlib axes to be plotted in.
			color (str): Color of domain.
			ann (bool): Show annotations.
				
		Returns:
			matplotlib.axes: Axes.
		
		"""
		
		if ann==None:
			ann=False
		
		if ax==None:
			fig,axes = pyfrp_plot_module.makeGeometryPlot()
			ax=axes[0]
		ax.plot([self.v1.x[0],self.v2.x[0]],[self.v1.x[1],self.v2.x[1]],zs=[self.v1.x[2],self.v2.x[2]],color=color,linestyle='-')
		if ann:
			m=self.getMiddle()
			ax.text(m[0]+self.domain.annXOffset, m[1]+self.domain.annYOffset, m[2]+self.domain.annZOffset, "l"+str(self.Id), None)
		
		pyfrp_plot_module.redraw(ax)
		
		return ax
		
	def getLastVertex(self,orientation):
		
		"""Returns last vertex of arc given a orientation.
		
		Orientation can be either forward (1), or reverse (-1).
		
		Args:
			orientation (int): Orientation of arc.
			
		Returns:
			pyfrp.pyfrp_gmsh_geometry.vertex: Vertex.
		
		"""
		
		if orientation==1:
			return self.v2
		elif orientation==-1:
			return self.v1
		else:
			printError("Cannot return last vertex. Orientation " + str(orientation) + " unknown.")
			return None
	
	def getFirstVertex(self,orientation):
		
		"""Returns first vertex of arc given a orientation.
		
		Orientation can be either forward (1), or reverse (-1).
		
		Args:
			orientation (int): Orientation of arc.
			
		Returns:
			pyfrp.pyfrp_gmsh_geometry.vertex: Vertex.
		
		"""
		
		if orientation==1:
			return self.v1
		elif orientation==-1:
			return self.v2
		else:
			printError("Cannot return first vertex. Orientation " + str(orientation) + " unknown.")
			return None
	
	def writeToFile(self,f):
		
		"""Writes line to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Line("+str(self.Id)+")= {" + str(self.v1.Id) + "," + str(self.v2.Id) + "};\n" )
		
		return f
	
	
class arc(edge):
	
	"""Arc class storing information from gmsh .geo cicle.
	
	Will compute ``angleOffset``, ``angle`` and ``pOffset`` on creation.
	
	.. image:: ../imgs/pyfrp_gmsh_geometry/arc.png
	
	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain arc belongs to.
		vstart (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Start vertex.
		vcenter (pyfrp.modules.pyfrp_gmsh_geometry.vertex): Center vertex.
		vend (pyfrp.modules.pyfrp_gmsh_geometry.vertex): End vertex.
		Id (int): ID of arc.
		
	"""		
	
	def __init__(self,domain,vstart,vcenter,vend,Id):
		
		edge.__init__(self,domain,Id,1)
		
		self.vcenter=vcenter
		self.vstart=vstart
		self.vend=vend
		
		self.radius=self.computeRadius()
		
		self.pOffset=self.computePOffset()
		
		self.angleOffset=self.computeAngleOffset()
		self.angle=self.computeAngle()
		
	

	def computeAngleOffset(self):
		
		"""Computes and returns offset angle of arc.
		"""
		
		self.angleOffset=getAngle(self.pOffset,self.vstart.x-self.vcenter.x)
		
		return self.angleOffset
	
	def computeAngle(self):
		
		"""Computes and returns angle of arc.
		"""
		
		self.angle=getAngle(self.vstart.x-self.vcenter.x,self.vend.x-self.vcenter.x)
		return self.angle
	
	def computePOffset(self):
		
		"""Computes and returns offset point of arc.
		"""
		
		v1n,v2nb = self.getNormVec()
		
		self.pOffset=self.radius*v2nb
		self.pOffset=self.pOffset/np.linalg.norm(self.pOffset)
		
		return self.pOffset
	
	def getNormVec(self):
		
		"""Computes and returns vectors normal to arc.
		
		Returns:
			tuple: Tuple containing:
				
				* v1n (numpy.ndarray): Normal vector to ``vstart-vcenter``.
				* v2n (numpy.ndarray): Normal vector to ``vend-vcenter``.
					
		"""
		
		v1=self.vstart.x-self.vcenter.x
		v2=self.vend.x-self.vcenter.x
		
		self.v1n = v1/np.linalg.norm(v1)
		v2n = v2/np.linalg.norm(v2)
		v2nb = v2n-np.dot(v2n,self.v1n)*self.v1n
		
		self.v2nb = v2nb/np.linalg.norm(v2nb)
		
		return self.v1n,self.v2nb
	
	def getPlotVec(self):
		
		"""Returns vectors for plotting arc.
		
		Returns:
			tuple: Tuple containing:
				
				* x (numpy.ndarray): x-array.
				* y (numpy.ndarray): y-array.
				* z (numpy.ndarray): z-array.
						
		"""
		
		self.getNormVec()
			
		if np.mod(self.angle,np.pi/2.)<0.01:
			a = np.linspace(0,self.angle,1000)
		else:
			a = np.linspace(self.angleOffset-self.angle,self.angleOffset,1000)
				
		x,y,z=self.getPointOnArc(a)
		
		return x,y,z
	
	def getPointOnArc(self,a):
		
		"""Returns point on arc at angle ``a``.
		
		Returns:
			tuple: Tuple containing:
				
				* x (float): x-coordinate.
				* y (float): y-coordinate.
				* z (float): z-coordinate.
						
		"""
			
		x = self.vcenter.x[0]+np.sin(a)*self.radius*self.v1n[0]+np.cos(a)*self.radius*self.v2nb[0]
		y = self.vcenter.x[1]+np.sin(a)*self.radius*self.v1n[1]+np.cos(a)*self.radius*self.v2nb[1]
		z = self.vcenter.x[2]+np.sin(a)*self.radius*self.v1n[2]+np.cos(a)*self.radius*self.v2nb[2]	
		
		return x,y,z

	def computeRadius(self):
		
		"""Computes and returns radius of arc.
		
		Returns:
			float: Radius of arc.
		"""
		
		self.radius=np.linalg.norm(self.vstart.x-self.vcenter.x)
		return self.radius
		
	def inArc(self,x,debug=False):
		
		"""Tells if coordinate ``x`` is on arc or not.
		
		Returns:
			bool: ``True`` if on arc, ``False`` otherwise.
		"""
		
		a=self.computeAngle(array([self.radius,0])-self.vcenter.x,x-self.vcenter.x)
				
		if np.mod(a,2*np.pi)<self.angle+self.angleOffset and self.angleOffset<=np.mod(a,2*np.pi):
			return True
		else:
			return False
	
	def getRadius(self):
		
		"""Returns radius of arc."""
		
		return self.radius
	
	def getAngle(self):
		
		"""Returns angle of arc."""
		
		return self.angle
	
	def getAngleOffset(self):
		
		"""Returns offset angle of arc."""
		
		return self.angleOffset
	
	def getVstart(self):
		
		"""Returns start vertex of arc."""
		
		return self.vstart
	
	def getVend(self):
		
		"""Returns end vertex of arc."""
		
		return self.vend
	
	def getXstart(self):
		
		"""Returns start coordinate of arc."""
		
		return self.vstart.x
	
	def getXend(self):
		
		"""Returns end coordinate of arc."""
		
		return self.vend.x
	
	def getVcenter(self):
		
		"""Returns center vertex of arc."""
		
		return self.vcenter
	
	def getXcenter(self):
		
		"""Returns center coordinate of arc."""
		
		return self.vcenter.x
	
	def draw(self,ax=None,color=None,ann=None):
		
		"""Draws arc into axes.
		
		.. note:: If ``ann=None``, will set ``ann=False``.
		
		.. note:: If no axes is given, will create new one.
		
		Keyword Args:
			ax (matplotlib.axes): Matplotlib axes to be plotted in.
			color (str): Color of domain.
			ann (bool): Show annotations.
				
		Returns:
			matplotlib.axes: Axes.
		
		"""
		
		if ann==None:
			ann=False
		
		if ax==None:
			fig,axes = pyfrp_plot_module.makeGeometryPlot()
			ax=axes[0]
			
		x,y,z=self.getPlotVec()
		
		ax.plot(x,y,zs=z,color=color,linestyle='-')
		
		if ann:
			x,y,z=self.getPointOnArc(self.angle/2.)
			ax.text(x+self.domain.annXOffset, y+self.domain.annYOffset, z+self.domain.annZOffset, "c"+str(self.Id), None)
			
			
			
		pyfrp_plot_module.redraw(ax)
	
	def getLastVertex(self,orientation):
		
		"""Returns last vertex of arc given a orientation.
		
		Orientation can be either forward (1), or reverse (-1).
		
		Args:
			orientation (int): Orientation of arc.
			
		Returns:
			pyfrp.pyfrp_gmsh_geometry.vertex: Vertex.
		
		"""
		
		if orientation==1:
			return self.getVend()
		elif orientation==-1:
			return self.getVstart()
		else:
			printError("Cannot return last vertex. Orientation " + str(orientation) + " unknown.")
			return None
	
	def getFirstVertex(self,orientation):
		
		"""Returns first vertex of arc given a orientation.
		
		Orientation can be either forward (1), or reverse (-1).
		
		Args:
			orientation (int): Orientation of arc.
			
		Returns:
			pyfrp.pyfrp_gmsh_geometry.vertex: Vertex.
		
		"""
		
		if orientation==-1:
			return self.getVend()
		elif orientation==1:
			return self.getVstart()
		else:
			printError("Cannot return first vertex. Orientation " + str(orientation) + " unknown.")
			return None
	
	def writeToFile(self,f):
		
		"""Writes arc to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Circle("+str(self.Id)+")= {" + str(self.vstart.Id) + ","+ str(self.vcenter.Id)+ "," + str(self.vend.Id) + "};\n" )
		
		return f
	
class lineLoop:
	
	"""Lineloop class storing information from gmsh .geo.

	Object has two major attributes:
	
		* edges (list): List of pyfrp.moduels.pyfrp_gmsh_geometry.edge objects.
		* orientations (list): List of orientations of each element, either ``1`` or ``-1`` 
	
	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain loop belongs to.
		edgeIDs (list): List of edge IDs.
		Id (int): ID of loop.
		
	"""		
	
	def __init__(self,domain,edgeIDs,ID):
		
		self.domain=domain
		self.Id=ID
		
		self.edges,self.orientations=self.initEdges(edgeIDs)
		
	def initEdges(self,IDs):
		
		"""Constructs ``edges`` and ``orientations`` list at object initiations 
		from list of IDs.
		
		Args:
			IDs (list): List of IDs
			
		Returns:
			tuple: Tuple containing:
			
				* edges (list): List of pyfrp.moduels.pyfrp_gmsh_geometry.edge objects.
				* orientations (list): List of orientations of each element, either ``1`` or ``-1`` 
		
		"""
		
		self.edges=[]
		self.orientations=[]
		
		for ID in IDs:
			self.addEdgeByID(ID)
		
		return self.edges,self.orientations
		
	def addEdgeByID(self,ID):
		
		"""Adds edge to lineloop.
		
		Args:
			ID (int): ID of edge to be added.
			
		Returns:
			list: Updated edgeIDs list.
			
		"""
		
		
		self.edges.append(self.domain.getEdgeById(abs(ID))[0])
		self.orientations.append(np.sign(ID))
		
		return self.edges
	
	def insertEdgeByID(self,ID,pos):
		
		"""Inserts edge to lineloop at position.
		
		Args:
			ID (int): ID of edge to be inserted.
			pos (int): Position at which ID to be inserted.
			
		Returns:
			list: Updated edgeIDs list.
			
		"""
		
		self.edges.insert(pos,self.domain.getEdgeById(abs(ID))[0])
		self.orientations.insert(pos,np.sign(ID))
		
		return self.edges
	
	def removeEdgeByID(self,ID):
		
		"""Remove edge from lineloop.
		
		Args:
			ID (int): ID of edge to be removed.
			
		Returns:
			list: Updated edgeIDs list.
			
		"""
		
		idx=self.edges.index(abs(ID))
		self.edges.remove(abs(ID))
		self.orientations.pop(idx)
		
		return self.edges
	
	def reverseEdge(self,ID):
		
		"""Reverses the orientation of an edge in the line loop.
		
		Args:
			ID (int): ID of edge to be reversed.
		
		Returns:
			list: Updated orientations list.
			
		"""
		
		e=self.domain.getEdgeById(abs(ID))[0]
		self.orientations[self.edges.index(e)]=-self.orientations[self.edges.index(e)]
		
		return self.orientations
		
	def checkClosed(self,fix=False,debug=False):
		
		"""Checks if lineLoop is closed.
		
		Keyword Args:
			debug (bool): Print debugging messages.
			fix (bool): Close if necessary.
			
		Returns:
			bool: True if closed.
		
		"""
		
		b=True
		
		for i in range(len(self.edges)):
			
			#Get ID of edge
			edge1Temp=self.edges[i]
			orient1=self.orientations[i]
			
			#Get ID of next edge
			edge2Temp=self.edges[pyfrp_misc_module.modIdx(i+1,self.edges)]
			orient2=self.orientations[pyfrp_misc_module.modIdx(i+1,self.edges)]
			
			#Get ID of first/last vertex
			firstVertexId=edge1Temp.getFirstVertex(orient1).Id
			lastVertexId=edge2Temp.getLastVertex(orient2).Id
			
			#Check if vertices are matching
			if firstVertexId!=lastVertexId:
				b=False
				
				if fix:
					self.reverseEdge(edge2Temp.Id)
					b=True
			
					if debug:
						print "Edge with ID " +str(edge1Temp.Id) + " was not matching edge with ID " + str(edge2Temp.Id) + ". \n Fixed this."
				
					
				if debug:
					printWarning("lineLoop with ID " + str(self.Id) + " does not close." )
					print "Edge with ID " +str(edge1Temp.Id) + " is not matching edge with ID " + str(edge2Temp.Id)
						
		return b
	
	def writeToFile(self,f):
		
		"""Writes line loop to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Line Loop("+str(self.Id)+")= {" )
			
		for i,s in enumerate(self.edges):
			f.write(str(self.orientations[i]*s.Id))
			if i!=len(self.edges)-1:
				f.write(",")
			else:
				f.write("};\n")
	
		return f
	
	def getVertices(self):
		
		"""Returns all vertices included in loop."""
		
		vertices=[]
		for i,edge in enumerate(self.edges):
			vertices.append(edge.getFirstVertex(self.orientations[i]))
		return vertices	
			
class ruledSurface:
	
	"""ruledSurface class storing information from gmsh .geo.

	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain surface belongs to.
		loopID (int): ID of surrounding loop.
		Id (int): ID of surface.
		
	"""		
	
	def __init__(self,domain,loopID,ID):
		
		self.domain=domain
		self.Id=ID
		
		
		self.initLineLoop(loopID)
	
	def initLineLoop(self,loopID,debug=False):
	
		"""Checks length of lineLoop and if length of lineLoop is greater
		than 4, will perform triangulation so Gmsh can handle surface."""
		
		#Get lineLoop
		self.lineLoop=self.domain.getLineLoopById(loopID)[0]
		
		#Check length
		if len(self.lineLoop.edges)<=4:
			return False
		
		#Get vertices
		vertices=self.lineLoop.getVertices()
		
		#Get coordinates
		coords=pyfrp_misc_module.objAttrToList(vertices,"x")
		
		#Compute normal vector
		self.getNormal()
		
		#Check if normal to plane
		if not self.normalToPlane():
			printError("ruledSurface with ID" +  str(self.Id) + "is not normal to a plane and has more than 4 edges. PyFRAP is not able to triangulate surface down to smaller pieces.")
			return False
		
		#Get coordinates in plane
		coordsPlane=np.asarray(coords)[:,np.where(self.normal!=1)[0]]
	
		#Create triangulation
		tri,coordsTri = pyfrp_idx_module.triangulatePoly(coordsPlane)
		
		#Loop through each triangle 
		for i in range(len(tri)):
			
			edges=[]
			
			#Loop through each vertex 
			for j in range(len(tri[i])):
				v1=vertices[tri[i][j]]
				v2=vertices[tri[i][pyfrp_misc_module.modIdx(j+1,tri[i])]]
				
				#Check if edge already exists
				if not self.domain.getEdgeByVertices(v1,v2)[0]:
					edges.append(self.domain.addLine(v1,v2))
				else:
					edges.append(self.domain.getEdgeByVertices(v1,v2)[0])
			
			#Add line loop
			edgeIDs=pyfrp_misc_module.objAttrToList(edges,"Id")
			loop=self.domain.addLineLoop(edgeIDs=edgeIDs)
			loop.checkClosed(fix=True,debug=True)
			
			#Add ruledSurface if necessary
			if i==0:
				self.lineLoop=loop
			else:
				self.domain.addRuledSurface(lineLoopID=loop.Id,Id=self.Id+i)
		
		#Delete original loop
		self.domain.lineLoops.remove(self.domain.getLineLoopById(loopID)[0])
		
		return True
		
	def normalToPlane(self):
		
		"""Checks if surface lies within either x-y-/x-z-/y-z-plane.
		
		Does this by checking if ``1.`` is in the normal vector.
		
		Returns:
			bool: True if in plane.
		
		"""
		
		return 1. in self.normal
	
	def getNormal(self):
		
		"""Computes normal to surface using Newell's method.
		
		Adapted from http://stackoverflow.com/questions/39001642/calculating-surface-normal-in-python-using-newells-method.
		
		Returns:
			numpy.ndarray: Normal vector to surface.
		"""
		
		#Get vertices
		vertices=self.lineLoop.getVertices()
		
		#Newell's method
		n = [0.0, 0.0, 0.0]
		
		for i, v in enumerate(vertices):
			v2 = vertices[(i+1) % len(vertices)]
			n[0] += (v.x[1] - v2.x[1]) * (v.x[2] + v2.x[2])
			n[1] += (v.x[2] - v2.x[2]) * (v.x[0] - v2.x[0])
			n[2] += (v.x[0] - v2.x[0]) * (v.x[1] - v2.x[1])
		
		normalised = [i/sum(n) for i in n]
		
		self.normal=np.asarray(normalised)
		
		return self.normal

		
	def writeToFile(self,f):
		
		"""Writes ruled surface to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Ruled Surface("+str(self.Id)+")= {"+str(self.lineLoop.Id)+ "};\n" )
	
		return f
	
class surfaceLoop:
	
	"""surfaceLoop class storing information from gmsh .geo.

	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain loop belongs to.
		surfaceIDs (list): List of surfaces.
		Id (int): ID of loop.
		
	"""		
	
	def __init__(self,domain,surfaceIDs,ID):
		
		self.domain=domain
		self.Id=ID
		
		self.surfaces=self.initSurfaces(surfaceIDs)	
		
	def initSurfaces(self,IDs):
		
		"""Constructs ``surfaces`` list at object initiations 
		from list of IDs.
		
		Args:
			IDs (list): List of IDs.
			
		Returns:
			list: List of pyfrp.modules.pyfrp_gmsh_geometry.ruledSurface objects.
		
		"""
		
		self.surfaces=[]
		
		for ID in IDs:
			self.addSurfaceByID(ID)
		
		return self.surfaces
	
	def addSurfaceByID(self,ID):
		
		"""Adds surface to surfaceloop.
		
		Args:
			ID (int): ID of surface to be added.
			
		Returns:
			list: Updated surfaceIDs list.
			
		"""
		
		self.surfaces.append(self.domain.getRuledSurfaceById(ID)[0])
		
		return self.surfaces
	
	def insertSurfaceByID(self,ID,pos):
		
		"""Inserts surface to surfaceloop at position.
		
		Args:
			ID (int): ID of surface to be inserted.
			pos (int): Position at which ID to be inserted.
			
		Returns:
			list: Updated surfaceIDs list.
			
		"""
		
		self.surfaces.insert(pos,self.domain.getRuledSurfaceById(ID)[0])
		
		return self.surfaces
	
	def removeSurfaceByID(self,ID):
		
		"""Remove surface from surfaceloop.
		
		Args:
			ID (int): ID of surface to be removed.
			
		Returns:
			list: Updated surfaceIDs list.
			
		"""
		
		self.surfaces.remove(self.domain.getRuledSurfaceById(ID)[0])
		
		return self.surfaces
	
	def writeToFile(self,f):
		
		"""Writes surface loop to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Surface Loop("+str(self.Id)+")= {" )
		
		for i,s in enumerate(self.surfaces):
			f.write(str(s.Id))
			if i!=len(self.surfaces)-1:
				f.write(",")
			else:
				f.write("};\n")
	
		return f
	
class volume:

	"""Volume class storing information from gmsh .geo.

	Args:
		domain (pyfrp.modules.pyfrp_gmsh_geometry.domain): Domain surface belongs to.
		surfaceLoopID (int): ID of surrounding surface loop.
		Id (int): ID of surface loop.
		
	"""		
	
	def __init__(self,domain,surfaceLoopID,ID):
		
		self.domain=domain
		self.Id=ID
		
		self.surfaceLoop=self.domain.getSurfaceLoopById(surfaceLoopID)[0]
	
	def writeToFile(self,f):
		
		"""Writes Volume to file.
		
		Args:
			f (file): File to write to.
			
		Returns:
			file: File.
		
		"""
		
		f.write("Volume("+str(self.Id)+")= {"+str(self.surfaceLoop.Id)+ "};\n" )
	
		return f
				
			