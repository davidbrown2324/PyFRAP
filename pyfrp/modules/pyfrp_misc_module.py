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

#Misc module for PyFRAP toolbox, including following functions:

#save_settings: Saves settings
#build_type_array: Builds array of types of list of variables
#conv_str_to_float_list: Converts list read out as string back into a list


#===========================================================================================================================================================================
#Importing necessary modules
#===========================================================================================================================================================================

#PyFRAP modules
from pyfrp_term_module import *
from pyfrp.modules import pyfrp_img_module

#PyFRAP subclasses


#Numpy
import numpy as np

#Misc
import csv
import time
import os
import inspect
import platform

#===========================================================================================================================================================================
#Module Functions
#===========================================================================================================================================================================

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Gets sorted file list from folder for files of type f_type

def getSortedFileList(fnFolder,fType):
	
	#Getting files in datafolder
	try:
		fileList=os.listdir(fnFolder)
	except OSError:
		printWarning("Folder " + fnFolder + " does not exist.")
		return []
		
	fileListNew=[]
	
	#Going through all filenames 
	for i in range(len(fileList)):
		#Check if its the right file type
		if fType in fileList[i]:
			fileListNew.append(fileList[i])
	
	#Sorting
	fileListNew.sort()
	fileList=fileListNew
	
	return fileList

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#saves array of data in csv file
	
def save_to_csv(vars_data_names,vars_data_values,fn_save):
	
	#Get timestamp
	ts = time.time()
	timestamp=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d%H:%M:%S')
	
	fn_save=fn_save+"_"+timestamp+".csv"
	
	#Open file for writing
	wfile=csv.writer(open(fn_save,'wb'), delimiter=';')
	
	#Creating type_vecs
	vars_data_types=build_type_array(vars_data_values)
	
	#Writing current settings
	wfile.writerow(vars_data_names)
	wfile.writerow(vars_data_types)
	wfile.writerow(vars_data_values)
	
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Checks filenames in object and adjusts them to work on the respective operating system

def adjust_filepaths(mol,newbase,osold="",osnew="",basefolder_old="",embs=[],mode='auto',gui=None,debug=False):
	
	if debug:
		print "======= adjust_filepaths debugging output ======="
	
	if embs==[]:
		embs=range(len(mol.embryos))

	for i,emb in enumerate(mol.embryos):
		if i in embs:
			
			#Dump all 
			data_old=emb.fn_datafolder
			res_old=emb.fn_resultfolder
			pre_old=emb.fn_preimage
			
			#Set adjust flag True
			adjust=True
			
			
			#Make sure to convert 
			if os.path.exists(data_old):
				if gui==None:
					if mode!="auto":
						ans=raw_input("Data path in embryo " + emb.name + "already exists on this machine, are you sure to change names? [Y/N]")
						if ans=="N":
							adjust=False
					else:
						adjust=False
			
			###NOTE: Not sure if I need this: will need to fix
			#if newbase in data_old:
				#if gui==None:
					#ans=raw_input("Newbase seems to be already in fn_datafolder of embryo " + emb.name + ". Are you sure to change names? [Y/N]")
					#if mode!="auto":
						#if ans=="N":
							#return mol
					#else:
						#return mol
			
			if adjust:
			
				#Change filepathing system
				if osold!=osnew:
					if osold in ["win","Win","Windows"] and osnew in ["lin","Linux","osx","OSX"]:	
						emb.fn_datafolder=win2lin_path(emb.fn_datafolder)
						emb.fn_resultfolder=win2lin_path(emb.fn_resultfolder)
						emb.fn_preimage=win2lin_path(emb.fn_preimage)	
					elif osnew in ["win","Win","Windows"] and osold in ["lin","Linux","osx","OSX"]:	
						emb.fn_datafolder=lin2win_path(emb.fn_datafolder)
						emb.fn_resultfolder=lin2win_path(emb.fn_resultfolder)
						emb.fn_preimage=lin2win_path(emb.fn_preimage)
					else:
						print "Warning, can't convert filepaths from os=", osold, " to os=", osnew, " ."
				
				#Adjust basefolder	
				emb.fn_datafolder=subst_basepath(emb.fn_datafolder,basefolder_old,newbase)
				emb.fn_resultfolder=subst_basepath(emb.fn_resultfolder,basefolder_old,newbase)
				emb.fn_preimage=subst_basepath(emb.fn_preimage,basefolder_old,newbase)
					
				if debug:
					print data_old, " --> " , emb.fn_datafolder
					print res_old, " --> " ,emb.fn_resultfolder
					print pre_old, " --> " ,emb.fn_preimage
					
	return mol		
			
				
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Converts Linux Path to Win path (/ -> \\)

