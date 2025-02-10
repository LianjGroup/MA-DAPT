# %% [markdown]
# # TODO
# 
# 
# - Create file to store addresses
# - Add option to change addresses in gui
# - Add settings tab if they are any other settings
# - Remake comparison fracture function


# 
# 
 #use crtl+k crtl+c to comment out and crtl+k crtl+u to uncomment

import io
import tkinter as tk
from tkinter import  messagebox,ttk,filedialog     
import pandas as pd
import os
import yaml
from PIL import Image, ImageTk, ImageGrab
import Improved as im
import ctypes     
import win32clipboard
 


#import Mypackage.Mymodule as mm Previous code



class App(tk.Tk):    # Basic App blueprint. Tabs with features are added to it
  def __init__(self):
      super().__init__()


      self.title("Materials Analysis")    
      style = ttk.Style()                            #Use to change the style of the tabs
      style.configure("Notebook.Tab", padding=[20,0,20,0])  
    
      self.notebook = ttk.Notebook()
      self.geometry("700x600")
      self.notebook.pack(fill="both", expand=True)

      material_result=obtain_materials()
      if material_result[0]:
          pass
      else:
          messagebox.showerror("Error","Can't find any Excel files")

      self.buffer=BufferStorage()
      
 
      self.show_photo_button = ttk.Button(self, text="⚙️", command=lambda:Settings(self))
      self.show_photo_button.pack(pady=20,side="right")
      
      self.organize_tab = OrganizeEverythingTab(self,self.notebook,material_result[2],self.buffer)    
      
      #self.plas_tab = PlasTab(self,self.notebook,material_result[2],self.buffer) 
      #self.calc_tab = CalcTab(self,self.notebook,material_result[1]) 
      #self.frac_tab = FracTab(self,self.notebook,material_result[1],self.buffer)
      #self.ani_tab =  AnisTab(self,self.notebook,material_result[2],self.buffer) 
      #self.comp_tab = CompTab(self,self.notebook,material_result[2],self.buffer) 
     


      self.mainloop()


# Misc functions

class BufferStorage:
    def __init__(self):
        self.photo_buffer = []  # To store photos
        self.data_buffer = []   # To store x,y values

    def add_photo(self, photo):
        self.photo_buffer.append(photo)

    def add_data(self, data):
        self.data_buffer.append(data)

    def get_photos(self):
      #print(len(self.photo_buffer))
      return self.photo_buffer

    def get_data(self):
      return self.data_buffer

    def clear_photos(self):
        self.photo_buffer.clear()
    def clear_data(self):
        self.data_buffer.clear()


def address():
  return ("Excel_raw","Excel_processed")

def obtain_materials():
    Excel_raw,Excel_processed=address()
    
    materials_raw = [os.path.splitext(f)[0] for f in os.listdir(Excel_raw) if f.endswith(('.xlsx', '.xls'))]
    materials_processed = [os.path.splitext(f)[0] for f in os.listdir(Excel_processed) if f.endswith(('.xlsx', '.xls'))]
    if not materials_raw:
        return False,materials_raw,materials_processed
    else:
        return True,materials_raw,materials_processed


def validate_input(new_value): #Ensures only numbers can be entered
    if new_value == "" or new_value.replace("", "1").isdigit():
        return True
    return False


def send_to_clipboard(name):
    image = Image.open(name)
    output = io.BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

