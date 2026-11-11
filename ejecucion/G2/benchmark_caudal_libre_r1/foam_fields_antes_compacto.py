"""Strict internal-field reader for uncompressed ASCII OpenFOAM scalar/vectors."""
from pathlib import Path
import re
import numpy as np

def read_internal(path,expected_cells,components=1):
    if components not in (1,3):raise ValueError('Only scalar/vector fields supported')
    text=Path(path).read_text()
    match=re.search(r'internalField\s+nonuniform\s+List<(scalar|vector)>\s+(\d+)\s*\(\s*\n',text)
    if match:
        if match[1]!=('vector' if components==3 else 'scalar'):raise ValueError('Wrong field type')
        if int(match[2])!=expected_cells:raise ValueError('Wrong cell count')
        end=text.find('\n)',match.end())
        if end<0:raise ValueError('Truncated internal field')
        values=np.fromstring(text[match.end():end].replace('(',' ').replace(')',' '),sep=' ')
        if values.size!=expected_cells*components:raise ValueError('Truncated or malformed values')
        values=values.reshape(expected_cells,3) if components==3 else values
    else:
        match=re.search(r'internalField\s+uniform\s+([^;]+);',text)
        if not match:raise ValueError('Missing supported internal field')
        values=np.fromstring(match[1].replace('(',' ').replace(')',' '),sep=' ')
        if values.size!=components:raise ValueError('Wrong uniform component count')
        values=np.tile(values,(expected_cells,1)) if components==3 else np.full(expected_cells,values[0])
    if not np.isfinite(values).all():raise ValueError('Nonfinite field')
    return values
