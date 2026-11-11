"""Scientific figures from computed tables, without rerunning the model."""
from pathlib import Path
import csv
import os
import numpy as np

HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'modulo_preliminar/mpl-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    rows=list(csv.DictReader((HERE/'modulo_preliminar/OPERACION_CONDICIONAL.csv').open()))
    mass_rows=list(csv.DictReader((HERE/'modulo_preliminar/MASA_MISION_5kg.csv').open()))
    fig,axes=plt.subplots(1,2,figsize=(13,5.4))
    for mass,color in ((2,'#317A91'),(5,'#DF8C32'),(10,'#7156A5')):
        values=[r for r in rows if float(r['mass_target_kg'])==mass and float(r['force_transfer_ASSUMED'])==.85 and r['maneuver']=='hover']
        axes[0].plot([float(r['rotor_diameter_mm']) for r in values],
                     [float(r['electrical_W_eta_0_9_ASSUMED'])/1000 for r in values],
                     'o-',color=color,label=f'{mass} kg objetivo')
    axes[0].set(xlabel='Diámetro del rotor [mm]',ylabel='Potencia de cuatro módulos [kW]',title='Estacionario: sensibilidad de diámetro')
    axes[0].legend()
    for factor,color in ((1.,'#317A91'),(1.25,'#DF8C32')):
        values=[r for r in mass_rows if float(r['diameter_factor'])==factor and r['peak_maneuver']=='hover' and float(r['pack_specific_power_W_kg_ASSUMED'])==5000]
        axes[1].plot([float(r['duration_total_s']) for r in values],
                     [float(r['remaining_for_other_hardware_and_changes_kg']) for r in values],
                     'o-',color=color,label=f'D={82*factor:g} mm')
    axes[1].axhline(0,color='#913A3A',lw=1)
    axes[1].set(xlabel='Duración total en estacionario [s]',ylabel='Masa aún disponible [kg]',title='5 kg: presupuesto parcial con batería')
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=.2)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('CRIBADO CONDICIONAL C01 — no es rendimiento validado',fontsize=14)
    fig.text(.5,.016,'κ=0,85; η eléctrica=0,90. Panel derecho: 150 Wh/kg y 5 kW/kg supuestos; otros equipos siguen sin cerrar.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.045,1,.94])
    fig.savefig(HERE/'modulo_preliminar/COMPROMISOS.png',dpi=170)
    plt.close(fig)


if __name__=='__main__':
    main()
