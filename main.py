from fastapi import FastAPI, UploadFile

from fastapi.responses import FileResponse

import meshio

import vtk

from vtk import vtkLSDynaReader as lsr
 
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/file/convert")
def convert(file: UploadFile):
    mesh = meshio.read(file)
    return meshio.write("example.vtu", mesh)


@app.post("/test")
def filetesting(file: UploadFile):
    return FileResponse(path = file.filename)

@app.post("/test2")
def toxdmf(file: UploadFile):
    mesh = meshio.read(file.filename, file_format="vtk")
    return  meshio.write("output.xml", mesh, file_format="xdmf")

@app.post("/testdolfin")
def dolfin(file: UploadFile):
    mesh = meshio.read(file.filename, file_format="vtk")
    return  meshio.write("outputdolfin.xml", mesh, file_format="dolfin-xml")

@app.post("/toXMLconvert")
def convert(file: UploadFile):
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(file.filename)
    reader.Update()

    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputData(reader.GetOutput())
    writer.SetFileName("outputXMLfromVTK.xml")
    writer.Write()

@app.post("/toVTKconvert")
def convert(file: UploadFile):
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file.filename)
    reader.Update()

    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetInputData(reader.GetOutput())
    writer.SetFileName("outputVTKfromXML.vtk")
    writer.Write()

@app.post("/CanReadFile")
def canread(file: UploadFile):
    reader = vtk.vtkLSDynaReader()
    reader.SetFileName(file.filename)
    reader.Update()
    return lsr.CanReadFile(reader)

@app.post("/fromVTKtoK")
def convert(file: UploadFile):
    mesh = meshio.read(file.filename, file_format="vtk")
    return  meshio.write("outputdolfin.k", mesh, file_format="k")

@app.post("/SliceFilter")
def Sfilter(file: UploadFile):
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(file.filename)
    reader.Update()

    plane = vtk.vtkPlane()
    plane.SetOrigin(2.5, 0, 0)
    plane.SetNormal(1, 1, 1)

    cutter = vtk.vtkCutter()
    cutter.SetInputData(reader.GetOutput())
    cutter.SetCutFunction(plane)
    cutter.Update()

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName("SliceFilterOUT.vtk")
    writer.SetInputData(cutter.GetOutput())
    writer.Write()
    
@app.post("/ValueFilter")
def Vfilter(file: UploadFile):
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(file.filename)
    reader.Update()

    grid = reader.GetOutput()

    point_filter = vtk.vtkThresholdPoints()
    point_filter.SetInputData(grid)
    point_filter.SetLowerThreshold(15)
    cell_filter = vtk.vtkThreshold()
    cell_filter.SetInputData(grid)
    cell_filter.SetLowerThreshold(0)
    combined_filter = vtk.vtkAppendFilter()
    combined_filter.AddInputConnection(point_filter.GetOutputPort())
    combined_filter.AddInputConnection(cell_filter.GetOutputPort())
    combined_filter.Update()

    filtered_output = combined_filter.GetOutput()

    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName("ValueFilterOUT.vtk")
    writer.SetInputData(filtered_output)
    writer.Write()