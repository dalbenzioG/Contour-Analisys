import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np
from numpy import random, size

colors = vtk.vtkNamedColors()


def CreatePolyDataFromCoords(x, y, z):
    data = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    points = vtk.vtkPoints()
    cells = vtk.vtkCellArray()
    polydata = vtk.vtkPolyData()

    for k in range(size(data, 0)):
        point = data[k]
        pointId = points.InsertNextPoint(point[:])
        cells.InsertNextCell(1)
        cells.InsertCellPoint(pointId)

    cells.Modified()
    points.Modified()
    polydata.SetPoints(points)
    polydata.SetVerts(cells)

    return polydata


if __name__ == "__main__":
    # get the data
    points_file = '/home/gabi/PycharmProjects/EFA_interopaltion_approximation/test_data/contour12.vtk'
    contour_reader = vtk.vtkPolyDataReader()
    contour_reader.SetFileName(points_file)
    contour_reader.Update()
    contour = contour_reader.GetOutput()
    contour_points = contour_reader.GetOutput().GetPoints().GetData()
    contour_array = vtk_to_numpy(contour_points)

    points = contour.GetPoints()
    xSpline = vtk.vtkKochanekSpline()
    ySpline = vtk.vtkKochanekSpline()
    zSpline = vtk.vtkKochanekSpline()

    spline = vtk.vtkParametricSpline()
    spline.SetXSpline(xSpline)
    spline.SetYSpline(ySpline)
    spline.SetZSpline(zSpline)
    spline.ClosedOn()
    spline.SetPoints(points)

    functionSource = vtk.vtkParametricFunctionSource()
    functionSource.SetParametricFunction(spline)
    functionSource.Update()

    # masks = vtk.vtkMaskPoints()
    # masks.SetInputData(contour)
    # masks.SingleVertexPerCellOn()
    # masks.GenerateVerticesOn()
    # masks.SetOnRatio(1)
    # # masks.SetMaximumNumberOfPoints(splineInterp.GetNumberOfPoints())
    # masks.Update()
    #
    # smoother = vtk.vtkAdaptiveSubdivisionFilter()
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputData(functionSource.GetOutput())
    smoother.SetNumberOfIterations(60)
    smoother.SetPassBand(0.01)
    smoother.NonManifoldSmoothingOn()
    smoother.BoundarySmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.GenerateErrorScalarsOn()
    smoother.GenerateErrorVectorsOn()
    smoother.Update()

    # Write out the interpolated points
    # interpolation_writer = vtk.vtkPolyDataWriter()
    # interpolation_writer.SetFileName("/home/gabi/PycharmProjects/EFA_interopaltion_approximation/test_data/contour12-smoother.vtk")
    # interpolation_writer.SetInputData(smoother.GetOutput())
    # interpolation_writer.Update()
    #

    sphere = vtk.vtkSphereSource()
    sphere.SetPhiResolution(21)
    sphere.SetThetaResolution(21)
    sphere.SetRadius(1)

    # Setup actor and mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(functionSource.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("DarkSlateGrey"))
    actor.GetProperty().SetLineWidth(4.0)

    # Create a polydata to store everything in
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(contour_reader.GetOutput().GetPoints())

    pointMapper = vtk.vtkGlyph3DMapper()
    pointMapper.SetInputData(polyData)
    pointMapper.SetSourceConnection(sphere.GetOutputPort())

    pointActor = vtk.vtkActor()
    pointActor.SetMapper(pointMapper)
    pointActor.GetProperty().SetColor(colors.GetColor3d("Peacock"))

    # Setup render window, renderer, and interactor
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName("ParametricSpline")

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderer.AddActor(actor)
    renderer.AddActor(pointActor)
    renderer.SetBackground(colors.GetColor3d("Silver"))

    renderWindow.Render()
    renderWindowInteractor.Start()
