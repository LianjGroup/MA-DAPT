import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os
import yaml
from io import BytesIO
#from scipy.optimize import curve_fit
#from scipy.interpolate import CubicSpline
#from openpyxl import load_workbook
# import numpy



'''Organize all the functions in the script'''


#Default values
# add option to change the default values in settings 
 
# set the default values for the plot
 

legend_on=True

def configs():
    with open(f'Script{os.sep}config.yaml') as file:
        config = yaml.full_load(file)


    plt.rcParams.update({
        'font.family': config['matplotlib']['font']['family'],
        'font.size': config['matplotlib']['font']['size'],
        'axes.labelsize': config['matplotlib']['font']['size'],
        'axes.titlesize': config['matplotlib']['font']['size'],
        'legend.fontsize': config['matplotlib']['font']['size']
    })
    global legend_on
    legend_on=config['matplotlib']['legend']
     

configs()


def xy_values(func_name):
    if func_name == "engineering":
        x_name = "Eng. Strain"
        y_name = "Eng. Stress"
        xlabel="Eng.strain, -"
        ylabel="Eng.stress, MPa"

    elif func_name == "true":
        x_name = "Y True strain"
        y_name = "True stress"
        xlabel=x_name+", -"
        ylabel=y_name+", MPa"
    elif func_name == "effective plastic strain":
        x_name = "Effective plastic strain"
        y_name = "True stress"
        xlabel=x_name+", -"
        ylabel=y_name+", MPa"
    elif func_name == "r-value":
        x_name = "Y True strain"      #Create another ?????
        y_name = "r-value"
        xlabel=x_name+", -"
        ylabel=y_name+", -"
    else: 
        print('invalid parameter, must be 1-4')
        return
    return x_name,y_name,xlabel,ylabel

def repeatablity (path,sheet_name,func_name,setting_fn=None):
    print(f"repeatablity({path},{sheet_name},{func_name})")
   
    x_name,y_name,xlabel,ylabel=xy_values(func_name)
    print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
    print(x_name,y_name,xlabel,ylabel)
    print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()
    #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]
    buffers = []

    for dire in directions:
        
        totalx=[]
        totaly=[]
        plt.clf()
        for i in range(6):
            test_name = f'{geo_name}_{dire}_{i+1}'
            try:
                x = data_frame[test_name]["Calculation"][x_name]
                y = data_frame[test_name]["Calculation"][y_name]
                start_index = x[x > 0.0001].index[0]  
                x = x.loc[start_index:]          
                y = y.loc[start_index:] 

                totalx.append(x)
                totaly.append(y)
                print(f"test{len(x)}")
                print(f"lest{len(y)}")

                plt.plot(x,y,label=f'{i+1}')
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
            except KeyError:
                continue
            except IndexError:
                continue

            

        if func_name == "r-value":
            
            tx= sum(totalx)/(len(totalx))
            ty= sum(totaly)/(len(totaly))
            print(f"best{len(tx)}")
            print(f"nest{len(ty)}")

            plt.xlim(left=(0.01))
            plt.plot(tx,ty,label="Average")
            #plt.ylim([0,2])


        plt.legend()
        plt.title("SDB-"+dire)
        if setting_fn:
            setting_fn()
        #plt.show()

        #print(f"{dire}.jpg")
        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', bbox_inches='tight')
        buffer.seek(0)  # Reset buffer's position to the start
        buffers.append(buffer)
    return buffers

def compare(address,materials,func_name,setting_fn=None):
    plt.clf()
    colors=['b', 'g', 'r', 'c','m', 'y', 'k']
    x_name,y_name,xlabel,ylabel=xy_values(func_name)

    for i,material in enumerate(materials):
        path = f"{address}{os.sep}{material}.xlsx"
        data_frame = pd.read_excel(path,sheet_name="Sheet1",header=([0,1,2]),index_col=0)
        test_name = f'SDB_RD_1'
        x = data_frame[test_name]["Calculation"][x_name]
        y = data_frame[test_name]["Calculation"][y_name]
        if x.isna().any() or y.isna().any():
            test_name = 'SDB_RD_2'
            x = data_frame[test_name]["Calculation"][x_name]
            y = data_frame[test_name]["Calculation"][y_name]
        material_name, separator, remainder = material.partition('_')
        plt.plot(x,y,label=f'{material_name}',color=colors[i])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    plt.legend()
    if func_name == "r-value":
        plt.ylim([0,2])
    if setting_fn:
        setting_fn()
    #plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()
    
def FDset():
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 16
    plt.xlabel("Displacement, -")
    plt.ylabel("Force, kN")
    plt.xlim([0,2.5])
    plt.ylim([0,14])
    plt.legend()