def lin2win_path(p):
	r=p.replace("/","\\")
	return r

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Converts Win Path to Linux path (\\ -> /)

def win2lin_path(p):
	r=p.replace("\\","/")
	return r

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Substitute basefolder of filepath

def subst_basepath(p,basefolder_old,newbase):
	
	if basefolder_old=='':
		basefolder_old=lcs(p,newbase)
		

	if p!="":
		if basefolder_old in p and basefolder_old!="":
			base,end=p.split(basefolder_old)
		else:
			end=""
			base=""
	else:
		end=""
		base=""
	
	pnew=newbase+end
	return pnew

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Find longest common substring, taken from http://www.bogotobogo.com/python/python_longest_common_substring_lcs_algorithm_generalized_suffix_tree.php

def lcs(S,T):
	m = len(S)
	n = len(T)
	counter = [[0]*(n+1) for x in range(m+1)]
	longest = 0
	lcs_set = set()
	for i in range(m):
		for j in range(n):
			if S[i] == T[j]:
				c = counter[i][j] + 1
				counter[i+1][j+1] = c
				if c > longest:
					lcs_set = set()
					longest = c
					lcs_set.add(S[i-c+1:i+1])
				elif c == longest:
					lcs_set.add(S[i-c+1:i+1])
	lcs_set=list(lcs_set)
	if len(lcs_set)>0:
		lcs_abs=lcs_set[0]
	else:
		lcs_abs=""
		
	return lcs_abs

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#String with lists/sublists to list filled with integers

def str2list(l,dtype="int",openDelim="[",closeDelim="]",sep=","):

	#New list
	lnew=[]
	op=False
	j=0
	
	#Find sublists
	for i in range(len(l)):
		k=j+i
		x=l[k]
		
		if x==openDelim:
			
			if op==True:
				#If brackets are already open, recursively start new list
				lrec,jnew=str2list(l[k:],dtype=dtype)	
				
				#Increase j
				j=j+jnew
				
				#Append recursive result
				lnew.append(lrec)
			
			#Start new string
			s=""
			
			#Set open=True
			op=True
			
		elif x==closeDelim:
			#If brackets are closed, append and break
			lnew=appDtype(lnew,s,dtype=dtype)
			op=False
			break
		elif x==sep:
			
			#Append and convert new string
			if len(s)>0:
				lnew=appDtype(lnew,s,dtype=dtype)
				s=""
		else:
			s=s+x
	
	return lnew,i

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Append to list and convert to right dtype
				
def appDtype(l,s,dtype='int'):
	if s!="":
		if dtype=="int":
			l.append(int(s))
		elif dtype=="float":
			l.append(float(s))
		elif dtype=="str":
			l.append(str(s))
		else:
			printWarning("Not understanding dtype = "+ dtype)
		
	return l	
		
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Returns complimentary values of two lists

def complValsSimple(l1,l2):
	
	l=[]
	for i in l1:
		if i not in l2:
			l.append(i)
	
	return l

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Returns complimentary values of two lists, faster version

def complValsFast(l1,l2):
	
	matches=matchVals(l1,l2)
	
	for m in matches:
		l1=removeAllOccFromList(l1,m)
	
	return l1

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Returns complimentary values of two lists, faster version

def removeAllOccFromList(l, val):
	return [value for value in l if value != val]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Returns matching values of two lists

def matchVals(l1,l2):

	l1=list(l1)
	l2=list(l2)
	
	return list(set(l1).intersection(l2))


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Builds dict of list of variables (only works if vars are in locals())

