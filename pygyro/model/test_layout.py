from mpi4py import MPI
import numpy as np
import pytest

from .layout        import LayoutManager, Layout
from .process_grid  import compute_2d_process_grid, compute_2d_process_grid_from_max

def define_f(Eta1,Eta2,Eta3,Eta4,layout,f):
    nEta1=len(Eta1)
    nEta2=len(Eta2)
    nEta3=len(Eta3)
    nEta4=len(Eta4)
    inv_dims=[0,0,0,0]
    for i,j in enumerate(layout.dims_order):
        inv_dims[j]=i
    
    # The loop ordering for the tests is not optimal but allows all layouts to use the same function
    for i,eta1 in enumerate(Eta1[layout.starts[inv_dims[0]]:layout.ends[inv_dims[0]]]):
        # get global index
        I=i+layout.starts[inv_dims[0]]
        for j,eta2 in enumerate(Eta2[layout.starts[inv_dims[1]]:layout.ends[inv_dims[1]]]):
            # get global index
            J=j+layout.starts[inv_dims[1]]
            for k,eta3 in enumerate(Eta3[layout.starts[inv_dims[2]]:layout.ends[inv_dims[2]]]):
                # get global index
                K=k+layout.starts[inv_dims[2]]
                for l,eta4 in enumerate(Eta4[layout.starts[inv_dims[3]]:layout.ends[inv_dims[3]]]):
                    # get global index
                    L=l+layout.starts[inv_dims[3]]
                    indices=[0,0,0,0]
                    indices[inv_dims[0]]=i
                    indices[inv_dims[1]]=j
                    indices[inv_dims[2]]=k
                    indices[inv_dims[3]]=l
                    
                    # set value using global indices
                    f[indices[0],indices[1],indices[2],indices[3]]= \
                            I*nEta4*nEta3*nEta2+J*nEta4*nEta3+K*nEta4+L

def compare_f(Eta1,Eta2,Eta3,Eta4,layout,f):
    nEta1=len(Eta1)
    nEta2=len(Eta2)
    nEta3=len(Eta3)
    nEta4=len(Eta4)
    inv_dims=[0,0,0,0]
    for i,j in enumerate(layout.dims_order):
        inv_dims[j]=i
    
    # The loop ordering for the tests is not optimal but allows all layouts to use the same function
    
    for i,eta1 in enumerate(Eta1[layout.starts[inv_dims[0]]:layout.ends[inv_dims[0]]]):
        # get global index
        I=i+layout.starts[inv_dims[0]]
        for j,eta2 in enumerate(Eta2[layout.starts[inv_dims[1]]:layout.ends[inv_dims[1]]]):
            # get global index
            J=j+layout.starts[inv_dims[1]]
            for k,eta3 in enumerate(Eta3[layout.starts[inv_dims[2]]:layout.ends[inv_dims[2]]]):
                # get global index
                K=k+layout.starts[inv_dims[2]]
                for l,eta4 in enumerate(Eta4[layout.starts[inv_dims[3]]:layout.ends[inv_dims[3]]]):
                    # get global index
                    L=l+layout.starts[inv_dims[3]]
                    indices=[0,0,0,0]
                    indices[inv_dims[0]]=i
                    indices[inv_dims[1]]=j
                    indices[inv_dims[2]]=k
                    indices[inv_dims[3]]=l
                    
                    # ensure value is as expected from function define_f()
                    assert(f[indices[0],indices[1],indices[2],indices[3]]== \
                        float(I*nEta4*nEta3*nEta2+J*nEta4*nEta3+K*nEta4+L))

@pytest.mark.serial
def test_Layout_DimsOrder():
    eta_grids=[np.linspace(0,1,40),
               np.linspace(0,6.28318531,20),
               np.linspace(0,10,10),
               np.linspace(0,10,30)]
    
    l = Layout('test', [2,3], [0,3,2,1], eta_grids, [0,0] )
    assert(l.dims_order==[0,3,2,1])
    assert(l.inv_dims_order==[0,3,2,1])
    
    l = Layout('test', [2,3], [0,2,3,1], eta_grids, [0,0] )
    assert(l.dims_order==[0,2,3,1])
    assert(l.inv_dims_order==[0,3,1,2])
    
    l = Layout('test', [2,3], [2,1,0,3], eta_grids, [0,0] )
    assert(l.dims_order==[2,1,0,3])
    assert(l.inv_dims_order==[2,1,0,3])