def FDplot(series_list):
    plt.clf()
    # Iterate over each series in the list
    for series in series_list:
        # Read the Excel sheet
        sheet = pd.read_excel(series["path"], series["sheetname"], header=[0,1])
        mainID = series["mainID"]
        
        # Extract x and y data, dropping NaN values
        x = sheet[mainID][series["x_name"]].dropna()
        y = sheet[mainID][series["y_name"]].dropna()
        
        # Check if x or y data is empty
        if x.empty or y.empty:
            print(f"Data for series {series.get('label', mainID)} is empty. Skipping this series.")
            continue  # Skip to the next series
        
        # Retrieve plotting parameters with defaults
        label = series.get('label', None)
        color = series.get('color', 'black')
        mark_end = series.get('mark_end', False)
        line_style = series.get('line_style', '-')
        linewidth = series.get("linewidth", 1.5)
        
        # Plotting logic
        if label is None:
            if mark_end:
                plt.plot(x, y, color=color, linestyle=line_style, linewidth=linewidth)
                plt.scatter(x.iloc[-1], y.iloc[-1], s=70, marker="*", color=color)
            else:
                plt.plot(x, y, color=color, linestyle=line_style, linewidth=linewidth)
        else:
            if mark_end:
                plt.plot(x, y, label=label, color=color, linestyle=line_style, linewidth=linewidth)
                plt.scatter(x.iloc[-1], y.iloc[-1], s=70, marker="*", color=color)
            else:
                plt.plot(x, y, label=label, color=color, linestyle=line_style, linewidth=linewidth)
                
    # Display legend if any labels are provided
    if any('label' in series for series in series_list):
        plt.legend()
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 16
    plt.xlabel("Displacement, mm")
    plt.ylabel("Force, kN")
 

def calculate_youngs_modulus(strain, stress, stress_limit=500):
    
    mask = stress > stress_limit
    if np.any(mask):
        first_index = np.argmax(mask)

 

    strain_elastic = strain[:first_index]
    stress_elastic = stress[:first_index]

    if len(strain_elastic) < 2:
        print("Not enough data in the elastic range.")
        return 
    
    slope, intercept, r_value, _, _ = stats.linregress(strain_elastic, stress_elastic)
    return slope


def calculation(path,sheet_name,stress_limit=500,modified=False):
    print(f"calculation({path},{sheet_name},{stress_limit},{modified})")
    
    max_youngs= get_max_E(path,sheet_name,stress_limit)

    data_frame=pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]))
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}

    for key in tests_series.keys():
        test_name = key
        tests_info=pd.read_excel(path,sheet_name="Tests_info",header=[0],index_col="Tests")
        
        try:
            S0 = tests_info.loc[test_name,"S0"]
        except KeyError:
            print("Can't find the area of cross section")
            continue
        Force = data_frame[test_name]["Machine"]["Force"]
        y_strain = 100*data_frame[test_name]["DIC_Y"]["∆L/L0"]
        x_strain = 100*data_frame[test_name]["DIC_X"]["∆L/L0"]
        eng_stress = (Force/S0)*1000
        print("dea")


        Young_Modulus = calculate_youngs_modulus(y_strain/100,eng_stress,stress_limit)
        if modified:
            group_name = "_".join(test_name.split("_")[:2])
            new_Youngs = max_youngs[group_name]
            y_strain = y_strain-100*eng_stress/Young_Modulus+100*eng_stress/new_Youngs
        # find out the index with highest engineering stress
        max_stress_idx = np.argmax(eng_stress)
        eng_stress_max = eng_stress[:max_stress_idx+1]
        y_strain_max = y_strain[:max_stress_idx+1]
        x_strain_max = x_strain[:max_stress_idx+1]
        true_stress = eng_stress_max*(1+y_strain_max/100)
        y_true_e = np.log(1+y_strain_max/100)
        x_true_e = np.log(1+x_strain_max/100)
        # calculate strain in thichness
        if "DIC_Z" not in data_frame[test_name] or data_frame[test_name]["DIC_Z"]["∆L/L0"].isna().all():
            z_true_e = -x_true_e - y_true_e
        else:
            z_strain = 100 * data_frame[test_name]["DIC_Z"]["∆L/L0"]
            z_true_e = np.log(1 + z_strain / 100)
        r_value = np.where(z_true_e != 0, x_true_e/z_true_e, 0)
        print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")

        print(y_true_e)
        print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
        print(true_stress)
        print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

        print(Young_Modulus)
        if Young_Modulus==None:
            Young_Modulus=0
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")



        print(true_stress/Young_Modulus)
        print("PPPPPPPPPPPPPPPPPPPPPPPP")
        print(y_true_e)
        effective_strain = y_true_e-true_stress/Young_Modulus
        print("QQQQQQQQQQQQQQQQQQQQQQQQQ")
        print(effective_strain)
        
        data_frame.loc[:, (test_name, 'Calculation', 'Eng. Strain')] = y_strain
        data_frame.loc[:, (test_name, 'Calculation', 'Eng. Stress')] = eng_stress
        data_frame.loc[:, (test_name, 'Calculation', 'True stress')] = true_stress
        data_frame.loc[:, (test_name, 'Calculation', 'Y True strain')] = y_true_e
        data_frame.loc[:, (test_name, 'Calculation', 'X True strain')] = x_true_e
        data_frame.loc[:, (test_name, 'Calculation', 'Thickness strain')] = z_true_e
        data_frame.loc[:len(r_value)-1, (test_name, 'Calculation', 'r-value')] = r_value
        data_frame.loc[:,(test_name,"Calculation","Effective plastic strain")] = effective_strain
        data_frame.loc[0,(test_name,"Calculation","Young's modulus")] = Young_Modulus


        #return 0
    
    
    data_frame.to_excel(f"Excel_processed/11{sheet_name}.xlsx")


