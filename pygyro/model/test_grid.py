from mpi4py import MPI
import numpy as np
import pytest
from math import pi
import h5py
import os

from .grid          import Grid
from .layout        import getLayoutHandler, LayoutSwapper
from .process_grid  import compute_2d_process_grid, compute_2d_process_grid_from_max

def define_f(grid,t=0):
    [nEta1,nEta2,nEta3,nEta4] = grid.nGlobalCoords
    
    for i,x in grid.getCoords(0):
        for j,y in grid.getCoords(1):
            for k,z in grid.getCoords(2):
                Slice = grid.get1DSlice([i,j,k])
                for l,a in enumerate(Slice):
                    [I,J,K,L] = grid.getGlobalIndices([i,j,k,l])
                    Slice[l] = I*nEta4*nEta3*nEta2+J*nEta4*nEta3+K*nEta4+L+t

def define_phi(grid):
    [nEta1,nEta2,nEta3] = grid.nGlobalCoords
    
    for i,x in grid.getCoords(0):
        for j,y in grid.getCoords(1):
            Slice = grid.get1DSlice([i,j])
            for k,z in enumerate(Slice):
                [I,J,K] = grid.getGlobalIndices([i,j,k])
                Slice[k] = I*nEta3*nEta2+J*nEta3+K

def compare_f(grid,t=0):
    [nEta1,nEta2,nEta3,nEta4] = grid.nGlobalCoords
    
    for i,x in grid.getCoords(0):
        for j,y in grid.getCoords(1):
            for k,z in grid.getCoords(2):
                Slice = grid.get1DSlice([i,j,k])
                for l,a in enumerate(Slice):
                    [I,J,K,L] = grid.getGlobalIndices([i,j,k,l])
                    assert(a == I*nEta4*nEta3*nEta2+J*nEta4*nEta3+K*nEta4+L+t)

def compare_phi(grid):
    [nEta1,nEta2,nEta3] = grid.nGlobalCoords
    
    for i,x in grid.getCoords(0):
        for j,y in grid.getCoords(1):
            Slice = grid.get1DSlice([i,j])
            for k,a in enumerate(Slice):
                [I,J,K] = grid.getGlobalIndices([i,j,k])
                assert(a == I*nEta3*nEta2+J*nEta3+K)

