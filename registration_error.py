'''
Author: QIN Shuo
Date: 2016/11/23
Description:
    Calculate the distance between points and surface

'''


import vtk
import numpy as np

import sys

def registration_error(points,surface):
    '''
    Input: points and surface are all vtkPolyData
    Workflow:
        1. construct a kd-tree from surface
        2. iterate points to find nearst points
    '''
    kdTree = vtk.vtkKdTree()
    kdTree.BuildLocatorFromPoints(surface.GetPoints())

    num_points = points.GetNumberOfPoints()
    dist = np.zeros(num_points)

    for i in range(num_points):
        print 'progress: %4f%%' % (float(i)*100/float(num_points))
        closestPointDist = vtk.mutable(0.0)
        closestPointID = 0
        testPoint = points.GetPoint(i)
        closestPointID = kdTree.FindClosestPoint(testPoint,closestPointDist)
        dist[i] = closestPointDist
    return dist

def report_error(dist,report = 'data/error_report.txt'):
    '''
    input a 1d array
    '''
    max_ = max(dist)
    min_ = min(dist)
    mean_ = np.mean(dist)
    square_mean_ = np.mean(np.power(dist,2))
    variance_ = np.var(dist)

    with open(report,'w+') as ff:
        ff.write('Distance error report: \n')
        ff.write('Point-Surface distacne:\n'+np.array_str(dist)+'\n')
        ff.write('Max error: '+ str(max_) + '\n')
        ff.write('Min error: '+str(min_)+ '\n')
        ff.write('Mean error:'+str(mean_)+ '\n')
        ff.write('Square_mean error: ' + str(square_mean_)+'\n')
        ff.write('Variance: '+ str(variance_))

if __name__ == '__main__':
    if len(sys.argv)<3:
        print "Para1: stl surface file"
        print "Para2: point file"
        raise ValueError('No enouth inputs..')
    
    from read_format import read_txt_points
    from read_format import read_vtk_format
    surface = read_vtk_format(sys.argv[1],type = 'poly')
    points = read_txt_points(sys.argv[2])

    dist = registration_error(points,surface)
    report_error(dist)

        


