


import vtk
import thread
from threading import Thread
import datetime 

# visuablize
renderer = vtk.vtkRenderer()

def marching_filter(input,th1=0,th2=1000):
    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(input)
    surface.SetValue(th1,th2)
    surface.Update()
    # extract largest connectivity area
    confilter = vtk.vtkPolyDataConnectivityFilter()
    confilter.SetInputData(surface.GetOutput());
    confilter.SetExtractionModeToLargestRegion();
    confilter.Update()
    return confilter.GetOutput()

def create_actor(poly,opacity=1.0):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(opacity)
    return actor


nii_file = 'skull.nii'
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName(nii_file)
reader.Update()
img = reader.GetOutput()

poly = marching_filter(img,th1=-100)
actor1 = create_actor(poly,opacity=0.5)
renderer.AddActor(actor1)
bound = poly.GetBounds()
p1=bound[0:6:2]
p2=bound[1:6:2]
center = [(x1+x2)/2 for x1,x2 in zip(p1,p2)]
numP = poly.GetNumberOfPoints()
print 'Total number of points: {}'.format(numP)
id_list = range(numP)


# line source
def add_line(p1,p2):
    line = vtk.vtkLineSource()
    line.SetPoint1(p1)
    line.SetPoint2(p2)
    line.Update()
    return create_actor(line.GetOutput())

lineActor = add_line(p1,p2)
renderer.AddActor(lineActor)

def obbTree_search(tree,pSource,pTarget):
    pointsVTKintersection = vtk.vtkPoints()
    code = obbTree.IntersectWithLine(pSource, pTarget, pointsVTKintersection, None)
    return pointsVTKintersection

# obb tree
obbTree = vtk.vtkOBBTree()
obbTree.SetDataSet(poly)
obbTree.BuildLocator()

class thread_it(Thread):
    def __init__(self,obbTree,center,id_list,poly,reserve_list):
        Thread.__init__(self)
        self.obbTree = obbTree
        self.id_list = id_list
        self.poly = poly
        self.center = center
        self.reserve_list = reserve_list

    def run(self):
        for point_id in self.id_list:
            pp = poly.GetPoint(point_id)
            pts = obbTree_search(self.obbTree,self.center,pp)
            if pts.GetNumberOfPoints() > 0:
                self.reserve_list.append(point_id)
        print '{} Done'.format(self.id_list[0]/1000)
        
id_reserve = []



for idx in id_list:
    pp = poly.GetPoint(idx)
    pts = obbTree_search(obbTree,center,pp)
    if pts.GetNumberOfPoints() > 0:
        id_reserve.append(idx)
    if idx%200 == 0:
        print 'progress {}%'.format(float(idx)/float(numP)*100)
        print datetime.datetime.now()

points = vtk.vtkPoints()


for id in id_reserve:
    pt = poly.GetPoint(id)
    points.InsertNextPoint(pt)
    

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
    #actor.GetProperty().SetPointSize(10)
    return actor

renderer.AddActor(p2actor(points))


# view
win = vtk.vtkRenderWindow()
win.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(win)
interactor.Start()