class ImageGrid(tk.Toplevel):
    def __init__(self, parent, image_buffers):
        super().__init__(parent)
        self.title("Graphs")
        self.geometry("1500x1600")

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.image_frame = ttk.Frame(self.canvas)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.image_frame, anchor="nw")
        
        
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.file_menu = tk.Menu(self.menubar,tearoff=False)
        self.file_menu.add_command(
            label='Save all',
            command=self.saveall,
        )
        self.menubar.add_cascade(
            label="File",
            menu=self.file_menu,
            underline=0
        )

        self.images = self.load_images(image_buffers)
        self.display_images()

        self.image_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        def cleanup():
            image_buffers.clear_photos()
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", cleanup)


    def saveall(self):
        for img in self.images:
            self.save_image(img, True)
    def load_images(self, image_buffers):
        images = []
        tem_image = image_buffers.get_photos()
        if tem_image.__len__() >1:
          for buffer in tem_image:
              img = Image.open(io.BytesIO(buffer))
              img = img.resize((180*4, 180*3))  
              images.append(ImageTk.PhotoImage(img))
        else:
          img = Image.open(io.BytesIO(tem_image[0]))
          img = img.resize((220*4, 220*3))  
          images.append(ImageTk.PhotoImage(img)) 
        return images

    def display_images(self):
        print(len(self.images))
      # For single graph
        if len(self.images) == 1:                
            img=self.images[0]
            container = ttk.Frame(self.image_frame)
            container.pack(side="top")
            label = tk.Label(container, image=img)
            label.pack()
            button_container = ttk.Frame(container)
            button_container.pack(pady=5)
            label.image = img
            save_button = ttk.Button(button_container, text="Save As ", command=lambda img=img: self.save_image(img))
            save_button.pack(padx=5,side="left")
            save_as_button = ttk.Button(button_container, text="Save Image", command=lambda img=img: self.save_image(img,True))
            save_as_button.pack(side="left")
            copy_button = ttk.Button(button_container, text="Copy (Windows)",command=lambda img=img:self.save_image(img,True,True))
            copy_button.pack(side="left")
        else:
          for i, img in enumerate(self.images):
              container = ttk.Frame(self.image_frame)
              container.grid(row=i // 2, column=i % 2, pady=10, sticky="nsew")
              label = tk.Label(container, image=img)
            
              label.pack()
              button_container = ttk.Frame(container)
              button_container.pack(pady=5)

              label.image = img  # Keep a reference to avoid garbage collection
              save_button = ttk.Button(button_container, text="Save As ", command=lambda img=img: self.save_image(img))
              save_button.pack(padx=5,side="left")
              save_as_button = ttk.Button(button_container, text="Save Image", command=lambda img=img: self.save_image(img,True))
              save_as_button.pack(side="left",padx=5)
              copy_button = ttk.Button(button_container, text="Copy",command=lambda img=img: self.save_image(img,True,True))
              copy_button.pack(side="left")
            # button1.grid(row=1, column=0)
              #button2.grid(row=1, column=1)
              #button3.grid(row=1, column=2)
 

    def save_image(self, img,location=False,clipboard=False):
        if location:
          save_path = f"Saved{os.sep}Graph.png"
          base, ext = os.path.splitext(save_path)
          counter = 1
          while os.path.exists(save_path):
            save_path = f"{base}_{counter}{ext}"
            counter += 1
          img._PhotoImage__photo.write(save_path)
          if clipboard:
            send_to_clipboard(save_path)
            os.remove(save_path)
          
  


        else:
          file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=[("PNG files", "*.png"),
                                                              ("JPEG files", "*.jpg"),
                                                              ("All files", "*.*")])
          if file_path:
            print("LLLLLLLLLLLLLLLLLM"+file_path)
            img._PhotoImage__photo.write(file_path)