def get_max_E(path,sheet_name,stress_limit=500):
    print(f"get_max_E({path},{sheet_name},{stress_limit})")
    data_frame=pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]))
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
     # Obtain the cross section area from sheet "Tests_info"
    tests_info=pd.read_excel(path,sheet_name="Tests_info",header=[0],index_col="Tests")
    Youngs = {}
    for key,value in tests_series.items():
        test_name = key
        try:
            S0 = tests_info.loc[test_name,"S0"]
        except KeyError:
            print("Can't find the area of cross section")
            continue
        Force = data_frame[test_name]["Machine"]["Force"]
        y_strain = data_frame[test_name]["DIC_Y"]["∆L/L0"]
        eng_stress = Force/S0*1000

        print("CCCCCCCCCC\n", eng_stress)
        print("DDDDDDDDDDDD\n", y_strain)

  
        Young_Modulus = calculate_youngs_modulus(y_strain,eng_stress,stress_limit)
        print("HHHHHHHHHHHHH\n", y_strain)

        group_name = "_".join(key.split('_')[:2])
        #return 0
        Youngs.setdefault(group_name, []).append(Young_Modulus)
    
    print("IIIIIIIIIIIIIIIIIIIIII")
    #max_E = {key:max(values) for key, values in Youngs.items()}
    max_values = {}
    print(Youngs.items())
    print("JJJJJJJJJJJJJJJJJ")
    non_empty_values = [value for values in Youngs.items() for value in values if value is not None]
    print(non_empty_values)
    for key, values in Youngs.items():
        filtered_values = [item for item in values if item is not None]
        print(filtered_values)
        if filtered_values:
            max_values[key] = max(filtered_values)
        else:
            max_values[key] = 0

    print("DICK")
    max_E = max_values

    return max_E
 

 

 ############

def rvalue(path,sheet_name):
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)

    r_table = data_frame.loc[:, data_frame.columns.get_level_values(2) ==  "r-value"]
    r_list = [r_table[col].tolist() for col in r_table] 
   
    non_null_r = [[x for x in r if x == x] for r in r_list]
   
    strain_table = data_frame.loc[:, data_frame.columns.get_level_values(2) == 'Effective plastic strain']
    strain_list = [strain_table[col].tolist() for col in strain_table] 

    non_null_strain=[[x for x in s if x == x] for s in strain_list]
   
   
    print(len(non_null_r[2]))
    print(len(non_null_strain[2]))

    for r_cur,stain_cur in zip(non_null_r,non_null_strain):
        if len(r_cur) < len(stain_cur):
            r_cur = r_cur + [r_cur[-1]] * (len(stain_cur) - len(r_cur))
            plt.plot( stain_cur,r_cur)        
            plt.show()



 
def custom_plot(path,tests_list,func_name,setting_fn=None):
    plt.clf()

    x_name,y_name,xlabel,ylabel=xy_values(func_name)

    data_frame = pd.read_excel(path,sheet_name="Sheet1",header=([0,1,2]),index_col=0)
    for test_name in tests_list:
        try:
            x = data_frame[test_name]["Calculation"][x_name]
            y = data_frame[test_name]["Calculation"][y_name]
            label = test_name.split("_",1)[1]
            plt.plot(x, y, label=f'{label}')
        except KeyError:
            print(f"Test {test_name} not found in data")
            continue
    # plot setting 
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if func_name == "r-value":
        plt.ylim([0,2])
    plt.legend()
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 16
    plt.title(f'Custom plot')
    if setting_fn:
        setting_fn()
    print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
    #plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()