def vars2dict(var,loc):	
	
	dic={}
	for name in var:
		dic[name]=loc[name]
		
	return {name: loc[name] for name, val in var.iteritems()}
	
	return dic
	
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Build string with variable name and its value from dict

def dict2string(dic,sep="=",newline=False):
	
	s=""
	
	for i,v in enumerate(dic):
		s=s+v+" "+sep+" "+ str(dic[v])
		if newline:
			if i<len(dic)-1:
				s=s+"\n"
			
	return s		
		
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Fixes file name 

def fix_fn_digits(fn,ndigits=3,op="lin",mode='auto',debug=False):
	
	if debug:
		print "======= fix_fn_digits debugging output ======="
	
	#Check if path exists
	if os.path.isfile(fn):
		if debug:
			print fn + "already exists, not going to do anything."
		return fn		
	else:
		if debug:
			print fn + "does not exist."
		
		if mode!='auto':
			ans=raw_input("Do you want me to fix it? [Y/N]")
			if ans!="Y":
				return fn
		
		if debug:
			print "Will try to fix digits in "+ fn 
		
		#Grab filename and ending
		if op in ["lin","osx"]:
			s=fn.split("/")
		else:
			s.fn.split("\\")
		
		base="/".join(s[:-1])
		
		#Check if containing folder exists
		if not os.path.exists(base):
			if debug:
				print "Folder ", base, " does not exist, going to return original filename!"
			return fn
		
		#Grab filename
		s=s[-1]
		
		#Grab file extension
		s=s.split(".")
		ending=s[-1]
		
		#Grab name
		n=s[-2]
		
		#Find last digits in name
		b=range(-len(n),0)
		b.reverse()
		
		idx=find_int_str(n,idxvec=b)[0]
		
		#Grab String of integers
		if max(idx)==-1:
			intstr=n[min(idx):]
		else:
			intstr=n[min(idx):max(idx)]
		
		#Convert string to list 
		n=list(n)
		
		#Insert enough zeros into list n to match digits
		for i in range(ndigits-len(intstr)):
			n.insert(min(idx),'0')
		
		#Join to string again
		a="".join(n)
		
		#New filename
		fn_new=base+"/"+a+"."+ending	
		
		#Check if new file actually exists
		if os.path.isfile(fn_new):
			print "Successfully fixed filename to ", fn_new, " !"
			return fn_new
		else:
			if debug:
				print "Fixed filename ", fn_new, "does not exist either, going to return original filename!"
			return fn
						
		
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Finds integers in str

def find_int_str(s,idxvec=[],debug=False):			
	
	if idxvec==[]:
		idxvec=range(len(s))
	
	idxs=[]
	found=False
	idx=[]
	for i in idxvec:
		try:
			int(s[i])
			idx.append(i)	
			found=True
		except ValueError:
			if found:
				idxs.append(idx)
				
			found=False
			idx=[]
		
	if found:
		idxs.append(idx)
		
		
	return idxs	

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Finds date in str

def find_date_str(s,sep='',lendate=8,yearreq='',monthreq='',debug=False):
	
	idxs=find_int_str(s)
	
	for i,idx in enumerate(idxs):
		d=""
		f=False
		if len(sep)>0:
			if i+2<=len(idxs)-1:
				if len_range(idx)+len_range(idxs[i+1])+len_range(idxs[i+2])+3==lendate:
					if s[max(idx):min(idxs[i+1])]==sep and s[max(idx):min(idxs[i+1])]==sep:
						lmin,lmax=range_lists([idx,idxs[i+1],idxs[i+2]])
						f=True
		else:
			if len_range(idx)+1==lendate:
				lmin,lmax=range_lists([idx])
				f=True
		if f:		
			if lmax+1==len(s):
				d=s[lmin:]
			else:
				d=s[lmin:lmax+1]
				
			if yearreq in d and monthreq in d:
				
				return d		
	return ""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Return the range of values in list
	
def len_range(l):
	return abs(max(l)-min(l))

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Return the range of values in list of lists

def range_lists(ls):
	lnew=[]
	for l in ls:
		lnew=lnew+l
		
	return min(lnew),max(lnew)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Finds file