@pytest.mark.parallel
def test_OddLayoutPaths():
    npts = [40,20,10,30]
    comm = MPI.COMM_WORLD
    nprocs = compute_2d_process_grid( npts , comm.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'0123': [0,1,2,3],
               '0321': [0,3,2,1],
               '1320': [1,3,2,0],
               '1302': [1,3,0,2]}
    remapper = LayoutManager( comm, layouts, nprocs, eta_grids )
    
    layout1=remapper.getLayout('1320')
    assert(layout1.name=='1320')
    layout2=remapper.getLayout('1302')
    
    fStart = np.empty(remapper.bufferSize)
    fEnd = np.empty(remapper.bufferSize)
    f1_s = np.split(fStart,[layout1.size])[0].reshape(layout1.shape)
    f1_e = np.split(fEnd  ,[layout1.size])[0].reshape(layout1.shape)
    f2_s = np.split(fStart,[layout2.size])[0].reshape(layout2.shape)
    f2_e = np.split(fEnd  ,[layout2.size])[0].reshape(layout2.shape)
    
    define_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout1,f1_s)
    
    remapper.transpose(source=fStart,
                       dest  =fEnd,
                       source_name='1320',
                       dest_name='1302')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout2,f2_e)
    
    # Even number of steps
    with pytest.warns(UserWarning):
        remapper.transpose(source=fEnd,
                           dest  =fStart,
                           source_name='1302',
                           dest_name='0321')
    
    layout = remapper.getLayout('0321')
    f = np.split(fStart  ,[layout.size])[0].reshape(layout.shape)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout,f)
    
    
    remapper.transpose(source=fStart,
                       dest  =fEnd,
                       source_name='0321',
                       dest_name='0123')
    
    layout = remapper.getLayout('0123')
    f = np.split(fEnd  ,[layout.size])[0].reshape(layout.shape)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout,f)
    
    # Odd number of steps
    with pytest.warns(UserWarning):
        remapper.transpose(source=fEnd,
                           dest  =fStart,
                           source_name='0123',
                           dest_name='1302')
    
    layout = remapper.getLayout('1302')
    f = np.split(fStart  ,[layout.size])[0].reshape(layout.shape)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout,f)

@pytest.mark.parallel
def test_OddLayoutPaths_IntactSource():
    npts = [40,20,10,30]
    comm = MPI.COMM_WORLD
    nprocs = compute_2d_process_grid( npts , comm.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'0123': [0,1,2,3],
               '0321': [0,3,2,1],
               '1320': [1,3,2,0],
               '1302': [1,3,0,2]}
    remapper = LayoutManager( comm, layouts, nprocs, eta_grids )
    
    layout1=remapper.getLayout('1320')
    assert(layout1.name=='1320')
    layout2=remapper.getLayout('1302')
    
    fStart = np.empty(remapper.bufferSize)
    fEnd = np.empty(remapper.bufferSize)
    fBuf = np.empty(remapper.bufferSize)
    f1_s = np.split(fStart,[layout1.size])[0].reshape(layout1.shape)
    f1_e = np.split(fEnd  ,[layout1.size])[0].reshape(layout1.shape)
    f2_s = np.split(fStart,[layout2.size])[0].reshape(layout2.shape)
    f2_e = np.split(fEnd  ,[layout2.size])[0].reshape(layout2.shape)
    
    define_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout1,f1_s)
    
    remapper.transpose(source=fStart,
                       dest  =fEnd,
                       buf   =fBuf,
                       source_name='1320',
                       dest_name='1302')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout2,f2_e)
    
    # Even number of steps
    with pytest.warns(UserWarning):
        remapper.transpose(source=fEnd,
                           dest  =fStart,
                           buf   =fBuf,
                           source_name='1302',
                           dest_name='0321')
    
    layout = remapper.getLayout('0321')
    f = np.split(fStart  ,[layout.size])[0].reshape(layout.shape)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout,f)
    
    
    remapper.transpose(source=fStart,
                       dest  =fEnd,
                       buf   =fBuf,
                       source_name='0321',
                       dest_name='0123')
    
    layout = remapper.getLayout('0123')
    f = np.split(fEnd  ,[layout.size])[0].reshape(layout.shape)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout,f)
    
    # Odd number of steps
    with pytest.warns(UserWarning):
        remapper.transpose(source=fEnd,
                           dest  =fStart,
                           buf   =fBuf,
                           source_name='0123',
                           dest_name='1302')
    
    layout = remapper.getLayout('1302')
    f = np.split(fStart  ,[layout.size])[0].reshape(layout.shape)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],layout,f)

