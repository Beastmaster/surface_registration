'''
Author: QIN Shuo
Date: 2016/10/26
Description:
    load a .nii file
    use marchingcube to extract a surface
    save the surface to a file 
    extract a set of points
    shift points randomly
'''

import read_format
import vtk
import numpy as np
import string
import sys

class extract_surface:
    '''
    operations:
    1. extract a countour, shift points randomly, transform by a transform
    2. save to file
    3. run registration process, check the transform
    4. view: different color
    '''

    def __init__(self):
        print "Class: extract_surface"

    
    def _read_points(self,filename):
        '''
        private function to read points from a file
        return a point list
        '''
        points = []
        with open(filename,'r') as ff:
            for line in ff.readlines():
                ss  = line.strip().split(',')
                if len(ss) == 3:
                   pp = [string.atof(ss[0]) ,string.atof(ss[1]),string.atof(ss[2])]
                   points.append(pp)
        return points
    
    def _write_points(self,points,filename):
        '''
        private function to write points array to a file
        '''
        print "Saving file: ",filename
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
        print 'Saved!'

    def _view_points(self,pts_list):
        '''
        private function to check 2 sets of points in the same view
        '''
        def p2actor(pp):
            pPoly = vtk.vtkPolyData()
            pPoly.SetPoints(pp)
            vx = vtk.vtkVertexGlyphFilter()
            vx.SetInputData(pPoly)
            vx.Update()
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(vx.GetOutput())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetPointSize(10)
            return actor
        
        renderer = vtk.vtkRenderer()
        try:
            for pts in pts_list:
                actor1 = p2actor(pts)
                actor1.GetProperty().SetColor(np.random.rand(1)[0],
                                              np.random.rand(1)[0],
                                              np.random.rand(1)[0])
                renderer.AddActor(actor1)
        except:  # a set of points stored in a python list
            pts = vtk.vtkPoints()
            for pt in pts_list:
                pts.InsertNextPoint(pt)
            actor = p2actor(pts)
            actor1.GetProperty().SetColor(np.random.rand(1)[0],
                                          np.random.rand(1)[0],
                                          np.random.rand(1)[0])
            renderer.AddActor(actor1)
            
        win = vtk.vtkRenderWindow()
        win.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(win)
        win.Render()
        interactor.Start()

    def load_nii_save_stl(self,in_name='data/skull.nii',out_name='data/skull.stl',threshold = 100.0):
        print "Function: load_nii_save_stl"
        print "Para1: input file name (.nii file)\nPara2: output file name (.stl file)"
        
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(in_name)
        reader.Update()
        image = reader.GetOutput()

        surface = vtk.vtkMarchingCubes()
        surface.SetInputData(image)
        surface.SetValue(0,threshold)
        surface.Update()
        # extract largest connectivity area
        confilter = vtk.vtkPolyDataConnectivityFilter()
        confilter.SetInputData(surface.GetOutput());
        confilter.SetExtractionModeToLargestRegion();
        confilter.Update()

        skull = confilter.GetOutput()

        writer = vtk.vtkSTLWriter()
        writer.SetFileName(out_name)
        writer.SetInputData(skull)
        writer.Update()
        print out_name,'  saved!'   

    
    def shift_poly_stl(self,file_in = 'data/skull.stl',file_out = 'data/moving_skull.stl'):        
        print "Reading from ", file_in
        print "Writing to   ", file_out
        transform = vtk.vtkTransform()
        transform.Translate(10,9,7.5)
        transform.RotateWXYZ(30,1,1.0,1.0)
        
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_in)
        reader.Update()
        poly = reader.GetOutput()

        transFilter = vtk.vtkTransformFilter()
        transFilter.SetInputData(poly)
        transFilter.SetTransform(transform)
        transFilter.Update()

        writer = vtk.vtkSTLWriter()
        writer.SetFileName(file_out)
        writer.SetInputData(transFilter.GetOutput())
        writer.Update()

    def select_poly_points(self,stl_file='data/skull.stl',save_file='points.txt'):
        print "Function: extract_poly_line"
        print "Usage:\n\t\'h\': Capture point.\n\t\'s\': Write points to file"
        self.points = []

        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_file)
        reader.Update()

        poly = reader.GetOutput()
        #poly = vtk.vtkPolyData()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        win = vtk.vtkRenderWindow()
        win.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(win)
        
        def keyPressEvent(obj,event):
            key = obj.GetKeySym()
            #print key
            # translation
            if key == "h":
                #print "key is ",key
                coor = interactor.GetEventPosition()
                #print "click position is ", coor  # coordinate in 2d view
                point = interactor.GetPicker().GetSelectionPoint()
                #print "2d coordinate is", point    # coordinate in 2d view
                interactor.GetPicker().Pick(interactor.GetEventPosition()[0],interactor.GetEventPosition()[1],0,renderer)
                picked = interactor.GetPicker().GetPickPosition()
                #print "3d coordinate is ",picked  # this is the true 3d coordinate

                self.points.append(picked) # add point here
                #print self.points

                ptSrc = vtk.vtkPointSource()
                ptSrc.Update()
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(ptSrc.GetOutput())
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetPointSize(5)
                actor.GetProperty().SetColor(1,0,0)
                actor.SetPosition(picked)
                renderer.AddActor(actor)
                win.Render()
            elif key == "s": # save to file
                self._write_points(self.points,save_file)
            else:
                pass 
        interactor.AddObserver(vtk.vtkCommand.KeyPressEvent,keyPressEvent)
        win.Render()
        interactor.Start()

    def shift_points(self,points_file,out_file='',drift = 0.3):
        '''
        Input: points file Name
        
        input a point set, move each point randomly
        display 2 point set in different color
        '''
        print "Function: shift_points"
        print "Usage:\n\tInput point file\n\tdrift: Rrandom drift range."

        points = self._read_points(points_file)
        n_p = [] # shifted new points
        ran = lambda _ : (np.random.random()-0.5)*2*drift
        for pt in points:
            pp = [pt[0]+ran(0),pt[1]+ran(0),pt[2]+ran(0)]
            n_p.append(pp)
        self._write_points(n_p,out_file)
        self._view_points([points,n_p])


if __name__=='__main__':
    ext = extract_surface()
    if len(sys.argv)>1:
        stl_file = sys.argv[1]
        save_file = sys.argv[2]
        ext.select_poly_points(stl_file = stl_file,save_file=save_file)
    
    
    #ext.load_nii_save_stl()
    #ext.select_poly_points(stl_file='data/fix_skull.stl')
    #ext.shift_poly_stl(file_in = 'data/fix_skull.stl')
    else:
        ext.select_poly_points(stl_file = 'data/fix_skull.stl')

    #ext.extract_poly_line()
    #ext.shift_points('data/point.txt','data/point_shift.txt')