def find_fn(fn,base,lvls_up=3,folder=False,debug=False):
	
	cwd=os.getcwd()
	
	os.chdir(base)
		
	for i in range(lvls_up):
		os.chdir('../')
	
	fn_found=""

	for f in os.walk(os.getcwd()):
		f=list(f)
		for k in f:
			if fn in k:
				f.remove([])
				fn_found="".join(f[:-1])+"/"+fn
				if folder:
					if os.path.isdir(fn_found):
						os.chdir(cwd)
						return fn_found
				else:	
					os.chdir(cwd)
					return fn_found
	
	os.chdir(cwd)
	
	if debug:
		print "======= find_folder debugging output ======="
		print "Could not find file ", fn ," . Going to return False"
		print "Closest path found:", fn_found
		
	return False
	
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Finds preiamge

def find_preimage(key,base,lvls_up=1,f_type='tif',debug=False):
	
	#find folder
	folder_pre=find_fn('pre',base,lvls_up=lvls_up,folder=True,debug=debug)

	if debug:
		print "======= find_preimage debugging output ======="
	
	if not folder_pre:
		if debug:
			print "Could not find prefolder with key = ", key ," . Going to return False"
		return folder_pre
	else:
		files=get_sorted_folder_list(folder_pre,f_type)
		if len(files)==0:
			if debug:
				print "Prefolder with key = ", key ," seems to be empty. Going to return False"
			return False
		else:
			print "Found preimage = ", folder_pre+"/"+files[0],  " ."
			return folder_pre+"/"+files[0]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Updates object with respect to blank object		
		
def updateObj(obj_blank,obj,debug=False):
	
	if debug:
		print "======update_obj: updated properties======"
	
	#Going through all attributes blank object
	for item in vars(obj_blank):
		
		if not hasattr(obj,str(item)):
			setattr(obj, str(item), vars(obj_blank)[str(item)])
			
			if debug:
				print item, " = ", vars(self)[str(item)]
	
	return obj	

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Remove multiple entries from list	
		
def remRepeatsList(l,debug=False):
	
	
	
	return list(set(l))
	 
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#unzips into two different lists	
		
def unzipLists(l):
	
	"""Unzips two zipped lists into seperate lists.
	
	Args:
		l (list): Zipped lists
		
	Returns:
		{
		list: Unzipped list 1.
		list: Unzipped list 2.
		}
	"""
	
	l1,l2=zip(*l)
	return list(l1),list(l2)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Assigns value if not value	
		
def assignIfVal(var,val,valCheck):
	
	"""Assigns val to var if var==valCheck.

	Args:
		var (var): Variable 
		val(any): Value to be assigned
		valCheck(any): Value to be checked for
		
	"""
	
	if var==valCheck:
		return val
	else:
		return var

def enumeratedName(baseName,listOfNames,sep="_"):
	
	"""Generates a new name given a list of names.
	Example:
	>>> baseName=embryo
	>>> listOfNames=[embryo_1,embryo_5]
	>>> enumeratedName(baseNamem,listOfNames)
	"embryo_6"
	
	Args:
		baseName (str): basename used for naming
		listOfNames(list): List of names
	
	Keyword Args:
		sep (str): Seperator between basename and number
	
	Returns:
		str: New name that has not been used yet
	"""
	
	numbers=[]
	for name in listOfNames:
		if baseName in name and sep in name:
			splittedName=name.strip(baseName).split(sep)
			try:
				numbers.append(int(splittedName[-1]))
			except ValueError:
				pass
	
	if len(numbers)>0:
		newNumber=str(max(numbers)+1)
	else:
		newNumber=str(0)
	
	return baseName+sep+newNumber

def objAttrToList(listOfObjects,AttributeName):
	
	"""Extracts a single object attribute from a list of
	objects and saves it into list.
	
	Args:
		listOfObjects (list): List of objects that all possess the same attribute
		AttributeName (str): Name of attribute to be appended
		
	Returns:
		list: List containing value of attribute of all objects
	"""
	
	l=[]
	for obj in listOfObjects:
		l.append(vars(obj)[str(AttributeName)])
		
	return l
	
