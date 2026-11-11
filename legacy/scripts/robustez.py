"""Sensitivity of the conditional model to actuator mismatch and maneuver duration."""
import csv
from dinamica import simulate, OUT

def main():
    rows=[]
    for duration in [.5,.8,1.2]:
        for tau in [.03,.07,.15]:
            result,_=simulate(tau,True,90,duration=duration,estimated_tau=.07)
            rows.append(result)
    with (OUT/'robustez_dinamica_CONDICIONAL.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
if __name__=='__main__':main()