class Settings(tk.Toplevel):
  def __init__(self, parent):
      super().__init__(parent)
      self.title("Settings")
      self.geometry("800x600")

      # Variables
      self.font_family_var = tk.StringVar()
      self.font_size_var = tk.StringVar()

      self.axes_labelsize_var = tk.StringVar()
      self.legend_on_var = tk.BooleanVar()
      self.legend_fontsize_var = tk.StringVar()

      self.raw_files_var = tk.StringVar()
      self.processed_files_var = tk.StringVar()

      self.save_location_var = tk.StringVar()
      self.axes_titlesize_var = tk.StringVar()

      # Load settings from YAML
      with open(f'Script{os.sep}config.yaml', "r") as file:
          self.settings = yaml.safe_load(file)

      # Set initial values
      self.font_family_var.set(self.settings["matplotlib"]["font"]["family"])
      self.font_size_var.set(str(self.settings["matplotlib"]["font"]["size"]))
      self.axes_labelsize_var.set(str(self.settings["matplotlib"]["axes"]["labelsize"]))
      self.axes_titlesize_var.set(str(self.settings["matplotlib"]["axes"]["titlesize"]))
      self.legend_on_var.set(self.settings["matplotlib"]["legend"]["on"])
      self.legend_fontsize_var.set(str(self.settings["matplotlib"]["legend"]["fontsize"]))
      self.raw_files_var.set(self.settings["file_paths"]["raw_files_location"])
      self.processed_files_var.set(self.settings["file_paths"]["processed_files_location"])
      self.save_location_var.set(self.settings["file_paths"]["save_location"])

      # GUI Layout
      ttk.Label(self, text="Font Family:").grid(row=1, column=0, sticky="w", padx=10)
      font_families = ["Arial", "Times New Roman", "Courier New", "Verdana", "Helvetica"]
      ttk.Combobox(self, textvariable=self.font_family_var, values=font_families, state="readonly").grid(row=1, column=1, padx=10)

      ttk.Label(self, text="Font Size:").grid(row=2, column=0, sticky="w", padx=10)
      self.validate_numeric = self.register(validate_input)
      ttk.Entry(self, textvariable=self.font_size_var, validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=2, column=1, padx=10)

      ttk.Label(self, text="Axes Label Size:").grid(row=3, column=0, sticky="w", padx=10)
      ttk.Entry(self, textvariable=self.axes_labelsize_var, validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=3, column=1, padx=10)

      ttk.Label(self, text="Axes Title Size:").grid(row=4, column=0, sticky="w", padx=10)
      ttk.Entry(self, textvariable=self.axes_titlesize_var, validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=4, column=1, padx=10)

      ttk.Label(self, text="Legend On:").grid(row=5, column=0, sticky="w", padx=10)
      ttk.Checkbutton(self, variable=self.legend_on_var).grid(row=5, column=1, padx=10, sticky="w")

      ttk.Label(self, text="Legend Font Size:").grid(row=6, column=0, sticky="w", padx=10)
      ttk.Entry(self, textvariable=self.legend_fontsize_var, validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=6, column=1, padx=10)

      ttk.Label(self, text="File Paths", font=("Arial", 14, "bold")).grid(row=7, column=0, columnspan=2, pady=10)

      ttk.Label(self, text="Raw Files Location:").grid(row=8, column=0, sticky="w", padx=10)
      ttk.Entry(self, textvariable=self.raw_files_var).grid(row=8, column=1, padx=10)

      ttk.Label(self, text="Processed Files Location:").grid(row=9, column=0, sticky="w", padx=10)
      ttk.Entry(self, textvariable=self.processed_files_var).grid(row=9, column=1, padx=10)

      ttk.Label(self, text="Save Location:").grid(row=10, column=0, sticky="w", padx=10)
      ttk.Entry(self, textvariable=self.save_location_var).grid(row=10, column=1, padx=10)

      # Save Button
      ttk.Button(self, text="Save Settings", command=self.save_settings).grid(row=11, column=1, pady=20)

 

  def save_settings(self):
      """Save the updated settings to the YAML file."""
      self.settings["matplotlib"]["font"]["family"] = self.font_family_var.get()
      self.settings["matplotlib"]["font"]["size"] = int(self.font_size_var.get())
      self.settings["matplotlib"]["axes"]["labelsize"] = int(self.axes_labelsize_var.get())
      self.settings["matplotlib"]["axes"]["titlesize"] = int(self.axes_titlesize_var.get())
      self.settings["matplotlib"]["legend"]["on"] = self.legend_on_var.get()
      self.settings["matplotlib"]["legend"]["fontsize"] = int(self.legend_fontsize_var.get())
      self.settings["file_paths"]["raw_files_location"] = self.raw_files_var.get()
      self.settings["file_paths"]["processed_files_location"] = self.processed_files_var.get()
      self.settings["file_paths"]["save_location"] = self.save_location_var.get()

      self.save_yaml(self.settings)
      print("Settings saved successfully!")
      im.configs()

  def save_yaml(self, data):
      """Save data to the YAML file."""
      with open(f'Script{os.sep}config.yaml', "w") as file:
          yaml.safe_dump(data, file)