@pytest.mark.parallel
def test_LayoutSwap_IntactSource():
    npts = [40,20,10,30]
    comm = MPI.COMM_WORLD
    nprocs = compute_2d_process_grid( npts, comm.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    pLayout = remapper.getLayout('poloidal')
    
    assert(remapper.bufferSize==max(fsLayout.size,vLayout.size,pLayout.size))
    
    f1 = np.empty(remapper.bufferSize)
    f2 = np.empty(remapper.bufferSize)
    f3 = np.empty(remapper.bufferSize)
    
    f_fs_1 = np.split( f1, [fsLayout.size] )[0].reshape(fsLayout.shape)
    f_fs_2 = np.split( f2, [fsLayout.size] )[0].reshape(fsLayout.shape)
    f_fs_3 = np.split( f3, [fsLayout.size] )[0].reshape(fsLayout.shape)
    assert(not f_fs_1.flags['OWNDATA'])
    assert(not f_fs_2.flags['OWNDATA'])
    assert(not f_fs_3.flags['OWNDATA'])
    
    f_v_1  = np.split( f1, [ vLayout.size] )[0].reshape( vLayout.shape)
    f_v_2  = np.split( f2, [ vLayout.size] )[0].reshape( vLayout.shape)
    f_v_3  = np.split( f3, [ vLayout.size] )[0].reshape( vLayout.shape)
    assert(not f_v_1.flags['OWNDATA'])
    assert(not f_v_2.flags['OWNDATA'])
    assert(not f_v_3.flags['OWNDATA'])
    
    f_p_1  = np.split( f1, [ pLayout.size] )[0].reshape( pLayout.shape)
    f_p_2  = np.split( f2, [ pLayout.size] )[0].reshape( pLayout.shape)
    f_p_3  = np.split( f3, [ pLayout.size] )[0].reshape( pLayout.shape)
    assert(not f_p_1.flags['OWNDATA'])
    assert(not f_p_2.flags['OWNDATA'])
    assert(not f_p_3.flags['OWNDATA'])
    
    define_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_1)
    
    remapper.transpose(source=f1,
                       dest=f2,
                       buf=f3,
                       source_name='flux_surface',
                       dest_name='v_parallel')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_1)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],vLayout,f_v_2)
    
    remapper.transpose(source = f2,
                       dest   = f1,
                       buf    = f3,
                       source_name='v_parallel',
                       dest_name='poloidal')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],vLayout,f_v_2)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],pLayout,f_p_1)
    
    remapper.transpose(source = f1,
                       dest   = f2,
                       buf    = f3,
                       source_name='poloidal',
                       dest_name='v_parallel')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],pLayout,f_p_1)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],vLayout,f_v_2)
    
    remapper.transpose(source = f2,
                       dest   = f1,
                       buf    = f3,
                       source_name='v_parallel',
                       dest_name='flux_surface')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],vLayout,f_v_2)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_1)

