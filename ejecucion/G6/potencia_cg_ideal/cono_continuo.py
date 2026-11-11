"""Independent SOCP contrast of the hypothetical force allocation."""
import math
import numpy as np
import scipy.sparse as sp
import clarabel
from reserva_momentos import G

def solve_continuous(centres,cg,moment,force=None,angle_deg=45.,preload=1.):
    """Minimize max Euclidean fan force, with continuous ideal upright cones."""
    if not 0 < angle_deg < 90:
        raise ValueError('angle must be between 0 and 90 degrees')
    blocks=[]
    for p in centres:
        x,y=p[0]-cg[0],p[1]-cg[1]
        zx,zy=-.039-cg[2],-.021-cg[2]
        blocks.append(np.array([[1,0,0],[0,1,0],[0,0,1],[0,-zy,y],[zx,0,-x],[-y,x,0]],float))
    equality=np.column_stack((np.hstack(blocks),np.zeros(6)))
    target=np.array([*(force if force is not None else (0,0,5*G)),*moment],float)
    matrices=[equality]; rhs=[target]; cones=[clarabel.ZeroConeT(6)]
    # Positive slack = Fz - preload.
    m=np.zeros((4,13))
    for i in range(4): m[i,3*i+2]=-1
    matrices.append(m);rhs.append(np.full(4,-preload));cones.append(clarabel.NonnegativeConeT(4))
    for i in range(4):
        # SOC slack (t, Fx, Fy, Fz).
        m=np.zeros((4,13));m[0,12]=-1;m[1:,3*i:3*i+3]=-np.eye(3)
        matrices.append(m);rhs.append(np.zeros(4));cones.append(clarabel.SecondOrderConeT(4))
        # SOC slack (tan(theta)*Fz, Fx, Fy).
        m=np.zeros((3,13));m[0,3*i+2]=-math.tan(math.radians(angle_deg));m[1,3*i]=-1;m[2,3*i+1]=-1
        matrices.append(m);rhs.append(np.zeros(3));cones.append(clarabel.SecondOrderConeT(3))
    A=sp.csc_matrix(np.vstack(matrices)); b=np.concatenate(rhs)
    objective=np.r_[np.zeros(12),1.]
    settings=clarabel.DefaultSettings(); settings.verbose=False
    solver=clarabel.DefaultSolver(sp.csc_matrix((13,13)),objective,A,b,cones,settings)
    solution=solver.solve();status=str(solution.status)
    if status!='Solved':
        return {'status':status,'capacity_N':None}
    z=np.array(solution.x); f=z[:12].reshape(4,3);t=float(z[12])
    residual=float(np.max(abs(equality@z-target)))
    caperr=float(max(0,np.max(np.linalg.norm(f,axis=1)-t)))
    coneerr=float(max(0,np.max(np.linalg.norm(f[:,:2],axis=1)-math.tan(math.radians(angle_deg))*f[:,2])))
    preloaderr=float(max(0,preload-min(f[:,2])))
    if not np.isfinite(z).all() or max(residual,caperr,coneerr,preloaderr)>2e-6:
        raise ArithmeticError(f'invalid SOCP solution {residual,caperr,coneerr,preloaderr}')
    return {'status':status,'capacity_N':t,'fan_forces_N':f.tolist(),
            'max_primal_residual':max(residual,caperr,coneerr,preloaderr),
            'solver_primal_residual':float(solution.r_prim),'solver_dual_residual':float(solution.r_dual)}