# Calculation Tab
 
class CalcTab(ttk.Frame):
  def __init__(self,parent, notebook,materials):
    super().__init__(parent)
    
    notebook.add(self, text="Calculation")



    #Enables buttons          
    def validate():
      if self.selected_calc_mat.get() != "" and entry.get() != "":
          calculate_button.config(state=tk.NORMAL)  
          modified_button.config(state=tk.NORMAL)  

      else:
          calculate_button.config(state=tk.DISABLED) 
          modified_button.config(state=tk.DISABLED)      


 
    canvas=tk.Canvas(self,scrollregion=(0,0,0,len(materials)*52),width=10,highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
    
    
    left_frame=ttk.Frame(canvas)
    canvas.create_window((30,100), window=left_frame, anchor="nw")
 



    mat_title = ttk.Label(canvas, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)

    self.selected_calc_mat = tk.StringVar(value="")

    for material in (materials):
      radio = ttk.Radiobutton(left_frame, 
                              text=material, 
                              value=material, 
                              variable=self.selected_calc_mat,
                              command=validate)
      radio.pack(anchor="w",pady=3)




    ''''Right frame'''


    right_frame=ttk.Frame(self)
    right_frame.pack(side="left",padx=20,anchor="s")



 


    top_right_frame=ttk.Frame(right_frame)
    top_right_frame.pack(pady=200)


    mat_title = ttk.Label(top_right_frame, text="Enter critical stress:",)
    mat_title.pack(anchor="s")
    

    
    validate_cmd = top_right_frame.register(validate_input)
    entry = ttk.Entry(top_right_frame, validate="key", validatecommand=(validate_cmd, "%P"))
    entry.pack(pady=10,side="top")
    entry.bind("<KeyRelease>", lambda event: validate())

    ''''Bottom right frame'''

    bottom_right_frame=ttk.Frame(right_frame)
    bottom_right_frame.pack(pady=20,padx=20)

    calculate_button = ttk.Button(bottom_right_frame, text="Calculate",state=tk.DISABLED,command= lambda :calculate(False,int(entry.get())))
    calculate_button.pack( side="left")

    modified_button = ttk.Button(bottom_right_frame, text="Modified",state=tk.DISABLED,command= lambda :calculate(True,int(entry.get())))
    modified_button.pack(padx=25 ,side="right")



    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)


    def calculate(modification,critical_stress:int):
          Excel_raw =address()[0]

          path = f"{Excel_raw}{os.sep}{self.selected_calc_mat.get()}.xlsx"
          search_string = 'SDB'
          excel_file = pd.ExcelFile(path, engine='openpyxl')
          matching_sheets = [sheet for sheet in excel_file.sheet_names if search_string in sheet]

          if modification:
            for sheet_name in matching_sheets:
                print("sheet_name")
                im.calculation(path, sheet_name, critical_stress,True)
          else: 
              for sheet_name in matching_sheets:
                im.calculation(path, sheet_name, critical_stress)

          return

 
