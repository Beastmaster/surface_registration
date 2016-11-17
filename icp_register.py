'''
Author: QIN Shuo
Date: 2016/10/26
Description:
    run ICP algorithm
'''
import sys
import string
import numpy as np

import vtk
from read_format import read_txt_points
from read_format import read_vtk_format

class icp_register:
    def __init__(self):
        print "Class: icp_register"
        pass
    
    def register(self,src,target,iter=100):
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(src)
        icp.SetTarget(target)
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.SetMaximumNumberOfIterations(iter)
        #icp.StartByMatchingCentroidsOn()
        icp.Modified()
        icp.Update()
        return icp.GetMatrix() 
        
    def _view(self,poly):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1,0,0)
        actor.GetProperty().SetPointSize(10)
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        win = vtk.vtkRenderWindow()
        win.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(win)
        win.Render()
        interactor.Start()

    def _write_poly(self,poly,name='data/tcut.stl'):
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(name)
        writer.SetInputData(poly)
        #writer.SetFileTypeToBinary()
        writer.Update()
    def _read_poly(self,name='data/cut.stl'):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(name)
        reader.Update()
        return reader.GetOutput()
        

    def change_file_format(self,file,out_format=''):
        #reader = vtk.vtkGenericDataObjectReader()
        reader = vtk.vtkUnstructuredGridReader()
        #reader = vtk.vtkSTLReader()
        #reader = vtk.vtkDataSetReader()
        reader.SetFileName(file)
        reader.Update()
        points = reader.GetOutput()
        geo = vtk.vtkGeometryFilter() # convert unstructed grid to a poly data, cannot write to stl now
        geo.SetInputData(points)
        geo.Update()
        poly = geo.GetOutput()

        # important: convert point to triangle
        triangle = vtk.vtkTriangleFilter()
        triangle.SetInputData(poly)
        triangle.Update()
        poly = triangle.GetOutput()

        new_file = file.split('.')
        new_file[-1]='stl'
        new_file = '.'.join(new_file)
        self._write_poly(poly,new_file)


    def transform_poly(self,poly,save=True):
        transform = vtk.vtkTransform()
        transform.RotateX(90)
        transform.Translate(10,-10,10)
        mat = transform.GetMatrix()

        transFilter = vtk.vtkTransformFilter()
        transFilter.SetTransform(transform)
        transFilter.SetInputData(poly)
        transFilter.Update()
        print "Transform done !"
        print mat
        return transFilter.GetOutput()

def landmark_registration(src,tgt):
    '''
    src: moving points
    tgt: fix points
    '''
    reg = vtk.vtkLandmarkTransform()
    reg.SetSourceLandmarks(src.GetPoints())
    reg.SetTargetLandmarks(tgt.GetPoints())
    reg.SetModeToRigidBody()
    reg.Update()

    return reg.GetMatrix()
    

def try_direct_surface_align():
    '''
    try surface registration with ICP, failed
    traped into local minimum
    '''
    alg = icp_register()
    poly_src = alg._read_poly('data/tcut.stl')
    poly_tgt = alg._read_poly('data/skull.stl')

    mat = alg.register(poly_src,poly_tgt,5000)
    transform = vtk.vtkTransform()
    transform.SetMatrix(mat)
    
    transFilter = vtk.vtkTransformFilter()
    transFilter.SetTransform(transform)
    transFilter.SetInputData(poly_src)
    transFilter.Update()
    print "Transform done !"
    print mat
    
    poly_tt = transFilter.GetOutput()
    alg._write_poly(poly_tt,'data/transed.stl')



def try_point_surface():
    '''
    Workflow proved valid:

    src_surface: source surface to be moved
    src_points:  points selected from src_surface
    tgt_surface: fixed surface, src_surface will transform to this
    moved_surface: src_surface applied transform

    Workflow:
        register src_points to tgt_surface, get a matrix Mat
        apply Mat to src_surface, get moved_surface

    Result:
        moved_surface apply perfectly to tgt_surface
    '''
    pt_list = read_txt('data/point.txt')
    points = vtk.vtkPoints()
    for pt in pt_list:
        points.InsertNextPoint(pt)
    
    # points as source 
    point_poly = vtk.vtkPolyData()
    point_poly.SetPoints(points)
    vertex = vtk.vtkVertexGlyphFilter()
    vertex.SetInputData(point_poly)
    vertex.Update()
    point_poly = vertex.GetOutput()

    # surface patch as target
    reg = icp_register()
    surface = reg._read_poly('data/tcut.stl')
    src_surface = reg._read_poly('data/cut.stl')

    mat = reg.register(point_poly,surface,5000)

    transform = vtk.vtkTransform()
    transform.SetMatrix(mat)
    transFilter = vtk.vtkTransformFilter()
    transFilter.SetTransform(transform)
    #transFilter.SetInputData(point_poly)
    transFilter.SetInputData(src_surface)
    transFilter.Update()
    pp = transFilter.GetOutput()
    
    reg._write_poly(src_surface,'data/src_tr.stl')
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(pp)
    writer.SetFileName('data/transed_P.vtp')
    #writer.Write()