def uts_plot(path,sheet_name):
    #plot the direction dependency of properties.
    plt.clf()
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()     
     #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    directions_ordered = ['RD', '15', '30', 'DD', '60', '75', 'TD']
    number_directions_ordered = ['0', '15', '30', '45', '60', '75', '90']

    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]
    avg_uts_list = []
    avg_elongation_list = []
    final_directions = []
    for dire in directions_ordered:
        uts_values = []
        strain_at_uts_values = []
        te_values=[]
        for i in range (1,4):
            test_name=f'{geo_name}_{dire}_{i}'
            try:
                x = data_frame[test_name]["Calculation"]["Eng. Strain"]
                y = data_frame[test_name]["Calculation"]["Eng. Stress"]
                uts = y.max()
                strain_at_uts = x[y.idxmax()]
                uts_values.append(uts)
                strain_at_uts_values.append(strain_at_uts)
                
                te=x.max()
                te_values.append(te)

                 


            except KeyError:
                print(f"Test {test_name} not found in data")
                continue
        if uts_values:
            avg_uts = sum(uts_values) / len(uts_values)
            avg_elongation = sum(strain_at_uts_values) / len(strain_at_uts_values)
            avg_uts_list.append(avg_uts)
            avg_elongation_list.append(avg_elongation) 
            final_directions.append(dire)
    fig, ax1 = plt.subplots(figsize=(6.4,4.8))

    ax1.set_xlabel('Direction')
    ax1.set_ylabel('UTS, MPa', color='tab:red')
    ax1.plot(final_directions, avg_uts_list, color='tab:red', marker='o', label='Avg UTS (MPa)')
   
    #ax1.plot(final_directions, avg_uts_list, color='tab:red', marker='o', label='Avg UTS (MPa)')
   
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Elonation, %', color='tab:blue')
    ax2.plot(final_directions, avg_elongation_list, color='tab:blue', marker='s', label='Avg elongation at UTS')
    ax2.tick_params(axis='y', labelcolor='tab:blue')



    dead = ['0', '15', '30', '45', '60', '75', '90']
    #plt.xticks(final_directions,dead)

    
    plt.rcParams['font.size'] = 14
    fig.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()    
 ################



def orientation (path,sheet_name,func_name,dire_test,setting_fn=None):
    plt.clf()
    x_name,y_name,xlabel,ylabel=xy_values(func_name)

    #plot the direction dependency of properties.
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()     
     #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]
    for dire, test_number in dire_test.items():
        test_name = f'{geo_name}_{dire}_{test_number}'  # the name of test
        try:
            x = data_frame[test_name]["Calculation"][x_name]
            y = data_frame[test_name]["Calculation"][y_name]
            start_index = x[x > 0.0001].index[0]  
            x = x.loc[start_index:]          
            y = y.loc[start_index:] 
            plt.plot(x, y, label=f'{dire}-{test_number}')
        except KeyError:
            print(f"Test {test_name} not found in data")
            continue
    # plot setting 
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if func_name == "r-value":
        plt.ylim([0,2])
    plt.legend()
    plt.title(f'{geo_name}: Comparison of All Directions')
    if setting_fn:
        setting_fn()
    #plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()

def fracture_repeat(path,sheet_name,setting_fn=None):

    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    old_list = data_frame.columns.get_level_values(0).unique().tolist()
    new_list = list({s.rsplit('_', 1)[0] for s in old_list})
    buffers = []
    for index, test in enumerate(new_list):
        plt.clf()
        for i in range(3): 
            try:
                x = data_frame[f'{str(test)}_{i+1}']["Disp_Y"]["∆L [mm]"].dropna()
                y = data_frame[f'{str(test)}_{i+1}']["Machine"]["Force"].dropna()
                plt.plot(x,y,label=i+1)
                if not x.empty and not y.empty:
                    plt.scatter(x.iloc[-1], y.iloc[-1], s=70, marker="*")
            except KeyError:
                continue
        plt.xlabel("Displacement, mm")
        plt.ylabel("Force, kN")
        plt.title(test)
        plt.legend()
        if setting_fn:
            setting_fn()


        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', bbox_inches='tight')
        buffer.seek(0)  # Reset buffer's position to the start
        buffers.append(buffer)
    return buffers
    

def fracture_normal_compare(path,sheet_names,setting_fn=None):
    print("Sssssssssssssssssssssssssss")

#     dataframes=[]
#     for sheet_name in sheet_names:
#         data_frame.append(pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
# )


    data_frame = pd.read_excel(path,sheet_name="SH",header=([0,1,2]),index_col=0)
    data_frame1 = pd.read_excel(path,sheet_name="CHD6",header=([0,1,2]),index_col=0)
    
    old_list = data_frame.columns.get_level_values(0).unique().tolist()
    new_list = list({s.rsplit('_', 1)[0] for s in old_list})
    buffers = []
    for index, test in enumerate(new_list):
        plt.clf()
        for i in range(3): 
            try:
                x = data_frame[f'{str(test)}_{i+1}']["Disp_Y"]["∆L [mm]"].dropna()
                y = data_frame[f'{str(test)}_{i+1}']["Machine"]["Force"].dropna()
                plt.plot(x,y,label=i+1)
                a = data_frame1[f'CHD6{str(test)[-3:]}_{i+1}']["Disp_Y"]["∆L [mm]"].dropna()
                b = data_frame1[f'CHD6{str(test)[-3:]}_{i+1}']["Machine"]["Force"].dropna()
                plt.plot(a,b,label=i+1)
                if not x.empty and not y.empty:
                    plt.scatter(x.iloc[-1], y.iloc[-1], s=70, marker="*")
                if not a.empty and not b.empty:
                    plt.scatter(a.iloc[-1], b.iloc[-1], s=70, marker="*")

            except KeyError:
                continue

        plt.xlabel("Displacement, mm")
        plt.ylabel("Force, kN")
        plt.title(test)
        handles, labels = plt.gca().get_legend_handles_labels()
        unique = dict(zip(labels, handles))  # Removes duplicates by keeping only the last occurrence
        plt.legend(unique.values(), unique.keys())

        if setting_fn:
            setting_fn()


        buffer = BytesIO()
        plt.savefig(buffer, format='PNG', bbox_inches='tight')
        buffer.seek(0)  # Reset buffer's position to the start
        buffers.append(buffer)
    return buffers
    

