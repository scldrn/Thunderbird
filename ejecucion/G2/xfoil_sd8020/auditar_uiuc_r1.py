"""Separate XFOIL's marching warnings from its final coupled-iteration check."""
from pathlib import Path
import hashlib
import json
import math
import re

import numpy as np

HERE=Path(__file__).resolve().parent


def main():
    case=HERE/'uiuc_61400_r1'
    source=HERE/'xoper_mit_6.996.f'
    assert re.search(r'DATA\s+EPS1\s*/\s*1\.0E-4\s*/',source.read_text(),re.I)
    original=json.loads((case/'RESULTADOS.json').read_text())
    assert len(original['points'])==10 and all(not p['accepted_numerical_point'] for p in original['points'])
    details=[]
    for point in original['points']:
        log=case/f"{point['index']:02d}.log"
        text=log.read_text()
        rms=[float(x) for x in re.findall(r'\brms:\s*([0-9.Ee+-]+)',text)]
        marching=re.findall(r'MRCH(?:UE|DU): Convergence failed',text)
        final_failed=bool(re.search(r'VISCAL:\s+Convergence failed',text))
        assert rms and math.isfinite(rms[-1])
        assert marching and point['reported_convergence_failure']
        details.append(dict(index=point['index'],alpha_deg=point['alpha_deg'],
            final_coupled_RMS_reported=rms[-1],final_coupled_RMS_below_source_EPS1=rms[-1]<1e-4,
            marching_warnings=len(marching), VISCAL_final_failure_reported=final_failed,
            strict_original_screen_accepted=point['accepted_numerical_point'],
            cl_error=point['cl_error'],cd_error=point['cd_error'],
            log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    cl=np.array([p['cl_error'] for p in details]);cd=np.array([p['cd_error'] for p in details])
    report=dict(scope='Diagnostic only: all 10 original points retained; no model or physical validation',
        reference_source_EPS1=1e-4,source_criterion_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_result_sha256=hashlib.sha256((case/'RESULTADOS.json').read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        final_coupled_criterion_pass_count=sum(r['final_coupled_RMS_below_source_EPS1'] and
                                               not r['VISCAL_final_failure_reported'] for r in details),
        cases_with_marching_warnings=sum(r['marching_warnings']>0 for r in details),
        strict_original_screen_pass_count=sum(r['strict_original_screen_accepted'] for r in details),
        cl_RMSE_all_ten=float(np.sqrt(np.mean(cl**2))),cd_RMSE_all_ten=float(np.sqrt(np.mean(cd**2))),
        no_point_discarded=True,conditions_uncertainties='UIUC actual Mach/Ncrit not matched; FPE traps absent in this build',
        warning_cause_unresolved=True, physical_fan_acceptance=False,points=details)
    out=case/'AUDITORIA_RESIDUOS.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('points',)},indent=2))


if __name__=='__main__':main()
