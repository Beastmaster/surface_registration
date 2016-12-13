'''
Author: QIN Shuo
Date: 2016/10/28
Description:
    file format and data format bridge
'''


import vtk
import string

def read_vtk_format(filename,type='point'):
    '''
    file: .vtk file or .stl
    type: 'point', 'poly'
    return: vtkPoints or vtkPolyData
    '''
    print 'Reading ',filename
    sufx = filename.split('.')[-1]
    if sufx == 'vtk':
        reader = vtk.vtkGenericDataObjectReader()
        reader.SetFileName(filename)
        reader.Update()
        geo = vtk.vtkGeometryFilter() # convert unstructed grid to a poly data, cannot write to stl now
        geo.SetInputData(reader.GetOutput())
        geo.Update()
        poly = geo.GetOutput()

        # important: convert point to triangle
        triangle = vtk.vtkTriangleFilter()
        triangle.SetInputData(poly)
        triangle.Update()
        poly = triangle.GetOutput()
        return poly
            
    elif sufx=='stl':
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        points = reader.GetOutput().GetPoints()
        poly = reader.GetOutput()
    else:
        raise ValueError('Support stl file only...')

    if type=='point':
        return points
    elif type=='poly':
        return poly
    else:
        raise ValueError('Invalid output type')


def read_txt_points(filename):
    '''
    private function to read points from a file
    return a point list
    '''
    print 'Reading file: ',filename 
    points = []
    vtkpt = vtk.vtkPoints()
    with open(filename,'r') as ff:
        for line in ff.readlines():
            ss  = line.strip().split(',')
            if len(ss) == 3:
               pp = [string.atof(ss[0]) ,string.atof(ss[1]),string.atof(ss[2])]
               points.append(pp)
               vtkpt.InsertNextPoint(pp)
    poly = vtk.vtkPolyData()
    poly.SetPoints(vtkpt)
    vx = vtk.vtkVertexGlyphFilter()
    vx.SetInputData(poly)
    vx.Update()
    poly = vx.GetOutput()
    return poly


def write_points(points,filename,type='pcd'):
    '''
    input a coordinate list: [[x,y,z],...[xn,yn,zn]]
    '''
    print 'Writing file: ',filename
    with open(filename,'w') as ff:
        if filename.split('.')[-1]=='pcd': # writing pcd file head
            ff.write('# .PCD v0.7 - Point Cloud Data file format\n')
            ff.write('VERSION 0.7\n')
            ff.write('FIELDS x y z\n')
            ff.write('SIZE 4 4 4\n') # if double: 8
            ff.write('TYPE F F F\n')
            ff.write('COUNT 1 1 1\n')
            width = 'WIDTH '+str(len(points))+'\n'
            ff.write(width)
            ff.write('HEIGHT 1\n')
            ff.write('VIEWPOINT 0 0 0 1 0 0 0\n')
            num_pt = 'POINTS '+str(len(points))+'\n' # number of points
            ff.write(num_pt)
            ff.write('DATA ascii\n')
        for pt in points:
            ss = '{0[0]}, {0[1]}, {0[2]}'.format(pt)
            ff.write(ss+'\n') 

def write_poly(poly,filename):
    '''
    input: vtkPolyData
    '''
    print 'Wrting poly file: ',filename
    type = filename.split('.')[-1]
    if type == 'stl':
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(filename)
        writer.SetInputData(poly)
        writer.Update()
    elif type == 'pcd':
        raise ValueError('Not implemented')
    else:
        raise ValueError('type error')

    