def fracture_summary(path,sheet_name,setting_fn=None):
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    old_list = data_frame.columns.get_level_values(0).unique().tolist()
    new_list = list({s.rsplit('_', 1)[0] for s in old_list})
    plt.clf()
    for index, test in enumerate(new_list):
        try:
            x = data_frame[f'{str(test)}_{2}']["Disp_Y"]["∆L [mm]"].dropna()
            y = data_frame[f'{str(test)}_{2}']["Machine"]["Force"].dropna()
            plt.plot(x,y,label=str(test)[-2:])
            if not x.empty and not y.empty:
                plt.scatter(x.iloc[-1], y.iloc[-1], s=70, marker="*")
        except KeyError:
            continue
        except ValueError:
            min_len = min(len(x), len(y))
            x = x.iloc[:min_len]
            y = y.iloc[:min_len]
            plt.plot(x,y,label=str(test)[-2:])

            
        plt.xlabel("Displacement, mm")
        plt.ylabel("Force, kN")
        plt.title(sheet_name)
        plt.legend()
        if setting_fn:
            setting_fn()


    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    
    return buffer
    

def fracture_compare_summary(path,sheet_names,setting_fn=None):
    plt.clf()

    label_color_map = {}
    color_list = ["blue", "red", "green", "blue", "red", "green", "blue", "red", "green"]
    color_no = 0
    for sheet_name in sheet_names:
        data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
        old_list = data_frame.columns.get_level_values(0).unique().tolist()
        new_list = list({s.rsplit('_', 1)[0] for s in old_list})
        for index, test in enumerate(new_list):
            try:
                x = data_frame[f'{str(test)}_{2}']["Disp_Y"]["∆L [mm]"].dropna()
                y = data_frame[f'{str(test)}_{2}']["Machine"]["Force"].dropna()
                label=str(test)[-2:]
                if label not in label_color_map:
                    label_color_map[label] = color_list[color_no % len(color_list)]
                    color_no += 1
                plt.plot(x,y,label=label,color=label_color_map[label])
                if not x.empty and not y.empty:
                    plt.scatter(x.iloc[-1], y.iloc[-1], s=70, color=label_color_map[label],marker="*")
            except KeyError:
                continue
            except ValueError:
                min_len = min(len(x), len(y))
                x = x.iloc[:min_len]
                y = y.iloc[:min_len]
                plt.plot(x,y,label=str(test)[-2:])

                
            plt.xlabel("Displacement, mm")
            plt.ylabel("Force, kN")
            plt.legend()

            if setting_fn:
                setting_fn()

    handles, labels = plt.gca().get_legend_handles_labels()
    unique = dict(zip(labels, handles))  # Removes duplicates by keeping only the last occurrence
    plt.legend(unique.values(), unique.keys())


    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    
    return buffer
    



















def summary(path,sheet_name,func_name,letters=False,setting_fn=None):
    plt.clf()
    
    x_name,y_name,xlabel,ylabel=xy_values(func_name)
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()
    #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]
    buffers = []
    if letters:
        directions = ['RD', 'DD', 'TD']
    for dire in directions:
        test_name = f'{geo_name}_{dire}_{2}'
        x = data_frame[test_name]["Calculation"][x_name]
        y = data_frame[test_name]["Calculation"][y_name]
        start_index = x[x > 0.0001].index[0]  
        x = x.loc[start_index:]          
        y = y.loc[start_index:] 

        plt.plot(x,y,label=f'{dire}',)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if func_name == "r-value":
        plt.xlim(left=(0.01))
        plt.ylim([0,2])
    plt.legend()
    plt.title(func_name)
 

    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()