def slashToFn(fn):
	
	"""Append / or \\ to filepath if necessary
	
	Args:
		fn (str): Filepath 
		
	Returns:
		str: Filepath
	"""
	
	if platform.system() in ["Windows"]:
		s="\\"
	else:
		s="/"
		
	if fn[-1]!=s:
		fn=fn+s
	return fn

def sortListsWithKey(l,keyList):
	
	"""Sorts two lists according to key list.
	
	Example:
	>>>l=[1,3,5]
	>>>keyList=[2,5,1]
	
	would result in 
	
	>>>[5,1,3],[1,2,5]
	
	Args:
		l (list): list to be sorted.
		keyList (list): list after which is being sorted.
		
	Returns:
		{
		list: Sorted list
		list: Sorted keys
		}
	"""
	
	s=sorted(zip(keyList, l), key=lambda keyList:keyList[0])
	
	sortedKeys=[]
	sortedList=[]
	
	for i in range(len(s)):
		sortedKeys.append(s[i][0])
		sortedList.append(s[i][1])
		
	return sortedList,sortedKeys
		
def compareObjAttr(obj1,obj2):
	
	"""Compare the values of two objects.
	
	Args:
		obj1 (object): First object.
		object2 (object): Second object.
		
	Returns:
		{
		dict: Dictionary of attributes with same values
		dict: Dictionary of attributes with different values
		dict: Dictionary of attributes that are not in both objects
		}

	"""
	
	same={}
	different={}
	notInBoth={}
	
	for item in vars(obj1):
		if item in vars(obj2):
			if vars(obj1)[str(item)]==vars(obj2)[str(item)]:
				same[str(item)]=[vars(obj1)[str(item)],vars(obj2)[str(item)]]
			else:
				different[str(item)]=[vars(obj1)[str(item)],vars(obj2)[str(item)]]
		else:
			notInBoth[str(item)]=1
	
	for item in vars(obj2):
		if item not in vars(obj1):
			notInBoth[str(item)]=2
			
	return same,different,notInBoth

def simpleHist(x,y,bins):

	"""Performs a simple histogram onto x-array.
	
	Args:
		x (numpy.array): x coordinates of data
		y (numpy.array): y coordinates of data
		bins (int):  number of bins
	
	Returns:
		{
		np.array: Center of bins
		np.array: Bin Values
		}

	"""
	

	xBin=np.linspace(min(x),max(x),bins+1)
			
	iLast=0
	j=1
	
	yBin=[]
	
	for i,xv in enumerate(x):
		try:
			if xv>=xBin[j]:
				yBin.append(np.mean(y[iLast:i]))
				iLast=i
				j=j+1
		except IndexError:
			pass
		
	xBin=np.diff(xBin)+xBin[:-1]
	
	return xBin,np.asarray(yBin)
	
def getMeshfilesDir():
	modulePath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	path=modulePath.replace("modules","meshfiles")+"/"
	return path

def getSubclassesDir():
	modulePath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	path=modulePath.replace("modules","subclasses")+"/"
	return path

def getGUIDir():
	modulePath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	path=modulePath.replace("modules","GUI")+"/"
	return path

def getConfDir():
	modulePath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	path=modulePath.replace("modules","configurations")+"/"
	return path

def getModulesDir():
	modulePath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	return modulePath+"/"

def getMacroDir():
	return getConfDir()+'macros/'

def getPathFile():
	return getConfDir()+'paths'

def getFijiBin(fnPath=None):
	return getPath('fijiBin',fnPath=fnPath)

def checkIfGmshBin(fn):
	return not os.system(fn + '-1')
	
def getPath(identifier,fnPath=None,defaultOutput=""):
	
	"""Extracts path with identifier from path definition file.
	
	If not defined diferently, will first look in configurations/paths,
	then configurations/paths.default.
	
	Args:
		identifier (str): Identifier of path
		
	Keyword Args:
		fnPath (str): Path to path definition file
			
	Returns:
		str: Path

	"""
	
	if fnPath==None:
		fnPath=getPathFile()
	else:
		if not os.path.isfile(fnPath):
			printWarning(fnPath+" does not exist. Will continue with paths defined in default paths files.")
			fnPath=getPathFile()
		
	path=None
	
	with  open (fnPath,'rb') as f:
		for line in f:
			if line.strip().startswith(identifier):
				ident,path=line.split('=')
				path=path.strip()
				break
		
	if path==None:
		printWarning("There is no line starting with ", identifier+"= in ", fnPath, ".")
		fnPath=getPathFile()+'.default'
		path=getPath(identifier,fnPath=fnPath)
		
	path=os.path.expanduser(path)
	
	return path
	