@pytest.mark.parallel
def test_LayoutSwap():
    npts = [40,20,10,30]
    nprocs = compute_2d_process_grid( npts, MPI.COMM_WORLD.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    pLayout = remapper.getLayout('poloidal')
    
    assert(remapper.bufferSize==max(fsLayout.size,vLayout.size,pLayout.size))

    f1 = np.empty(remapper.bufferSize)
    f2 = np.empty(remapper.bufferSize)
    
    f_fs_1 = np.split( f1, [fsLayout.size] )[0].reshape(fsLayout.shape)
    f_fs_2 = np.split( f2, [fsLayout.size] )[0].reshape(fsLayout.shape)
    assert(not f_fs_1.flags['OWNDATA'])
    assert(not f_fs_2.flags['OWNDATA'])
    
    f_v_1  = np.split( f1, [ vLayout.size] )[0].reshape( vLayout.shape)
    f_v_2  = np.split( f2, [ vLayout.size] )[0].reshape( vLayout.shape)
    assert(not f_v_1.flags['OWNDATA'])
    assert(not f_v_2.flags['OWNDATA'])
    
    f_p_1  = np.split( f1, [ pLayout.size] )[0].reshape( pLayout.shape)
    f_p_2  = np.split( f2, [ pLayout.size] )[0].reshape( pLayout.shape)
    assert(not f_p_1.flags['OWNDATA'])
    assert(not f_p_2.flags['OWNDATA'])
    
    define_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_1)
    
    remapper.transpose(source=f1,
                       dest=f2,
                       source_name='flux_surface',
                       dest_name='v_parallel')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],vLayout,f_v_2)
    
    remapper.transpose(source = f2,
                       dest   = f1,
                       source_name='v_parallel',
                       dest_name='poloidal')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],pLayout,f_p_1)
    
    remapper.transpose(source = f1,
                       dest   = f2,
                       source_name='poloidal',
                       dest_name='v_parallel')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],vLayout,f_v_2)
    
    remapper.transpose(source = f2,
                       dest   = f1,
                       source_name='v_parallel',
                       dest_name='flux_surface')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_1)
    
    assert(not f_fs_1.flags['OWNDATA'])
    assert(not f_v_1.flags['OWNDATA'])
    assert(not f_p_1.flags['OWNDATA'])
    assert(not f_fs_2.flags['OWNDATA'])
    assert(not f_v_2.flags['OWNDATA'])
    assert(not f_p_2.flags['OWNDATA'])

@pytest.mark.parallel
def test_IncompatibleLayoutError():
    npts = [10,10,10,10]
    nprocs = compute_2d_process_grid( npts, MPI.COMM_WORLD.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    with pytest.raises(RuntimeError):
        layouts = {'flux_surface': [0,3,1,2],
                   'v_parallel'  : [0,2,1,3],
                   'poloidal'    : [3,2,1,0],
                   'broken'      : [1,0,2,3]}
        LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )

@pytest.mark.parallel
def test_CompatibleLayouts():
    eta_grids=[np.linspace(0,1,10),
               np.linspace(0,6.28318531,10),
               np.linspace(0,10,10),
               np.linspace(0,10,10)]
    
    nprocs = compute_2d_process_grid( [10,10,10,10], MPI.COMM_WORLD.Get_size() )
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )

