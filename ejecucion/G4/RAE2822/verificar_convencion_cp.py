"""Check NASA plot sign/branch ordering against its own published WIND data.

No own CFD prediction is used to choose the data convention.
"""
from pathlib import Path
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2]/'fuentes/benchmark_RAE2822'


def read_gen(path, count):
    rows = []
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) == 2:
            try:
                rows.append([float(v) for v in fields])
            except ValueError:
                continue
    a = np.array(rows)
    assert a.shape == (count, 2)
    return a


def main():
    commands = (SOURCE/'cfpost.cp.com').read_text()
    assert 'Cp scale -1' in commands
    assert 'subset i 33 337 j 1 k 1' in commands
    wind = read_gen(SOURCE/'cp.wind.gen', 305)
    exp = read_gen(SOURCE/'cp.exp.gen', 103)
    lew, lee = np.argmin(wind[:, 0]), np.argmin(exp[:, 0])
    # NASA documents i33..337 as lower TE -> LE -> upper TE.
    lo, up = wind[:lew+1][::-1], wind[lew:]
    rms = {}
    for name, first, second in (('experimental_first_upper', up, lo),
                                ('experimental_first_lower', lo, up)):
        published = np.r_[np.interp(exp[:lee+1, 0], first[:, 0], first[:, 1]),
                          np.interp(exp[lee+1:, 0], second[:, 0], second[:, 1])]
        rms[name] = float(np.sqrt(np.mean((published-exp[:, 1])**2)))
    assert rms['experimental_first_upper'] < .15
    assert rms['experimental_first_lower'] > 3*rms['experimental_first_upper']
    result = dict(scope='Input-data convention check, not own-solver validation',
        raw_experimental_second_column='minus_Cp_plot_ordinate', physical_Cp_multiplier=-1,
        experimental_trace='upper_TE_to_LE_then_lower_LE_to_TE',
        published_WIND_trace='lower_TE_to_LE_then_upper_LE_to_TE',
        sign_evidence='NASA cfpost.cp.com explicitly uses variables x; Cp scale -1',
        branch_evidence='NASA documented grid index order plus independent interpolation against published cp.wind.gen',
        published_WIND_vs_experiment_raw_ordinate_RMS=rms,
        original_raw_files_unchanged=True, own_CFD_used_to_choose_convention=False,
        source_URLs=[f'https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/{n}' for n in ('cfpost.cp.com','cp.exp.gen','cp.wind.gen')],
        source_sha256={n:hashlib.sha256((SOURCE/n).read_bytes()).hexdigest() for n in ('cfpost.cp.com','cp.exp.gen','cp.wind.gen')})
    (HERE/'CONVENCION_CP_VERIFICADA.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