def Normalized_plot(path,quality="Displacement"):
    #plot the direction dependency of properties.
    
    row1="Disp_Y"			
    row2="∆L [mm]"			

    if quality=="Force":
        row1="Machine"			
        row2="Force"			

    plt.clf()
 
    rdx=[]
    ddx=[]
    tdx=[]
    yyy=[]
    sheet_names=[ 'NDBR25', 'NDBR6', 'NDBR2', 'NDBR02', 'SH','CHD6']

    for sheet_name in sheet_names:
        data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
        old_list = data_frame.columns.get_level_values(0).unique().tolist()
        new_list = list({s.rsplit('_', 1)[0] for s in old_list})
        for test in (new_list):
            print(sheet_name+"AND "+test)

            #print(test)
            x = data_frame[f'{str(test)}_{1}'][row1][row2].dropna()
            if ((str(test)[-2:])=="DD"):
                try:
                    ddx.append((x.iloc[-1:]).tail(1).values[0])
                except IndexError:
                    ddx.append(None)

            if ((str(test)[-2:])=="RD"):
                try:
                    rdx.append((x.iloc[-1:]).tail(1).values[0])
                except IndexError:
                    rdx.append(None)            
            if ((str(test)[-2:])=="TD"):
                try:
                    tdx.append((x.iloc[-1:]).tail(1).values[0])
                except IndexError:
                    tdx.append(None)


    result_rd = [a / b if a is not None and b is not None else None for a, b in zip(rdx, rdx)]
    result_dd = [a / b if a is not None and b is not None else None for a, b in zip(ddx, rdx)]
    result_td = [a / b if a is not None and b is not None else None for a, b in zip(tdx, rdx)]

    print(result_rd)
    print(result_dd)
    print(result_td)

    print(yyy)


 

    plt.plot(sheet_names, result_rd, 'o-', label='RD', color='green')
    plt.plot(sheet_names, result_dd, '^-', label='DD', color='red')
    plt.plot(sheet_names, result_td, 's-', label='TD', color='blue')

     
    plt.legend()
    
    plt.ylabel(f"Normalized fracture {quality}, -")

    plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()
   
 ################



 ################





















###########REMAKE

def fracture_compare(path,sheet_name,materials,setting_fn=None):
    plt.clf()
    print("hhhhhhhhhhhhhhhh")
    print(materials)
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    old_list = data_frame.columns.get_level_values(0).unique().tolist()
    new_list = list({s.rsplit('_', 1)[0] for s in old_list})
 
























def r_plot(path,sheet_name):
    #plot the direction dependency of properties.
    plt.clf()
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()     
     #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    directions_ordered = ['RD', '15', '30', 'DD', '60', '75', 'TD']
    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]
    avg_uts_list = []
    avg_elongation_list = []
    final_directions = []
    for dire in directions_ordered:
        uts_values = []
        strain_at_uts_values = []
        for i in range (1,4):
            test_name=f'{geo_name}_{dire}_{i}'
            try:
                x = data_frame[test_name]["Calculation"]["Eng. Strain"]
                y = data_frame[test_name]["Calculation"]["r-value"]
                uts = y.max()
                strain_at_uts = x[y.idxmax()]
                uts_values.append(uts)
                strain_at_uts_values.append(strain_at_uts)
            except KeyError:
                print(f"Test {test_name} not found in data")
                continue
        if uts_values:
            avg_uts = sum(uts_values) / len(uts_values)
            avg_elongation = sum(strain_at_uts_values) / len(strain_at_uts_values)
            
            avg_uts_list.append(avg_uts)
            avg_elongation_list.append(avg_elongation) 
            final_directions.append(dire)
    fig, ax1 = plt.subplots(figsize=(6.4,4.8))

    ax1.errorbar(final_directions, avg_uts_list, yerr=len(uts_values), color='tab:red', marker='o', label='Avg UTS (MPa)')
    ax1.set_xlabel('Direction')
    ax1.set_ylabel('R-values', color='tab:red')
    ax1.plot(final_directions, avg_uts_list, color='tab:red', marker='o', label='Avg R-value')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Elonation, %', color='tab:blue')
    ax2.plot(final_directions, avg_elongation_list, color='tab:blue', marker='s', label='Avg elongation at R value')
    ax2.tick_params(axis='y', labelcolor='tab:blue')


    dead = ['0', '15', '30', '45', '60', '75', '90']

    plt.xticks(final_directions,dead)

    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 14
    fig.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()    
 ################







# def falcon (path,sheet_name,func_name,setting_fn=None):

#     x_name,y_name,xlabel,ylabel=xy_values(func_name)
#     data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
#     tests_list = data_frame.columns.get_level_values(0).unique().tolist()
#     tests_series = {s : s.split('_', 2)[1] for s in tests_list}
#     directions = list(set(tests_series.values()))
#     geo_name = tests_list[0].split("_",1)[0]
#     buffers = []
#     for dire in directions:
#         plt.clf()
#         for i in range(6):
#             test_name = f'{geo_name}_{dire}_{i+1}'
#             try:
#                 x = data_frame[test_name]["Calculation"][x_name]
#                 y = data_frame[test_name]["Calculation"][y_name]
#                 youngs_modulus = data_frame[test_name]["Calculation"]["Young's modulus"][0]
#                 print(youngs_modulus)
#                 start_index = x[x > 0.0001].index[0]  
#                 x = x.loc[start_index:]          
#                 y = y.loc[start_index:] 
#                 print("EE",find_yield_stress(y,x,youngs_modulus))
#                 plt.plot(x,y,label=f'{i+1}')
#                 plt.xlabel(xlabel)
#                 plt.ylabel(ylabel)
#             except KeyError:
#                 continue
#         if func_name == "r-value":
            
#             plt.ylim([0,2])
#         plt.legend()
#         plt.title(dire)
#         plt.rcParams['font.family'] = 'Arial'
#         plt.rcParams['font.size'] = 16
#     return buffers

 

# def find_yield_stress(stress, strain, youngs_modulus, offset=0.002):
#     stress = np.array(stress)
#     strain = np.array(strain)
    