@pytest.mark.parallel
def test_BadStepWarning():
    npts = [10,10,20,15]
    nprocs = compute_2d_process_grid( npts, MPI.COMM_WORLD.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    pLayout = remapper.getLayout('poloidal')
    
    assert(remapper.bufferSize==max(fsLayout.size,vLayout.size,pLayout.size))
    
    f1 = np.empty(remapper.bufferSize)
    f2 = np.empty(remapper.bufferSize)
    
    with pytest.warns(UserWarning):
        remapper.transpose(source = f1,
                           dest   = f2,
                           source_name='flux_surface',
                           dest_name='poloidal')

@pytest.mark.parallel
def test_BadStepWarning_IntactSource():
    npts = [10,10,20,15]
    nprocs = compute_2d_process_grid( npts, MPI.COMM_WORLD.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    pLayout = remapper.getLayout('poloidal')
    
    fStart = np.empty(max(fsLayout.size,vLayout.size,pLayout.size))
    fEnd = np.empty(max(fsLayout.size,vLayout.size,pLayout.size))
    fBuf = np.empty(max(fsLayout.size,vLayout.size,pLayout.size))
    f_fs_s = np.split(fStart,[fsLayout.size])[0].reshape(fsLayout.shape)
    assert(not f_fs_s.flags['OWNDATA'])
    f_v_s  = np.split(fStart,[ vLayout.size])[0].reshape( vLayout.shape)
    assert(not f_v_s.flags['OWNDATA'])
    f_p_s  = np.split(fStart,[ pLayout.size])[0].reshape( pLayout.shape)
    assert(not f_p_s.flags['OWNDATA'])
    f_fs_e = np.split(fEnd  ,[fsLayout.size])[0].reshape(fsLayout.shape)
    assert(not f_fs_e.flags['OWNDATA'])
    f_v_e  = np.split(fEnd  ,[ vLayout.size])[0].reshape( vLayout.shape)
    assert(not f_v_e.flags['OWNDATA'])
    f_p_e  = np.split(fEnd  ,[ pLayout.size])[0].reshape( pLayout.shape)
    assert(not f_p_e.flags['OWNDATA'])
    
    
    
    with pytest.warns(UserWarning):
        remapper.transpose(source = fStart,
                           dest = fEnd,
                           buf  = fBuf,
                           source_name='flux_surface',
                           dest_name='poloidal')

@pytest.mark.parallel
def test_copy():
    npts = [10,10,20,15]
    nprocs = compute_2d_process_grid( npts, MPI.COMM_WORLD.Get_size() )
    
    eta_grids=[np.linspace(0,1,npts[0]),
               np.linspace(0,6.28318531,npts[1]),
               np.linspace(0,10,npts[2]),
               np.linspace(0,10,npts[3])]
    
    layouts = {'flux_surface': [0,3,1,2],
               'v_parallel'  : [0,2,1,3],
               'poloidal'    : [3,2,1,0]}
    remapper = LayoutManager( MPI.COMM_WORLD, layouts, nprocs, eta_grids )
    
    fsLayout = remapper.getLayout('flux_surface')
    vLayout = remapper.getLayout('v_parallel')
    pLayout = remapper.getLayout('poloidal')
    
    fStart = np.empty(remapper.bufferSize)
    fEnd = np.empty(remapper.bufferSize)
    fBuf = np.empty(remapper.bufferSize)
    
    f_fs_s = np.split(fStart,[fsLayout.size])[0].reshape(fsLayout.shape)
    f_fs_e = np.split(fEnd  ,[fsLayout.size])[0].reshape(fsLayout.shape)
    f_fs_b = np.split(fBuf  ,[fsLayout.size])[0].reshape(fsLayout.shape)
    assert(not f_fs_s.flags['OWNDATA'])
    assert(not f_fs_e.flags['OWNDATA'])
    assert(not f_fs_b.flags['OWNDATA'])
    
    f_v_s  = np.split(fStart,[ vLayout.size])[0].reshape( vLayout.shape)
    f_v_e  = np.split(fEnd  ,[ vLayout.size])[0].reshape( vLayout.shape)
    f_v_b  = np.split(fBuf  ,[ vLayout.size])[0].reshape( vLayout.shape)
    assert(not f_v_s.flags['OWNDATA'])
    assert(not f_v_e.flags['OWNDATA'])
    assert(not f_v_b.flags['OWNDATA'])
    
    f_p_s  = np.split(fStart,[ pLayout.size])[0].reshape( pLayout.shape)
    f_p_e  = np.split(fEnd  ,[ pLayout.size])[0].reshape( pLayout.shape)
    f_p_b  = np.split(fEnd  ,[ pLayout.size])[0].reshape( pLayout.shape)
    assert(not f_p_s.flags['OWNDATA'])
    assert(not f_p_e.flags['OWNDATA'])
    assert(not f_p_b.flags['OWNDATA'])
    
    define_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_s)
    
    remapper.transpose(source=fStart,
                       dest=fEnd,
                       buf =fBuf,
                       source_name='flux_surface',
                       dest_name='flux_surface')
    
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_s)
    compare_f(eta_grids[0],eta_grids[1],eta_grids[2],eta_grids[3],fsLayout,f_fs_e)
    
    remapper.transpose(source=fEnd,
                       dest=fBuf,
                       source_name='flux_surface',
                       dest_name='flux_surface')