"""OpenFOAM Foundation 13 prototype RANS duct case; no claimed validation."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent;case=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'conducto_X0_Y0_h0.006')
def foam(path,text,cls='dictionary',obj=None):
 p=case/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('FoamFile\n{version 2.0; format ascii; class '+cls+'; object '+(obj or p.name)+';}\n'+text+'\n')
wall='"(walls|vane.*)"'
foam('constant/physicalProperties','viscosityModel constant;\nnu [0 2 -1 0 0 0 0] 1.46e-5;')
foam('constant/momentumTransport','simulationType RAS;\nRAS { model kOmegaSST; turbulence on; printCoeffs on; }')
foam('0/U',f'dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (0 0 -40);\nboundaryField {{ inlet {{type fixedValue; value uniform (0 0 -40);}} outlet {{type pressureInletOutletVelocity; value uniform (0 0 -40);}} {wall} {{type noSlip;}} }}','volVectorField')
foam('0/p',f'dimensions [0 2 -2 0 0 0 0];\ninternalField uniform 0;\nboundaryField {{ inlet {{type zeroGradient;}} outlet {{type fixedValue; value uniform 0;}} {wall} {{type zeroGradient;}} }}','volScalarField')
for field,dim,value,wtype in [('k','[0 2 -2 0 0 0 0]',6,'kqRWallFunction'),('omega','[0 0 -1 0 0 0 0]',894.4271909999,'omegaWallFunction'),('nut','[0 2 -1 0 0 0 0]',0,'nutkWallFunction')]:
 inlet=f'type fixedValue; value uniform {value};' if field!='nut' else 'type calculated; value uniform 0;'
 outlet=f'type inletOutlet; inletValue uniform {value}; value uniform {value};' if field!='nut' else 'type calculated; value uniform 0;'
 foam('0/'+field,f'dimensions {dim};\ninternalField uniform {value};\nboundaryField {{inlet {{{inlet}}} outlet {{{outlet}}} {wall} {{type {wtype}; value uniform {value};}} }}','volScalarField')
functions=''
for axis,z in [('X',-.012),('Y',-.040)]:
 for j,offset in enumerate([-.022,0,.022]):
  center=(0,offset,z) if axis=='X' else (offset,0,z);cs=' '.join(map(str,center));name=f'vane{axis}{j}'
  functions+=f'force_{name} {{type forces; libs ("libforces.so"); patches ({name}); rho rhoInf; rhoInf 1.225; CofR ({cs}); writeControl timeStep; writeInterval 1;}}\n'
for patch in ['inlet','outlet']:
 functions+=f'p_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation areaAverage; writeFields false; fields (p U); writeControl timeStep; writeInterval 1;}}\n'
 functions+=f'flow_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation sum; writeFields false; fields (phi); writeControl timeStep; writeInterval 1;}}\n'
foam('system/controlDict','application foamRun;\nsolver incompressibleFluid;\nstartFrom startTime; startTime 0; stopAt endTime; endTime 300; deltaT 1; writeControl timeStep; writeInterval 100; purgeWrite 2; writeFormat ascii; writePrecision 9; runTimeModifiable true;\nfunctions {\n'+functions+'}')
foam('system/fvSchemes','ddtSchemes { default steadyState; }\ngradSchemes {default Gauss linear;}\ndivSchemes {default none; div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear;}\nlaplacianSchemes {default Gauss linear corrected;}\ninterpolationSchemes {default linear;}\nsnGradSchemes {default corrected;}\nwallDist {method meshWave;}')
foam('system/fvSolution','solvers { p {solver GAMG; tolerance 1e-7; relTol 0.05; smoother GaussSeidel;} "(U|k|omega)" {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0.1;} }\nSIMPLE {nNonOrthogonalCorrectors 2; consistent yes; residualControl { p 1e-4; U 1e-5; k 1e-5; omega 1e-5;} }\nrelaxationFactors {fields {p 0.3;} equations {U 0.5; k 0.5; omega 0.5;} }')
(case/'case_assumptions.json').write_text(json.dumps(dict(version='OpenFOAM Foundation13',rho_kgm3=1.225,nu_m2s=1.46e-5,inlet_U_ms=[0,0,-40],inlet_turbulence_I=.05,k_m2s2=6,omega_s1=894.4271909999,model='steady incompressible RANS kOmegaSST',end_iterations=300,status='Prototype case, not converged/validated by preparation',limits=['No fan pressure/rotation coupling','No exterior domain or installed fuselage','No thermal/compressible or transonic model','No prism layers; yPlus and grid sensitivity must be checked','Flat square-edge vanes; transition/separation sensitive','Inlet turbulence and operating speed assumed']),indent=2))
print(case)