def try_landmark_registration():
    f_fix = 'data/fix_small_points.txt'
    f_mov = 'data/moving_small_points.txt'
    p_fix = read_txt_points(f_fix)
    p_mov = read_txt_points(f_mov)

    mat = landmark_registration(p_mov,p_fix)
    transform = vtk.vtkTransform()
    transform.SetMatrix(mat)
    
    def temp_read(name):
        reader1 = vtk.vtkSTLReader()
        reader1.SetFileName(name)
        reader1.Update()
        poly_fix = reader1.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_fix)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor

    fix_actor = temp_read('data/fix_skull.stl')
    mov_actor = temp_read('data/moving_skull.stl')
    mov_actor.SetUserTransform(transform)

    renderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.Render()
    interactor = renWin.GetInteractor()
    interactor.Start()

    pass



def try_2step_registration():
    '''
    2 step registration:
        1. Select some points in the surface
        2. Shift points randomly ###
        3. Select rough corresponding points
        4. Register roughly get reg matrix 1 (landmark transform proved to be efficient)
        5. Move, run register, get reg matrix 2
        6. multiply 2 matrix
        7. 
    '''
    # reg1
    rough_mv_points = read_txt_points('data/moving_small_points.txt')
    rough_fix_points = read_txt_points('data/fix_small_points.txt')


    icp = icp_register()
    mat1 = landmark_registration(rough_mv_points,rough_fix_points)
    #mat1.SetElement(0,3,0.1)
    #mat1.SetElement(0,3,0.1)
    #mat1.SetElement(0,3,0.1)
    print 'Mat1 :\n',mat1
    
    transform = vtk.vtkTransform()
    transform.SetMatrix(mat1)
    trans_filter = vtk.vtkTransformFilter()
    trans_filter.SetTransform(transform)
    trans_filter.SetInputData(rough_mv_points)
    trans_filter.Update()
    new_rough_pt = trans_filter.GetOutput()


    # transform with reg1
    fine_points = read_txt_points('data/large_points.txt')
    print fine_points.GetNumberOfPoints()

    transform = vtk.vtkTransform()
    transform.SetMatrix(mat1)
    trans_filter = vtk.vtkTransformFilter()
    trans_filter.SetTransform(transform)
    trans_filter.SetInputData(fine_points)
    trans_filter.Update()
    new_fine_pt = trans_filter.GetOutput()
    bound = new_fine_pt.GetBounds()

    # reg2
    fix_skull = read_vtk_format('data/fix_skull.stl',type='poly')
    def clip_area(poly,bounds):
        new_pts = vtk.vtkPoints()
        for id in range(poly.GetNumberOfPoints()):
            pt = poly.GetPoint(id)
            if ((pt[0]>bounds[0]-10) & 
                (pt[0]<bounds[1]+10) &
                (pt[1]>bounds[2]-10) &
                (pt[1]<bounds[3]+10) &
                (pt[2]>bounds[4]-10) &
                (pt[2]<bounds[5]+10) ):
                new_pts.InsertNextPoint(pt)
        poly = vtk.vtkPolyData()
        poly.SetPoints(new_pts)
        vx = vtk.vtkVertexGlyphFilter()
        vx.SetInputData(poly)
        vx.Update()
        new_pts = vx.GetOutput()
        return new_pts
    fix_skull_part = clip_area(fix_skull,bound)


    mat2 = icp.register(new_fine_pt,fix_skull_part)
    print 'Mat2: \n',mat2

    # final matrix
    mat_final = vtk.vtkMatrix4x4()
    ##### This is the key line!! ######
    vtk.vtkMatrix4x4.Multiply4x4(mat2,mat1,mat_final)
    ###################################
    print 'Mat final:\n',mat_final
    # transform points here
    fin_transform = vtk.vtkTransform()
    fin_transform.SetMatrix(mat_final)
    trans_filter = vtk.vtkTransformFilter()
    trans_filter.SetTransform(fin_transform)
    trans_filter.SetInputData(fine_points)
    trans_filter.Update()
    final_fine_pt = trans_filter.GetOutput()

    # visualization
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
        actor.GetProperty().SetColor(np.random.rand(1)[0],
                                     np.random.rand(1)[0],
                                     np.random.rand(1)[0])
        return actor
    def create_actor(poly):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(10)
        actor.GetProperty().SetColor(np.random.rand(1)[0],
                                     np.random.rand(1)[0],
                                     np.random.rand(1)[0])
        return actor
    
    renderer = vtk.vtkRenderer()
    renderer.AddActor(create_actor(fine_points))
    renderer.AddActor(create_actor(new_fine_pt))
    renderer.AddActor(create_actor(final_fine_pt))  
    ac = create_actor(fix_skull)
    ac.GetProperty().SetColor(0.5,0.5,0.5)
    ac.GetProperty().SetOpacity(0.9)
    renderer.AddActor(ac)
    #renderer.AddActor(create_actor(read_vtk_format('data/moving_skull.stl',type='poly')))

    win = vtk.vtkRenderWindow()
    win.AddRenderer(renderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(win)
    win.Render()
    interactor.Start()


    pass



if __name__ == '__main__':
    
    #icp = icp_register()
    #icp.change_file_format('data/cut.vtk')
    # stl = icp._read_poly('data/moving_skull.stl')
    # stl2 = icp.transform_poly(stl)
    # icp._write_poly(stl2,name='data/tskull.stl')
    #try_2step_registration()
    try_landmark_registration()

'''
    1 0 0 0 
    0 2.22045e-16 -1 0 
    0 1 2.22045e-16 0 
    0 0 0 1 
'''