#     # Calculate the offset line: σ_offset = E * (strain + offset)
#     offset_line = youngs_modulus/100 * (strain + offset)
    
#     # Find the first point where stress exceeds offset line
#     for i in range(1, len(stress)):
#         #print(stress[i],"FUCK",offset_line[i])
#         if stress[i] >= offset_line[i]:
#             # Interpolate to get a more precise yield stress
#             yield_stress = np.interp(
#                 offset_line[i],  # Target value
#                 stress[i-1:i+1],  # Stress values around the intersection
#                 stress[i-1:i+1]  # Strain values around the intersection
#             )
#             return yield_stress

#     return None  # If no intersection is found

# # Example Usage
 

# def find_intersection_points(x1, y1, x2, y2):
#     intersections = []

#     for i in range(len(x1) - 1):
#         # Check if there is a sign change between y1[i] - y2[i] and y1[i+1] - y2[i+1]
#         if (y1[i] - y2[i]) * (y1[i + 1] - y2[i + 1]) < 0:
#             # Linear interpolation to find x where y1 = y2
#             x_intersect = x1[i] + (x1[i + 1] - x1[i]) * abs(y1[i] - y2[i]) / (abs(y1[i] - y2[i]) + abs(y1[i+1] - y2[i+1]))
#             y_intersect = y1[i] + (y1[i + 1] - y1[i]) * (x_intersect - x1[i]) / (x1[i+1] - x1[i])
            
#             intersections.append((x_intersect, y_intersect))

#     return intersections



def get_yield_stress(x,y,youngs_modulus):
    elasticStress=((youngs_modulus/100)*(x-2))  ## CHECK WHAT PROPER OFFSET SHOULD BE
    elasticStress = [i for i in elasticStress if i <= max(y)]  
    diff = np.abs(y[:len(elasticStress)] - elasticStress)
    idx = np.argmin(diff)  # Index of the closest match



    return idx


def yield_stress_plot(path,sheet_name):
    #plot the direction dependency of properties.
    plt.clf()
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()     
     #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    directions_ordered = ['RD', '15', '30', 'DD', '60', '75', 'TD']
 
    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]

    final_directions = []


    avg_yield_stress_list=[]
    avg_r_value_list=[]

    max_yield_stress_list=[]
    max_r_value_list=[]

    min_r_value_list=[]
    min_yield_stress_list=[]

    for dire in directions_ordered:



        yield_stress=[]
        r_value=[]


        for i in range (1,4):
            test_name=f'{geo_name}_{dire}_{i}'
            try:
                x = data_frame[test_name]["Calculation"]["Eng. Strain"]
                y = data_frame[test_name]["Calculation"]["Eng. Stress"]
                all_r_values = data_frame[test_name]["Calculation"]["r-value"]


                young_modulus = data_frame[test_name]["Calculation"]["Young's modulus"].head()[0]
                id=get_yield_stress(x,y,young_modulus)
                
                
                yield_stress.append(y[id])
                r_value.append(all_r_values[id])

            except KeyError:
                print(f"Test {test_name} not found in data")
                continue
        if yield_stress:

            max_yield_stress_list.append(max(yield_stress))
            max_r_value_list.append(max(r_value))
            

            min_yield_stress_list.append(min(yield_stress))
            min_r_value_list.append(min(r_value))
            
            avg_yield_stress=sum(yield_stress) / len(yield_stress)
            avg_r_value=sum(r_value) / len(r_value)

            avg_yield_stress_list.append(avg_yield_stress)
            avg_r_value_list.append(avg_r_value)
            final_directions.append(dire)




    fig, ax1 = plt.subplots(figsize=(6.4,4.8))

    ax1.set_xlabel('Direction, °')
    ax1.set_ylabel('E, MPa', color='tab:red')
   # ax1.plot(final_directions, avg_yield_stress_list, color='tab:red', marker='o', label='Yield Stress (MPa)')


    yield_err_upper = [yp_i - y_i for yp_i, y_i in zip(max_yield_stress_list, avg_yield_stress_list)]
    yield_err_lower = [y_i - ym_i for y_i, ym_i in zip(avg_yield_stress_list, min_yield_stress_list)]


    r_err_upper = [yp_i - y_i for yp_i, y_i in zip(max_r_value_list, avg_r_value_list)]
    r_err_lower = [y_i - ym_i for y_i, ym_i in zip(avg_r_value_list, min_r_value_list)]



    ax1.errorbar(final_directions, avg_yield_stress_list,
                yerr=[yield_err_lower, yield_err_upper], 
                color='tab:red', 
                marker='o', 
                label='Yield Stress (MPa)'
                ,capsize=5, capthick=1, elinewidth=1, errorevery=1)
    
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('R value, ', color='tab:blue')


    ax2.errorbar(final_directions, avg_r_value_list,
                yerr=[r_err_lower, r_err_upper], 
                color='tab:blue', 
                marker='o', 
                label='Rvalue at yield stress (MPa)'
                ,capsize=5, capthick=1, elinewidth=1, errorevery=1)
    
    
    ax2.tick_params(axis='y', labelcolor='tab:blue')
   
    ax1.tick_params(axis='y', labelcolor='tab:red')


    dead = ['0', '15', '30', '45', '60', '75', '90']
   # plt.xticks(final_directions,dead)

    
    print(min_yield_stress_list)

    print(avg_yield_stress_list)

    print(max_yield_stress_list)

    plt.rcParams['font.size'] = 14
    fig.tight_layout()
    buffer = BytesIO()
    plt.show()
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()    
 ################



