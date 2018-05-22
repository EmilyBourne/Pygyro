from mpi4py import MPI
import numpy as np
import pytest
from math import pi

from .grid          import Grid
from .layout        import LayoutManager
from .process_grid  import compute_2d_process_grid

def define_f(grid):
    [nEta1,nEta2,nEta3,nEta4] = grid.nGlobalCoords
    
    for i,x in grid.getCoords(0):
        for j,y in grid.getCoords(1):
            for k,z in grid.getCoords(2):
                Slice = grid.get1DSlice([i,j,k])
                for l,a in enumerate(Slice):
                    [I,J,K,L] = grid.getGlobalIndices([i,j,k,l])
                    Slice[l] = I*nEta4*nEta3*nEta2+J*nEta4*nEta3+K*nEta4+L

def compare_f(grid):
    [nEta1,nEta2,nEta3,nEta4] = grid.nGlobalCoords
    
    for i,x in grid.getCoords(0):
        for j,y in grid.getCoords(1):
            for k,z in grid.getCoords(2):
                Slice = grid.get1DSlice([i,j,k])
                for l,a in enumerate(Slice):
                    [I,J,K,L] = grid.getGlobalIndices([i,j,k,l])
                    assert(a == I*nEta4*nEta3*nEta2+J*nEta4*nEta3+K*nEta4+L)

@pytest.mark.serial
def test_Grid_serial():
    eta_grids=[np.linspace(0,1,10),
               np.linspace(0,6.28318531,10),
               np.linspace(0,10,10),
               np.linspace(0,10,10)]
    
    nprocs = compute_2d_process_grid( [10,10,10,10], MPI.COMM_WORLD.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    Grid(eta_grids,manager,'flux_surface')

@pytest.mark.parallel
def test_Grid_parallel():
    eta_grids=[np.linspace(0,1,10),
               np.linspace(0,6.28318531,10),
               np.linspace(0,10,10),
               np.linspace(0,10,10)]
    
    nprocs = compute_2d_process_grid( [10,10,10,10], MPI.COMM_WORLD.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    Grid(eta_grids,manager,'flux_surface')

@pytest.mark.serial
def test_CoordinateSave():
    nv=10
    ntheta=20
    nr=30
    nz=15
    
    eta_grid = [np.linspace(0.5,14.5,nr),
                np.linspace(0,2*pi,ntheta,endpoint=False),
                np.linspace(0,50,nz),
                np.linspace(-5,5,nv)]
    
    nprocs = compute_2d_process_grid( [10,10,10,10], MPI.COMM_WORLD.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grid )
    
    grid = Grid(eta_grid,manager,'flux_surface')
    
    dim_order = [0,3,1,2]
    for j in range(4):
        for i, x in grid.getCoords(j):
            assert(x==eta_grid[dim_order[j]][i])

@pytest.mark.parallel
def test_LayoutSwap():
    nprocs = compute_2d_process_grid( [40,20,10,30], MPI.COMM_WORLD.Get_size() )
    
    eta_grids=[np.linspace(0,1,4),
               np.linspace(0,6.28318531,4),
               np.linspace(0,10,4),
               np.linspace(0,10,10)]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    
    grid = Grid(eta_grids,remapper,'flux_surface')
    
    define_f(grid)
    
    grid.setLayout('v_parallel')
    
    compare_f(grid)

@pytest.mark.parallel
def test_Contiguous():
    eta_grids=[np.linspace(0,1,10),
               np.linspace(0,6.28318531,10),
               np.linspace(0,10,10),
               np.linspace(0,10,10)]
    
    nprocs = compute_2d_process_grid( [10,10,10,10], MPI.COMM_WORLD.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    grid = Grid(eta_grids,manager,'flux_surface')
    
    assert(grid.get2DSlice([0,0]).flags['C_CONTIGUOUS'])
    assert(grid.get1DSlice([0,0,0]).flags['C_CONTIGUOUS'])
    
    grid.setLayout('v_parallel')
    
    assert(grid.get2DSlice([0,0]).flags['C_CONTIGUOUS'])
    assert(grid.get1DSlice([0,0,0]).flags['C_CONTIGUOUS'])
    
    grid.setLayout('poloidal')
    
    assert(grid.get2DSlice([0,0]).flags['C_CONTIGUOUS'])
    assert(grid.get1DSlice([0,0,0]).flags['C_CONTIGUOUS'])
    
    grid.setLayout('v_parallel')
    
    assert(grid.get2DSlice([0,0]).flags['C_CONTIGUOUS'])
    assert(grid.get1DSlice([0,0,0]).flags['C_CONTIGUOUS'])
    
    grid.setLayout('flux_surface')
    
    assert(grid.get2DSlice([0,0]).flags['C_CONTIGUOUS'])
    assert(grid.get1DSlice([0,0,0]).flags['C_CONTIGUOUS'])