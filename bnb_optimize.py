'''
Author: QIN Shuo
Date: 2016/11/9
Description:
    Running Branch and bound registration to avoid local minimum

'''



import sys
import string
import vtk
import numpy as np

# basic functions
import icp_register
import extract_surface



class bnb_optimization:
    def __init__(self):
        pass

    def set_fix(self,poly):
        self.m_fix_ply = poly
        # get a pointset
        self.m_pointset = poly.GetPoints()

    def partition_volume(self,parts = 8):
        bound = self.m_pointset.GetBounds()
        print bound

        # partition area
        pointset_part = []
        for i in range(parts):
            temp = vtk.vtkPoints()
            pointset_part.append(temp)

        for pt_id in range(self.m_pointset.GetNumberOfPoints() ):
            pt = self.m_pointset.GetPoint(pt_id)
            idx = 0
            if pt[0]>(bound[0]+bound[1])/2:
                idx = idx + 1
            if pt[1]>(bound[2]+bound[3])/2:
                idx = idx + 2
            if pt[2]>(bound[4]+bound[5])/2:
                idx = idx + 4 

            pointset_part[idx].InsertNextPoint(pt)
            self.m_pointset_part = []
            for sub_set in pointset_part:  # exclude empty pointset
                if sub_set.GetNumberOfPoints()>=1:
                    self.m_pointset_part.append(sub_set)
        return self.m_pointset_part



if __name__ == '__main__':
    
    poly_name = 'data/skull.stl'
    icp_reg = icp_register.icp_register()
    sfc = extract_surface.extract_surface()
    poly = icp_reg._read_poly(poly_name)

    bnb = bnb_optimization()
    bnb.set_fix(poly)
    sfc._view_points(bnb.partition_volume())
    
    pass