class PlasTab(ttk.Frame):
  def __init__(self,parent, notebook,materials,buffer):
    super().__init__(parent)
    Excel_processed=address()[1]

    notebook.add(self, text="Plasticity")

    mat_title = ttk.Label(self, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)

    canvas=tk.Canvas(self, 
                     scrollregion=(0,0,0,len(materials)*45),
                     width=10,
                     highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
    
    
    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,20), window=left_frame, anchor="nw")
 


    self.selected_mat = tk.StringVar(value="")

    for material in (materials):
      radio = ttk.Radiobutton(left_frame, 
                              text=material,
                               value=material,
                                 variable=self.selected_mat)
      radio.pack(anchor="sw",pady=3)


    ''''Middle Frame'''
    

    properties_frame=ttk.Frame(self)
    properties_frame.pack(side="left",padx=15,expand=True,fill="both",anchor="n")


    prop_title = ttk.Label(properties_frame, text="Graph", font=("Arial", 15))
    prop_title.pack(pady=20)

    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  

    properties = ["engineering", "true", "effective plastic strain","r-value"] 
    self.property_vars = {}
    for prop in (properties):
      var = tk.BooleanVar(value=False)   
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var)
      self.property_vars[prop] = var
      chk.pack(anchor="sw", pady=2) 


    
    
    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  


    
    def repeatablity_caller():
      path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
      selected = [prop for prop, var in self.property_vars.items() if var.get()]
      for p in selected:
        bufs=im.repeatablity(path,"Sheet1",p)
        for b in bufs:
          buffer.add_photo(b.getvalue())
        #buffer.add_photo(im.repeatablity(path,"Sheet1",p))

      ImageGrid(self,buffer) # type: ignore
        

 
   
    repeat_button=ttk.Button(properties_frame,text="Repeat",command=lambda :repeatablity_caller())
    repeat_button.pack(pady=3)  
   
 
    def size_effect():
      selected_indices = [idx for idx, var in self.property_vars.items() if var.get()]
      path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
      selected = [prop for prop, var in self.property_vars.items() if var.get()]

      
      data_frame=pd.read_excel(path,sheet_name="Sheet1",header=([0,1,2]))
      tests_list = data_frame.columns.get_level_values(0).unique().tolist()
      # create a new window
      new_window = tk.Toplevel(self)
      new_window.title("Select test number")
      # build a frame to display checkboxes
      check_frame = ttk.Frame(new_window)
      check_frame.pack (pady=10)
      #generate a list of checkboxes with all tests list in the processed excel.
      selected_tests = {}
      for idx, prop in enumerate(tests_list):
        var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(check_frame, text=prop, variable=var)
        chk.grid(row=idx+1, column=1, sticky='w')
        selected_tests[prop] = var
      def on_confirm():
        print("Donkey")
        selected_options = [opt for opt, var in selected_tests.items() if var.get()]
        print((path, selected_options,selected_indices[0]))
        for opts in selected:
          buffer.add_photo(im.custom_plot(path, selected_options,opts))
        ImageGrid(self,buffer) # type: ignore
      confirm_button = ttk.Button(new_window, text="Confirm", command=on_confirm)
      confirm_button.pack(pady=10)
    
    
    custom_plot_button=ttk.Button(properties_frame,text="Custom Plot",command=size_effect)
    custom_plot_button.pack(pady=3)  



    def r_elong():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.r_plot(path,"Sheet1"))

        ImageGrid(self,buffer) 
   
   
    ytsU_button=ttk.Button(properties_frame, text="R-Value", command=r_elong)
    ytsU_button.pack(pady=3)

    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)


 