@pytest.mark.serial
def test_Grid_serial():
    eta_grids=[np.linspace(0,1,10),
               np.linspace(0,6.28318531,10),
               np.linspace(0,10,10),
               np.linspace(0,10,10)]
    comm = MPI.COMM_WORLD
    
    nprocs = compute_2d_process_grid( [10,10,10,10], comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    Grid(eta_grids,[],manager,'flux_surface')

@pytest.mark.parallel
def test_Grid_parallel():
    eta_grids=[np.linspace(0,1,10),
               np.linspace(0,6.28318531,10),
               np.linspace(0,10,10),
               np.linspace(0,10,10)]
    comm = MPI.COMM_WORLD
    
    nprocs = compute_2d_process_grid( [10,10,10,10], comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    Grid(eta_grids,[],manager,'flux_surface')

@pytest.mark.parallel
def test_Grid_max():
    npts = [10,10,10,10]
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    comm = MPI.COMM_WORLD
    
    nprocs = compute_2d_process_grid( [10,10,10,10], comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    grid = Grid(eta_grids,[],manager,'flux_surface')
    define_f(grid)
    maxVal = grid.getMax(0)
    if (comm.Get_rank()==0):
        assert(maxVal==(np.prod(npts)-1))

@pytest.mark.parallel
def test_Grid_min():
    npts = [10,10,10,10]
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    comm = MPI.COMM_WORLD
    
    nprocs = compute_2d_process_grid( [10,10,10,10], comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    grid = Grid(eta_grids,[],manager,'flux_surface')
    define_f(grid)
    minVal = grid.getMin(0)
    if (comm.Get_rank()==0):
        assert(minVal==0)

@pytest.mark.parallel
def test_Grid_save_restore():
    npts = [10,10,10,10]
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    comm = MPI.COMM_WORLD
    
    nprocs = compute_2d_process_grid( [10,10,10,10], comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    grid = Grid(eta_grids,[],manager,'flux_surface',allocateSaveMemory = True)
    define_f(grid,0)
    grid.saveGridValues()
    define_f(grid,100)
    compare_f(grid,100)
    grid.restoreGridValues()
    compare_f(grid,0)

@pytest.mark.parallel
def test_Grid_save_restore_once():
    npts = [10,10,10,10]
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    comm = MPI.COMM_WORLD
    
    nprocs = compute_2d_process_grid( [10,10,10,10], comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    grid = Grid(eta_grids,[],manager,'flux_surface',allocateSaveMemory = True)
    grid.saveGridValues()
    with pytest.raises(AssertionError):
        grid.saveGridValues()
    grid.restoreGridValues()
    grid.saveGridValues()
    grid.freeGridSave()
    grid.saveGridValues()

@pytest.mark.serial
def test_CoordinateSave():
    comm = MPI.COMM_WORLD
    npts = [30,20,15,10]
    
    eta_grid = [np.linspace(0.5,14.5,npts[0]),
                np.linspace(0,2*pi,npts[1],endpoint=False),
                np.linspace(0,50,npts[2]),
                np.linspace(-5,5,npts[3])]
    
    nprocs = compute_2d_process_grid( npts, comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grid )
    
    grid = Grid(eta_grid,[],manager,'flux_surface')
    
    dim_order = [0,3,1,2]
    for j in range(4):
        for i, x in grid.getCoords(j):
            assert(x==eta_grid[dim_order[j]][i])

@pytest.mark.parallel
def test_LayoutSwap():
    comm = MPI.COMM_WORLD
    npts = [40,20,10,30]
    nprocs = compute_2d_process_grid( npts , comm.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    
    grid = Grid(eta_grids,[],remapper,'flux_surface')
    
    define_f(grid)
    
    grid.setLayout('v_parallel')
    
    compare_f(grid)

@pytest.mark.parallel
def test_Contiguous():
    comm = MPI.COMM_WORLD
    npts = [10,10,10,10]
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    nprocs = compute_2d_process_grid( npts, comm.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    manager = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    grid = Grid(eta_grids,[],manager,'flux_surface')
    
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

@pytest.mark.parallel
def test_PhiLayoutSwap():
    comm = MPI.COMM_WORLD
    npts = [40,20,40]
    
    n1 = min(npts[0],npts[2])
    n2 = min(npts[0],npts[1])
    nprocs = compute_2d_process_grid_from_max( n1 , n2 , comm.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2])]
    
    layout_poisson = {'mode_find' : [2,0,1],
                      'mode_solve': [2,1,0]}
    layout_advection = {'dphi'    : [0,1,2],
                        'poloidal': [2,1,0]}
    
    nproc = max(nprocs)
    if (nproc>n1):
        nproc=min(nprocs)
    
    remapper = LayoutSwapper( comm, [layout_poisson, layout_advection], [nprocs,nproc], eta_grids, 'mode_find' )
    
    fsLayout = remapper.getLayout('mode_find')
    vLayout = remapper.getLayout('poloidal')
    
    phi = Grid(eta_grids,[],remapper,'mode_find')
    
    define_phi(phi)
    
    phi.setLayout('poloidal')
    
    compare_phi(phi)

@pytest.mark.parallel
def test_h5py():
    comm = MPI.COMM_WORLD
    npts = [10,20,10,10]
    nprocs = compute_2d_process_grid( npts , comm.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = getLayoutHandler( comm, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    
    grid = Grid(eta_grids,[],remapper,'flux_surface')
    
    define_f(grid)
    
    if (comm.Get_rank()==0):
        if (not os.path.isdir('testValues')):
            os.mkdir('testValues')
    
    define_f(grid,20)
    grid.writeH5Dataset('testValues',20)
    define_f(grid,40)
    grid.writeH5Dataset('testValues',40)
    define_f(grid,80)
    grid.writeH5Dataset('testValues',80)
    define_f(grid,100)
    grid.writeH5Dataset('testValues',100)
    grid.loadFromFile('testValues')
    compare_f(grid,100)
