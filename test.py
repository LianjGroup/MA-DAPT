import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit


path=r'Excel_processed\Al1mm_SDB.xlsx'


angle1='RD'
angle2='DD'

# add function to show the difference between work equiv and actual 
#save the new data 
    # maaybe same file witha  new sheet
    
def equiv_calc(path,angle1,angle2):
    print(path,angle1,angle2)
    from scipy.integrate import cumulative_trapezoid
    from scipy.interpolate import interp1d
    from scipy.optimize import curve_fit
    data_frame = pd.read_excel(path, header=[0,1,2], index_col=0)


    stress_ref = data_frame[f'SDB_{angle1}_1']['Calculation']['True stress'].dropna()  # true stress
    strain_ref = data_frame[f'SDB_{angle1}_1']['Calculation']['Y True strain'].dropna()  # true strain


    ref_work = cumulative_trapezoid(strain_ref, stress_ref, initial=0)


    # get strain from refrence work by using inverse
    work_ref_interp = interp1d(ref_work, strain_ref, bounds_error=False, fill_value="extrapolate")



    strain_theta = data_frame[f'SDB_{angle2}_1']['Calculation']['Y True strain'].dropna().values
    stress_theta = data_frame[f'SDB_{angle2}_1']['Calculation']['True stress'].dropna().values
    work_theta = cumulative_trapezoid(strain_theta, stress_theta, initial=0)

    strain_eq_theta = work_ref_interp(work_theta)


    plt.figure(figsize=(10, 6))

    plt.plot(strain_ref, stress_ref, 'b-', label=f"{angle1}")
    plt.plot(strain_theta, stress_theta, 'g--', label=f"Raw {angle2}")
    plt.plot(strain_eq_theta, stress_theta, 'r-', label=f"Work-equivalent {angle2}")
    plt.xlabel("Equivalent Plastic Strain")
    plt.ylabel("True Stress")
    plt.legend()
    plt.grid(True)
    plt.show()
    


 

equiv_calc(path,angle1,angle2)