class FracTab(ttk.Frame):
  def __init__(self, parent,notebook,materials,buffer):
    super().__init__(parent)
    notebook.add(self, text="Fracture")
    self.material_vars = {}
     
    
    canvas=tk.Canvas(self,scrollregion=(0,0,0,len(materials)*52),width=10,highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
 


    ''''Left frame'''


    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,100), window=left_frame, anchor="nw")
     
    mat_title = ttk.Label(canvas, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)
    self.selected_calc_mat = tk.StringVar(value="")
    

    
    
    right_frame=ttk.Frame(self)
    right_frame.pack(side="left")



    self.selected_calc_mat = tk.StringVar(value="")

    def frac_calculate(path,var):  
        for header in var:
          bufs=(im.fracture_repeat(path,  header))
          for b in bufs:
            buffer.add_photo(b.getvalue())
        ImageGrid(self,buffer)  
    
    def frac_summary(path,var):  
      for header in var:
        buffer.add_photo(im.fracture_summary(path,  header).getvalue())
      ImageGrid(self,buffer)  
        

    def frac_summary_multiple(path,var):  
      buffer.add_photo(im.fracture_compare_summary(path,  var).getvalue())
      ImageGrid(self,buffer)  
        

 
    def frac_one_name(path,var):  
      print("cake",var)
      ans=im.fracture_normal_compare(path,  var)
      for i in ans:
        buffer.add_photo(i.getvalue())
      ImageGrid(self,buffer)  
        

 
 






    def frac_repeat():        #Add list for eveyr selected matertial
        for widget in right_frame.winfo_children():
          widget.pack_forget()
      
        Excel_raw=address()[0]

        print(self.selected_calc_mat.get())
        path = f"{Excel_raw}{os.sep}{self.selected_calc_mat.get()}.xlsx"
        all_sheets = pd.ExcelFile(path).sheet_names
        filtered_sheets = [sheet for sheet in all_sheets if "SDB" not in sheet and "Tests" not in sheet]
        sheet_list = list(filtered_sheets)
        self.checkbox_vars = {}
        for header in sheet_list:
          var = tk.BooleanVar(value=False)
          checkbox = ttk.Checkbutton(right_frame, text=header, variable=var)
          self.checkbox_vars[header] = var
          checkbox.pack(anchor="w", pady=2,padx=50)

        def get_selected(): # Collect the ticked boxses    
            selected = [header for header, var in self.checkbox_vars.items() if var.get()]
            return selected


        def frac_compare(path,var):
          compare_materials=[]
          for material in materials:
            path = f"{Excel_raw}{os.sep}{material}.xlsx"
            all_sheets = pd.ExcelFile(path).sheet_names
            filtered_sheets = [sheet for sheet in all_sheets if "SDB" not in sheet and "Tests" not in sheet]
            sheet_list = list(filtered_sheets)
            if (all(item in sheet_list for item in get_selected())):
              compare_materials.append(material)
          
          
          compare_materials.remove((self.selected_calc_mat.get()))
          print(compare_materials)
          
          
          window = tk.Toplevel()
          window.title("Select Other Materials")
          self.bvars = {}
          for material in compare_materials:
              bvar = tk.BooleanVar(value=False)
              chk = ttk.Checkbutton(window, text=material, variable=bvar, onvalue=True, offvalue=False)              
              self.bvars[material]=bvar
              #chk.pack(anchor='w')

              chk.pack(anchor='w')
          def get_selected_checks():   
            selected = [header for header, var in self.bvars.items() if var.get()]
            selected.append(self.selected_calc_mat.get())
            return selected

          btn = ttk.Button(window, text="OK", command=lambda:frac_compare_caller(var,get_selected_checks()))
          btn.pack()


        def frac_compare_caller(var,materials):
          print(materials)
  

          for header in var:
            bufs=im.fracture_compare(path,  header,materials)
             
            #buffer.add_photo(im.fracture_compare(path,  header,materials))
            
          #ImageGrid(self,buffer) # type: ignore
          
          #ImageGrid(self,"Script\images") # type: ignore

            #if get_selected()



        confirm_button=ttk.Button(right_frame,text="Confirm",command= lambda:frac_calculate(path,get_selected()))           
        confirm_button.pack(padx=50)
        compare_button=ttk.Button(right_frame,text="Compare",command= lambda:frac_compare(path,get_selected()))           
        compare_button.pack(padx=50)
        summary_button=ttk.Button(right_frame,text="Summary",command= lambda:frac_summary(path,get_selected()))           
        summary_button.pack(padx=50)
        summary_button_compare=ttk.Button(right_frame,text="Sum comp",command= lambda:frac_summary_multiple(path,get_selected()))           
        summary_button_compare.pack(padx=50)
        confirm_compare_button=ttk.Button(right_frame,text="confirm comp",command= lambda:frac_one_name(path,get_selected()))           
        confirm_compare_button.pack(padx=50)


    for material in (materials):  #Add materials
      radio = ttk.Radiobutton(left_frame, text=material, value=material, variable=self.selected_calc_mat, command=frac_repeat)
      radio.pack(anchor="w")

    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

 


   
 