def buildEmbryoWizard(fn,ftype,name,nChannel=1,fnDest=None,createEmbryo=True):
	
	"""Creates embryo object ready for analysis from microscope data.
	
	(1) Extracts microscope data into .tif files
	(2) Builds folder structure
	(3) Moves image files in proper folders
	(4) Creates embryo object and automatically sets filepaths properly
	
	Args:
		fn (str): Path to embryo folder
		ftype (str): Type of microscopy file, such as lsm or czi
		name (str): Name of embryo
	
	Keyword Args:
		nChannel (int): Defines which channel of the images contains relevant data
		fnDest (str): Path of embryo data structure
		createEmbryo (boo): Flag if embryo object should be created
		
	Returns:
		pyfrp.subclasses.pyfrp_embryo.embryo: Created Embryo in case of success, otherwise -1

	"""
	
	fn=slashToFn(fn)
	
	if not os.path.isdir(fn):
		printError(fn+ " does not exist.")
		return -1
	
	l=getSortedFileList(fn,ftype)
	if len(l)==0:
		printError(fn+ "does not contain images of type ", ftype)
		return -1
	
	r=pyfrp_img_module.extractMicroscope(fn,ftype)
	
	if r==-1:
		return -1
	
	if fnDest==None:
		fnDest=fn
	
	fnDest=slashToFn(fnDest)
	
	makeEmbryoFolderStruct(fnDest)
	sortImageFiles(fn,fnDest,ftype,nChannel=nChannel)
	
	if createEmbryo:
		from pyfrp.subclasses import pyfrp_embryo
		
		emb=pyfrp_embryo.embryo(name)
		emb.setDataFolder(fnDest+'recover')
		a=emb.newAnalysis()
		a.setFnPre(fnDest+'pre')
		
		return emb
	else:
		return 1
	
def sortImageFiles(fn,fnDest,ftype,recoverIdent=['recover','post'],bleachIdent=['bleach'],preIdent=['pre'],nChannel=1,debug=False,colorPrefix='_c00'):
	
	"""Sorts all image data in fn into the respective folders of embryo project.
	
	Args:
		fn (str): Path to folder containing images
		fnDest (str): Path of embryo project.
		ftype (str): Type of microscopy file, such as lsm or czi

	Keyword Args:
		recoverIdent (list): List of identifiers for recovery data
		bleachIdent (list): List of identifiers for bleach data
		preIdent (list): List of identifiers for pre-bleach data
		nChannel (int): Defines which channel of the images contains relevant data
		debug (bool): Debugging flag
		colorPrefix (str): Defines how to detect if multichannel or not
		
	Returns:
		int: 0

	"""
	
	recoverMulti,preMulti,bleachMulti=checkDataMultiChannel(fn,recoverIdent=recoverIdent,bleachIdent=bleachIdent,preIdent=preIdent,colorPrefix=colorPrefix)
	
	moveImageFiles(fn,'recover','tif',recoverIdent,recoverMulti,fnDest=fnDest,debug=debug,colorPrefix=colorPrefix)
	moveImageFiles(fn,'pre','tif',preIdent,preMulti,fnDest=fnDest,debug=debug,colorPrefix=colorPrefix)
	moveImageFiles(fn,'bleach','tif',bleachIdent,bleachMulti,fnDest=fnDest,debug=debug,colorPrefix=colorPrefix)
	moveImageFiles(fn,'lsm','lsm',[""],False,fnDest=fnDest,debug=debug,colorPrefix=colorPrefix)
	
	return 
	
