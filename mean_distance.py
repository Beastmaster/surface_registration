'''
Author: QIN Shuo
Date: 2016/11/15
Description:
    Find the least mean distacne between a point set and a surface

'''






import vtk
import numpy as np


class mean_distace():
    def __init__(self):
        self.m_kdTree = vtk.vtkKdTree()

    def setsourcepointSet(self,ptSet):
        '''
        Set a large set of points, target to be searched
        ptSet type is: vtkPoints
        '''
        self.m_srcSet = ptSet
        self.m_kdTree.BuildLocatorFromPoints(self.m_srcSet)
        

    def find_least_distance(self,pt):
        '''
        pt is python array length 3
        '''
        dist = 0.0
        self.m_kdTree.FindClosestPoint(pt,dist)
        return dist

    def find_mean_distance(self,pts):
        '''
        pts is a python array
        '''
        sum = 0.0
        for pt in pts:
            sum = sum+self.find_least_distance(pt)

        mean = sum/len(pts)
        return mean

    def find_mean_dist_pointSet(self,ptSet):
        '''
        ptSet is a vtkPointSet
        '''
        sum = 0.0
        total = ptSet.GetNumberOfPoints()
        for i in range(total):
            pt = ptSet.GetPoint(i)
            sum = sum + self.find_mean_distance(pt)
        mean = sum/total
        return mean


if __name__ == '__main__':
    pass