class CompTab(ttk.Frame):
  def __init__(self,parent, notebook,materials,buffer):
    super().__init__(parent)

    Excel_processed=address()[1]


      
    notebook.add(self, text="Comparasion")

    mat_title = ttk.Label(self, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)

    canvas=tk.Canvas(self, 
                     scrollregion=(0,0,0,len(materials)*33),
                     width=10,
                     highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
    
    
    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,20), window=left_frame, anchor="nw")
 


    self.selected_mat = tk.StringVar(value="")

    self.material_vars = {}
    for idx, material in enumerate(materials):
      var = tk.BooleanVar(value=False)   
      chk = ttk.Checkbutton(left_frame, text=material, variable=var)
      chk.grid(row=idx+1, column=0, sticky='w')
      self.material_vars[material] = var

    def compare_caller():
      selected_materials = [mat for mat, var in self.material_vars.items() if var.get()]
      selected = [prop for prop, var in self.property_vars.items() if var.get()]

   
      import matplotlib.pyplot as plt
      plt.switch_backend('Agg')  # Non-GUI backend for saving or handling plots without display
      
   
      for p in selected:
        buffer.add_photo(im.compare(address()[1],selected_materials,p))



      ImageGrid(self,buffer) # type: ignore
        
  
    

     

    properties_frame=ttk.Frame(self)
    properties_frame.pack(side="left",padx=15,expand=True,fill="both",anchor="ne")



    # Fills horizontally

    prop_title = ttk.Label(properties_frame, text="Graphs", font=("Arial", 15),anchor="w")
    prop_title.pack(pady=20)

    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  

    properties = ["engineering", "true", "effective plastic strain","r-value"] 
    self.property_vars = {}
    for prop in (properties):
      var = tk.BooleanVar(value=False)   
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var)
      self.property_vars[prop] = var
      chk.pack(anchor="s", pady=2) 


  
    
    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  



    compare_button=ttk.Button(properties_frame,text="Compare",command=lambda :compare_caller())
    compare_button.pack(pady=10)  



    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)





class AnisTab(ttk.Frame):
  def __init__(self,parent, notebook,materials,buffer):
    super().__init__(parent)
    Excel_processed=address()[1]

    notebook.add(self, text="Anistropy")

    mat_title = ttk.Label(self, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)

    canvas=tk.Canvas(self, 
                     scrollregion=(0,0,0,len(materials)*45),
                     width=10,
                     highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
    
    
    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,40), window=left_frame, anchor="nw")
 


    self.selected_mat = tk.StringVar(value="")

    for material in (materials):
      radio = ttk.Radiobutton(left_frame, 
                              text=material,
                               value=material,
                                 variable=self.selected_mat)
      radio.pack(anchor="sw",pady=3)




    ''''Middle Frame'''




    labels_frame=ttk.Frame(self)
    labels_frame.pack(side="left",anchor="nw",padx=1)


    label_separator = ttk.Separator(labels_frame, orient="horizontal")
    label_separator.grid(row=0,column=0,columnspan=2,pady=35)  



    labels = ["RD", "DD", "TD","24", "15", "30", "60", "75"]
    self.label_vars = {}
    self.entry_vars = {}
    for i,label in enumerate(labels):
      var = tk.BooleanVar(value=False)   
      
      chk = ttk.Label(labels_frame, text=label)
      self.label_vars[label] = var
      chk.grid(row=i+1,column=0,pady=2)  
     
      entry_var = tk.StringVar()
      validate_cmd = labels_frame.register(validate_input)
      entry = ttk.Entry(labels_frame, textvariable=entry_var, width=10, validate="key", validatecommand=(validate_cmd, "%P"))
      entry.grid(row=i+1,column=1,pady=2,columnspan=5)
      self.entry_vars[label] = entry_var

      

    properties_frame=ttk.Frame(self)
    properties_frame.pack(side="left",padx=55,fill="both",anchor="n")




    # Fills horizontally

    prop_title = ttk.Label(properties_frame, text="Graph", font=("Arial", 15))
    prop_title.pack(pady=5,anchor="n",side="top")

    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
   # prop_separator.pack(pady=1)  

    properties = ["engineering", "true", "effective plastic strain","r-value"] 
    self.property_vars = {}
    for prop in (properties):
      var = tk.BooleanVar(value=False)   
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var)
      self.property_vars[prop] = var
      chk.pack(anchor="sw", pady=2) 


 

    def get_values():
        values = {}
        for label, var in self.entry_vars.items():
            value = var.get()
            if value:  
                try:
                    values[label] = value
                except ValueError:
                    messagebox.showerror("input error")
                    return
        return values   

    def orientation():
      path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
      dire_test = get_values()
      selected = [prop for prop, var in self.property_vars.items() if var.get()]
      buffer.add_photo(im.orientation(path,"Sheet1",selected[0],dire_test))
      ImageGrid(self,buffer) # type: ignore


    anisotropy_button=ttk.Button(properties_frame,text="Anisotropy",command=lambda:orientation())
    anisotropy_button.pack(pady=3)  

    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)