def yield_r_plot(path,sheet_name):
    #plot the direction dependency of properties.
    plt.clf()
    data_frame = pd.read_excel(path,sheet_name=sheet_name,header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()     
     #assign direction to test number
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    directions_ordered = ['RD', '15', '30', 'DD', '60', '75', 'TD']
 
    #creat a list containing all directions
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]

    final_directions = []


    avg_yield_stress_list=[]
    avg_r_value_list=[]

    max_yield_stress_list=[]
    max_r_value_list=[]

    min_r_value_list=[]
    min_yield_stress_list=[]

    for dire in directions_ordered:



        yield_stress=[]
        r_value=[]


        for i in range (1,4):
            test_name=f'{geo_name}_{dire}_{i}'
            try:
                x = data_frame[test_name]["Calculation"]["Eng. Strain"]
                y = data_frame[test_name]["Calculation"]["Eng. Stress"]
                all_r_values = data_frame[test_name]["Calculation"]["r-value"]


                young_modulus = data_frame[test_name]["Calculation"]["Young's modulus"].head()[0]
                id=get_yield_stress(x,y,young_modulus)
                
                
                yield_stress.append(y[id])
                r_value.append(all_r_values[id])

            except KeyError:
                print(f"Test {test_name} not found in data")
                continue
        if yield_stress:

            max_yield_stress_list.append(max(yield_stress))
            max_r_value_list.append(max(r_value))
            

            min_yield_stress_list.append(min(yield_stress))
            min_r_value_list.append(min(r_value))
            
            avg_yield_stress=sum(yield_stress) / len(yield_stress)
            avg_r_value=sum(r_value) / len(r_value)

            avg_yield_stress_list.append(avg_yield_stress)
            avg_r_value_list.append(avg_r_value)
            final_directions.append(dire)




    fig, ax1 = plt.subplots(figsize=(6.4,4.8))

    ax1.set_xlabel('Direction, °')
    ax1.set_ylabel('E, MPa', color='tab:red')
   # ax1.plot(final_directions, avg_yield_stress_list, color='tab:red', marker='o', label='Yield Stress (MPa)')


    yield_err_upper = [yp_i - y_i for yp_i, y_i in zip(max_yield_stress_list, avg_yield_stress_list)]
    yield_err_lower = [y_i - ym_i for y_i, ym_i in zip(avg_yield_stress_list, min_yield_stress_list)]


    r_err_upper = [yp_i - y_i for yp_i, y_i in zip(max_r_value_list, avg_r_value_list)]
    r_err_lower = [y_i - ym_i for y_i, ym_i in zip(avg_r_value_list, min_r_value_list)]



 

    plt.errorbar(final_directions, avg_r_value_list,
                yerr=[r_err_lower, r_err_upper], 
                color='tab:blue', 
                marker='o', 
                label='Rvalue at yield stress (MPa)'
                ,capsize=5, capthick=1, elinewidth=1, errorevery=1)
    
    
    plt.tick_params(axis='y', labelcolor='tab:blue')
   

    dead = ['0', '15', '30', '45', '60', '75', '90']
   # plt.xticks(final_directions,dead)

    
    fig.tight_layout()
    buffer = BytesIO()
     
    plt.savefig(buffer, format='PNG', bbox_inches='tight')
    buffer.seek(0)  # Reset buffer's position to the start
    return buffer.getvalue()    
 ################








def main():

    yield_stress_plot("Excel_processed\QP1200_SDB.xlsx","Sheet1")
    return 

    data_frame = pd.read_excel("Excel_processed\QP1200_SDB.xlsx",sheet_name="Sheet1",header=([0,1,2]),index_col=0)
    tests_list = data_frame.columns.get_level_values(0).unique().tolist()
    tests_series = {s : s.split('_', 2)[1] for s in tests_list}
    directions = list(set(tests_series.values()))
    geo_name = tests_list[0].split("_",1)[0]
    buffers = []

    test_name = "SDB_RD_2"
    x = data_frame[test_name]["Calculation"]["Eng. Strain"]
    y = data_frame[test_name]["Calculation"]["Eng. Stress"]
    young_modulus = data_frame[test_name]["Calculation"]["Young's modulus"].head()[0]


    plt.plot(x,y)
    id=get_yield_stress(x,y,young_modulus)

    plt.plot([0,x[id]], [0,y[id]], color="red", zorder=3, label="Intersection")
 
    plt.show()

if __name__ == '__main__':
  main()