def moveImageFiles(fn,fnTarget,ftype,ident,isMulti,fnDest=None,debug=False,colorPrefix='_c00',nChannel=1):
	
	"""Moves all image files fullfilling *ident*(isMulti*colorPrefix)* to fnDest+fnTarget.
	
	Args:
		fn (str): Path to folder containing images
		fnTarget (str): Name of folder files should go in, for example "recover"
		ftype (str): Type of file, for example "tif"
		indent (list): List of identifiers, for example ["recover","post"]
		isMulti (bool): Flag if images are multichannel or not

	Keyword Args:
		fnDest (str): Path containing fnTarget
		debug (bool): Debugging flag
		colorPrefix (str): Defines how to detect if multichannel or not
		nChannel (int): Defines which channel of the images contains relevant data
		
	Returns:
		int: Returns 0 if success, -1 if error

	"""
	
	if fnDest==None:
		fnDest=fn
	
	debugFlag=debug*' -v '
	r=0
	for ind in ident:
		try:
			colorFlag=isMulti*('*'+colorPrefix+str(nChannel))
			cmd='mv '+debugFlag+fn+'*'+ind+colorFlag+'*.'+ftype +' ' + fnDest + fnTarget+'/'
			os.system(cmd)
			r=1
		except:
			printError("Something went wrong executing:" )
			print cmd
			r=0
	
	return r
	
def checkDataMultiChannel(fn,recoverIdent=['recover','post'],bleachIdent=['bleach'],preIdent=['pre'],colorPrefix='_c00'):
	
	"""Checks if extracted bleach/pre/recover microscopy data are multichannel.
	
	Args:
		fn (str): Path to folder containing images

	Keyword Args:
		recoverIdent (list): List of identifiers for recovery data
		bleachIdent (list): List of identifiers for bleach data
		preIdent (list): List of identifiers for pre-bleach data
		colorPrefix (str): Defines how to detect if multichannel or not
				
	Returns:
		{
		bool: True if recover is multichannel
		bool: True if pre is multichannel
		bool: True if bleach is multichannel
		}
	"""
	
	l=getSortedFileList(fn,'.tif')
	
	recoverMulti=checkMultiChannel(fn,recoverIdent,colorPrefix=colorPrefix)
	preMulti=checkMultiChannel(fn,preIdent,colorPrefix=colorPrefix)
	bleachMulti=checkMultiChannel(fn,bleachIdent,colorPrefix=colorPrefix)
	
	return recoverMulti,preMulti,bleachMulti
	
	

def checkMultiChannel(fn,ident,colorPrefix='_c00'):
	
	"""Checks if extracted microscopy with identifier are multichannel.
	
	Args:
		fn (str): Path to folder containing images
		indent (list): List of identifiers, for example ["recover","post"]
	
	Keyword Args:
		colorPrefix (str): Defines how to detect if multichannel or not
		
	Returns:
		bool: True if multichannel, False if not

	"""
	
	l=getSortedFileList(fn,'.tif')
	for f in l:
		for i in ident:
			if colorPrefix in f:
				return True
	return False		
			

def makeEmbryoFolderStruct(fn):
	
	"""Creates default folder structure for embryo object.
	
	fn
	|--recover
	|--pre
	|--bleach
	|--lsm
	|--meshfiles
	
	Args:
		fn (str): Path to embryo folder
			
	Returns:
		int: 0

	"""
	
	try:
		os.mkdir(fn)
	except OSError:
		pass
		
	try:
		os.mkdir(fn+"recover")
	except OSError:
		pass

	try:
		os.mkdir(fn+"pre")
	except OSError:
		pass
	
	try:
		os.mkdir(fn+"bleach")
	except OSError:
		pass
	
	try:
		os.mkdir(fn+"meshfiles")
	except OSError:
		pass
	
	try:
		os.mkdir(fn+"lsm")
	except OSError:
		pass
	
	
	return 0
	
def translateNPFloat(x):
	
	"""Translates string into numpy float.
	If string==+/-'inf', will return +/- numpy.inf,
	otherwise will leave x unchanged.
	
	This function is necessary to prevent Sphinx from
	not being able to import modules because np.inf is an 
	default value for an keyword arg, but numpy is mocked.
	
	Args:
		x (float): Input number/string.
			
	Returns:
		float: Translated float.

	"""
	
	return np.float(x)
		
	
	
	
	
	