class OrganizeEverythingTab(ttk.Frame):
  def __init__(self,parent, notebook,materials,buffer):
    super().__init__(parent)
    Excel_processed=address()[1]

    notebook.add(self, text="ORGANIZE")

    mat_title = ttk.Label(self, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)

    canvas=tk.Canvas(self, 
                     scrollregion=(0,0,0,len(materials)*45),
                     width=10,
                     highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
    
    
    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,20), window=left_frame, anchor="nw")
 


    self.selected_mat = tk.StringVar(value="")

    for material in (materials):
      radio = ttk.Radiobutton(left_frame, 
                              text=material,
                               value=material,
                                 variable=self.selected_mat)
      radio.pack(anchor="sw",pady=3)


    ''''Middle Frame'''
    

    properties_frame=ttk.Frame(self)
    properties_frame.pack(side="left",padx=15,expand=True,fill="both",anchor="n")


    prop_title = ttk.Label(properties_frame, text="Graph", font=("Arial", 15))
    prop_title.pack(pady=20)

    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  

    properties = ["engineering", "true", "effective plastic strain","r-value"] 
    self.property_vars = {}
    for prop in (properties):
      var = tk.BooleanVar(value=False)   
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var)
      self.property_vars[prop] = var
      chk.pack(anchor="sw", pady=2) 


    
    
    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  


    def summary(letters=False):
      path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
      selected = [prop for prop, var in self.property_vars.items() if var.get()]
      for p in selected:
        buffer.add_photo(im.summary(path,"Sheet1",p,letters) )
         

      ImageGrid(self,buffer)

    summary_frame=ttk.Frame(properties_frame)

    short_var = tk.BooleanVar(value=False)   
    short_check=ttk.Checkbutton(summary_frame,text="DD,RD,TD",variable=short_var)
    summary_button=ttk.Button(summary_frame,text="Summary",command=lambda :summary(short_var.get()))
    summary_frame.pack(pady=3)

    summary_button.pack(side="right")
    short_check.pack(side="right",padx=29)


    def uts():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.uts_plot(path,"Sheet1"))
        ImageGrid(self,buffer) 
   
   
    uts_button=ttk.Button(properties_frame, text="UTS", command=uts)
    uts_button.pack(pady=3,padx=100)

    def yts():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.yield_stress_plot(path,"Sheet1"))
        ImageGrid(self,buffer) 
   
   
    yts_button=ttk.Button(properties_frame, text="Yield Stress", command=yts)
    yts_button.pack(pady=3)
 

    def yieldr():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.yield_stress_plot(path,"Sheet1",True))
        ImageGrid(self,buffer) 
   
   
    R_button=ttk.Button(properties_frame, text="R values", command=yieldr)
    R_button.pack(pady=3)
    
   
 

    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)


 


 
def main(): 
  ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix scaling so text isn't blurry. Test on mac screens
  App()


if __name__ == '__main__':
  main()