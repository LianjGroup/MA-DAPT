import io
import tkinter as tk
from tkinter import  messagebox,ttk,filedialog     
import pandas as pd
import os
import yaml
from PIL import Image, ImageTk
import Improved as im
import traceback

     # Logo based on name
     # Add more about about info
     # Add settings to change x lims 

import sys
if sys.platform == "win32":
  import win32clipboard
  import ctypes 
elif sys.platform == "darwin":
    import subprocess


 

class App(tk.Tk):    # Basic App blueprint. Tabs with features are added to it
  def __init__(self):
    super().__init__()

    self.report_callback_exception = self.show_error

    try:
      self.iconbitmap("final_icon.ico")

      self.title("Materials Analysis")    
      style = ttk.Style()                            #Use to change the style of the tabs
      style.configure("Notebook.Tab", padding=[20,0,20,0])  
    
      self.notebook = ttk.Notebook()
      self.geometry("700x600")
      self.minsize(700, 600)  
      self.notebook.pack(fill="both", expand=True)

      material_result=obtain_materials()
      if material_result[0]:
          pass
      else:
          messagebox.showerror("Error","Can't find any Excel files")

      self.buffer=BufferStorage()
      

      def cause_error():
          raise RuntimeError("money!")

      btn = tk.Button(self, text="This is an easter egg I'm too lazy to remove", command=cause_error)
      btn.pack(pady=20)


      # All tabs. Get sent proper materials
      
      self.plas_tab = PlasTab(self,self.notebook,material_result[2],self.buffer) 
      
      self.ani_tab =  AnisTab(self,self.notebook,material_result[2],self.buffer) 
    
      self.comp_tab = CompTab(self,self.notebook,material_result[2],self.buffer) 
      
      self.frac_tab = FracTab(self,self.notebook,material_result[1],self.buffer)
      self.calc_tab = CalcTab(self,self.notebook,material_result[1])
      self.mainloop() 
    except Exception as e:
        self.show_error(type(e), e, e.__traceback__)
        self.destroy()  

  def show_error(self, exc_type, exc_value, exc_traceback):
      error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
      messagebox.showerror("Error", f"An error occurred:\n\n{error_message}")

    



# Stores photos while shown in the gallery
# Later store data
class BufferStorage:
    def __init__(self):
      self.photo_buffer = []  # To store photos
      self.data_buffer = []   # To store x,y values

    def add_photo(self, photo):
      self.photo_buffer.append(photo)

    def add_data(self, data):
      self.data_buffer.append(data)

    def get_photos(self): 
      return self.photo_buffer

    def get_data(self):
      return self.data_buffer

    def clear_photos(self):
      self.photo_buffer.clear()
    def clear_data(self):
      self.data_buffer.clear()



# Misc functions
def address():
  return ("Excel_raw","Excel_processed")

def obtain_materials():
    Excel_raw,Excel_processed=address()
    
    materials_raw = [os.path.splitext(f)[0] for f in os.listdir(Excel_raw) if f.endswith((".xlsx", ".xls"))]
    materials_processed = [os.path.splitext(f)[0] for f in os.listdir(Excel_processed) if f.endswith((".xlsx", ".xls"))]
    if not materials_raw or not materials_processed:
        return False,materials_raw,materials_processed
    else:
        return True,materials_raw,materials_processed


def validate_input(new_value): #Ensures only numbers can be entered
    if new_value == "" or new_value.replace(".", "", 1).isdigit():
      return True
    return False




def send_to_clipboard(name):
    image = Image.open(name)                                          
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")     #Take image as rgb buffer
    data = output.getvalue()[14:]            # Cut Header
    output.close()

    if sys.platform == "win32":                    # For winodws
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    
    elif sys.platform == "darwin":  #Test ON MAC
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        process = subprocess.Popen(
            ["pbcopy"], stdin=subprocess.PIPE
        )
        process.communicate(output.getvalue())

    ## Add linux version



class ImageGrid(tk.Toplevel):
  existing_instance = None   
  def __init__(self, parent, image_buffers):
    if ImageGrid.existing_instance is not None:   # Ensures only one (latest) window exists
        ImageGrid.existing_instance.destroy()


    super().__init__(parent)
    self.title("Graphs")
    self.geometry("1480x1600")
    ImageGrid.existing_instance = self
    self.canvas = tk.Canvas(self, highlightthickness=0)
    
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
        label="Save all",
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
      if ImageGrid.existing_instance == self:
        ImageGrid.existing_instance = None
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
        self.geometry("910x750")

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
          button_container.pack(pady=5,anchor="e")
          label.image = img
          save_button = ttk.Button(button_container, text="Save As ", command=lambda img=img: self.save_image(img))
          save_button.pack(padx=5,side="left")
          save_as_button = ttk.Button(button_container, text="Save Image", command=lambda img=img: self.save_image(img,True))
          save_as_button.pack(padx=5,side="left")
          copy_button = ttk.Button(button_container, text="Copy",command=lambda img=img:self.save_image(img,True,True))
          copy_button.pack(padx=5,side="left")
      else:
        for i, img in enumerate(self.images):
            container = ttk.Frame(self.image_frame)
            container.grid(row=i // 2, column=i % 2, pady=10, sticky="nsew")
            label = tk.Label(container, image=img)
          
            label.pack()
            button_container = ttk.Frame(container)
            button_container.pack(pady=5,anchor="center")

            label.image = img  # Keep a reference to avoid garbage collection
            save_button = ttk.Button(button_container, text="Save As ", command=lambda img=img: self.save_image(img))
            save_button.pack(padx=5,side="left")
            save_as_button = ttk.Button(button_container, text="Save Image", command=lambda img=img: self.save_image(img,True))
            save_as_button.pack(side="left",padx=5)
            copy_button = ttk.Button(button_container, text="Copy",command=lambda img=img: self.save_image(img,True,True))
            copy_button.pack(padx=5,side="left")
 


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

        img._PhotoImage__photo.write(file_path)




class Settings(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("500x700")
        self.iconbitmap("final_icon.ico")
        
        notebook = ttk.Notebook(self)
        settings_tab = ttk.Frame(notebook)
        about_tab = ttk.Frame(notebook)
        
        notebook.add(settings_tab, text="Settings")
        notebook.add(about_tab, text="About")
        notebook.pack(expand=True, fill="both")
        
        # Variables
        self.validate_numeric = self.register(validate_input)
        self.font_family_var = tk.StringVar()
        self.font_size_var = tk.DoubleVar()
        
        self.axes_labelsize_var = tk.DoubleVar()
        self.axes_titlesize_var = tk.DoubleVar()
        
        self.legend_on_var = tk.BooleanVar()
        self.legend_fontsize_var = tk.DoubleVar()
        
        self.normalize_var = tk.BooleanVar()
       
        self.xlim_min_var = tk.DoubleVar()
        self.xlim_max_var = tk.DoubleVar()
       
        self.ylim_min_var = tk.DoubleVar()
        self.ylim_max_var = tk.DoubleVar()
       
        self.xlim_enabled_var = tk.BooleanVar()
        self.ylim_enabled_var = tk.BooleanVar()

        # Load settings from YAML
        with open("config.yaml", "r") as file:
            self.settings = yaml.safe_load(file)

        # Set initial values
        self.font_family_var.set(self.settings["matplotlib"]["font"]["family"])
        self.font_size_var.set(str(self.settings["matplotlib"]["font"]["size"]))
        
        self.axes_labelsize_var.set(str(self.settings["matplotlib"]["axes"]["labelsize"]))
        self.axes_titlesize_var.set(str(self.settings["matplotlib"]["axes"]["titlesize"]))
        self.legend_on_var.set(self.settings["matplotlib"]["legend"]["on"])
        self.legend_fontsize_var.set(str(self.settings["matplotlib"]["legend"]["fontsize"]))
        
        self.normalize_var.set(self.settings["misc"]["normalized"])
        
        self.xlim_enabled_var.set(self.settings["matplotlib"]["limits"]["xlim_enabled"])
        self.ylim_enabled_var.set(self.settings["matplotlib"]["limits"]["ylim_enabled"])
        
        self.xlim_min_var.set(self.settings["matplotlib"]["limits"]["xlim"][0])
        self.xlim_max_var.set(self.settings["matplotlib"]["limits"]["xlim"][1])
        self.ylim_min_var.set(self.settings["matplotlib"]["limits"]["ylim"][0])
        self.ylim_max_var.set(self.settings["matplotlib"]["limits"]["ylim"][1])

        # Settings Layout
        ttk.Label(settings_tab, text="Font Family:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        font_families = ["Arial", "Times New Roman", "Cursive", "Comic Sans"]
        ttk.Combobox(settings_tab, textvariable=self.font_family_var, values=font_families, state="readonly").grid(row=0, column=1, padx=10)
        
        ttk.Label(settings_tab, text="Font Size:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.font_size_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=1, column=1, padx=10)

        ttk.Label(settings_tab, text="Axes Label Size:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.axes_labelsize_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=2, column=1, padx=10)

        ttk.Label(settings_tab, text="Legend On:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(settings_tab, variable=self.legend_on_var).grid(row=3, column=1, padx=10, sticky="w")

        ttk.Label(settings_tab, text="Legend Font Size:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.legend_fontsize_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=4, column=1, padx=10)

        ttk.Label(settings_tab, text="Normalization:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(settings_tab, variable=self.normalize_var).grid(row=6, column=1, padx=10, sticky="w")

        ttk.Label(settings_tab, text="X Lim Min:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.xlim_min_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=7, column=1, padx=10)

        ttk.Label(settings_tab, text="X Lim Max:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.xlim_max_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=8, column=1, padx=10)

        ttk.Label(settings_tab, text="Enable X Lim:").grid(row=9, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(settings_tab, variable=self.xlim_enabled_var).grid(row=9, column=1, padx=10, sticky="w")

        ttk.Label(settings_tab, text="Y Lim Min:").grid(row=10, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.ylim_min_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=10, column=1, padx=10)

        ttk.Label(settings_tab, text="Y Lim Max:").grid(row=11, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(settings_tab, textvariable=self.ylim_max_var,validate="key", validatecommand=(self.validate_numeric, "%P")).grid(row=11, column=1, padx=10)

        ttk.Label(settings_tab, text="Enable Y Lim:").grid(row=12, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(settings_tab, variable=self.ylim_enabled_var).grid(row=12, column=1, padx=10, sticky="w")

        for var in self.__dict__.values():
            if isinstance(var, (tk.StringVar, tk.DoubleVar)):
                var.trace_add("write", self.check_entries)


        # About Layout
        title_frame=ttk.Frame(about_tab)
        icon= Image.open("final_icon.ico") 
        photo = ImageTk.PhotoImage(icon.resize((80, 80)))
      
        label = ttk.Label(title_frame, image=photo)
        label.image = photo  
        label.grid(row=0, column=0,sticky="w") 
        ttk.Label(title_frame, text="MA-DAPT:\nMaterial Design, Analysis,\nProcessing, and Testing\n\n ", font=("TkDefaultFont", 11, "bold")).grid(row=0,column=1,sticky="w",padx=34)

        title_frame.pack(padx=10,pady=10,anchor="w")
        ttk.Label(about_tab, text="Version: 0.45", font=("TkDefaultFont", 11)).pack(pady=5,padx=5,anchor="w")
        
        creation = """        Created by Guijia Li and Saad Zia
        Developed as part of the Aalto University Materials
        to Products Department, led by Lian junhe."""
        ttk.Label(about_tab, text=creation).pack(pady=10,anchor="w")    

        ttk.Label(about_tab, text="License: MIT License", font=("TkDefaultFont", 11, "bold")).pack(pady=10,padx=5,anchor="w")    
        ttk.Label(about_tab, text="This software is open-source and provided 'as-is'\nwithout warranty of any kind, express or implied.").pack(pady=10)    



        # Save Button
        self.save_button = ttk.Button(settings_tab, text="Save", command=self.save_settings, state="enabled")
        self.save_button.grid(row=193, column=0, columnspan=2, pady=20)

    def save_settings(self):
        """Save the updated settings to the YAML file."""
        self.settings["matplotlib"]["font"]["family"] = self.font_family_var.get()
        self.settings["matplotlib"]["font"]["size"] = int(self.font_size_var.get())
        self.settings["matplotlib"]["axes"]["labelsize"] = int(self.axes_labelsize_var.get())
        self.settings["matplotlib"]["legend"]["on"] = self.legend_on_var.get()
        self.settings["matplotlib"]["legend"]["fontsize"] = int(self.legend_fontsize_var.get())
        self.settings["misc"]["normalized"] = self.normalize_var.get()
        self.settings["matplotlib"]["limits"]["xlim_enabled"] = self.xlim_enabled_var.get()
        self.settings["matplotlib"]["limits"]["ylim_enabled"] = self.ylim_enabled_var.get()
        self.settings["matplotlib"]["limits"]["xlim"] = [self.xlim_min_var.get(), self.xlim_max_var.get()]
        self.settings["matplotlib"]["limits"]["ylim"] = [self.ylim_min_var.get(), self.ylim_max_var.get()]
        
        self.save_yaml(self.settings)
        print("Settings saved successfully!")

    def save_yaml(self, data):
        """Save data to the YAML file."""
        with open("config.yaml", "w") as file:
            yaml.safe_dump(data, file)
    
    def check_entries(self, *args):
        for var in self.__dict__.values():
            if isinstance(var, (tk.StringVar, tk.DoubleVar)):
                try:
                    value = str(var.get()).strip()
                    print(value)
                    if value == "" or value == ".":
                        self.save_button.config(state="disabled")
                        return
                except (ValueError, tk.TclError):
                    self.save_button.config(state="disabled")
                    return
        self.save_button.config(state="normal")




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
    # For scrolling
    
    
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

      
    settings_button = ttk.Button(left_frame, text="Settings", command=lambda:Settings(self))
    settings_button.pack(pady=30)



    """Right frame"""


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

    """Bottom right frame"""

    bottom_right_frame=ttk.Frame(right_frame)
    bottom_right_frame.pack(pady=20,padx=20)

    calculate_button = ttk.Button(bottom_right_frame, text="Calculate",state=tk.DISABLED,command= lambda :calculate(False,int(entry.get())))
    calculate_button.pack(side="left")

    modified_button = ttk.Button(bottom_right_frame, text="Modified",state=tk.DISABLED,command= lambda :calculate(True,int(entry.get())))
    modified_button.pack(padx=10 ,side="left")



    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)


    def calculate(modification,critical_stress:int):
          Excel_raw =address()[0]

          path = f"{Excel_raw}{os.sep}{self.selected_calc_mat.get()}.xlsx"
          search_string = "SDB"
          excel_file = pd.ExcelFile(path, engine="openpyxl")
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
      


    def validate():
        if self.selected_mat.get():
            if  any(var.get() for var in self.property_vars.values()):
              repeat_button.config(state=tk.NORMAL)
              custom_plot_button.config(state=tk.NORMAL)
              summary_button.config(state=tk.NORMAL)
            else:
              repeat_button.config(state=tk.DISABLED)
              custom_plot_button.config(state=tk.DISABLED)
              summary_button.config(state=tk.DISABLED)
            uts_button.config(state=tk.NORMAL)
            yts_button.config(state=tk.NORMAL)
            R_button.config(state=tk.NORMAL)
            
        else:
            repeat_button.config(state=tk.DISABLED)
            custom_plot_button.config(state=tk.DISABLED)
            uts_button.config(state=tk.DISABLED)
            yts_button.config(state=tk.DISABLED)
            R_button.config(state=tk.DISABLED)
            summary_button.config(state=tk.DISABLED)


    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,20), window=left_frame, anchor="nw")
 


    self.selected_mat = tk.StringVar(value="")

    for material in (materials):
      radio = ttk.Radiobutton(left_frame, 
                              text=material,
                               value=material,
                                 variable=self.selected_mat
                                 ,command=validate)
      radio.pack(anchor="sw",pady=3)

    settings_button = ttk.Button(left_frame, text="Settings", command=lambda:Settings(self))
    settings_button.pack(pady=30)
    """Middle Frame"""
    

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
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var,command=validate)
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
        chk.grid(row=idx+1, column=1, sticky="w")
        selected_tests[prop] = var
      def on_confirm():
        selected_options = [opt for opt, var in selected_tests.items() if var.get()]
        print((path, selected_options,selected_indices[0]))
        for opts in selected:
          buffer.add_photo(im.custom_plot(path, selected_options,opts))
        ImageGrid(self,buffer) # type: ignore
      confirm_button = ttk.Button(new_window, text="Confirm", command=on_confirm)
      confirm_button.pack(pady=10)
    
 
   
    def summary(letters=False):
      path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
      selected = [prop for prop, var in self.property_vars.items() if var.get()]
      for p in selected:
        buffer.add_photo(im.summary(path,"Sheet1",p,letters) )
         

      ImageGrid(self,buffer)


    def uts():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.uts_plot(path,"Sheet1"))
        ImageGrid(self,buffer) 
   
   
    def yts():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.yield_stress_plot(path,"Sheet1"))
        ImageGrid(self,buffer) 
   
   

 

    def yieldr():
        path = f"{Excel_processed}{os.sep}{self.selected_mat.get()}.xlsx"
        buffer.add_photo(im.yield_stress_plot(path,"Sheet1",True))
        ImageGrid(self,buffer) 
   
   

    


    button_frame = ttk.Frame(properties_frame)
    button_frame.pack(pady=5)

    repeat_button = ttk.Button(button_frame, text="Repeat", state=tk.DISABLED, command=repeatablity_caller)
    repeat_button.grid(row=0, column=0, padx=5, pady=5)



    custom_plot_button = ttk.Button(button_frame, text="Custom Plot", command=size_effect, state=tk.DISABLED)
    custom_plot_button.grid(row=0, column=1, padx=5, pady=5)



    short_var = tk.BooleanVar(value=False)   
    short_check=ttk.Checkbutton(button_frame,text="DD,RD,TD",variable=short_var)
    summary_button=ttk.Button(button_frame,text="Summary",state=tk.DISABLED,command=lambda :summary(short_var.get()))

    short_check.grid(row=1,column=0, padx=5, pady=5)
    summary_button.grid(row=1,column=1, padx=5, pady=5)

    uts_button=ttk.Button(button_frame, text="UTS", command=uts,state=tk.DISABLED)
    uts_button.grid(row=2,column=0, padx=5, pady=5)

    yts_button=ttk.Button(button_frame, text="YTS", command=yts,state=tk.DISABLED)
    yts_button.grid(row=2,column=1, padx=5, pady=5)

    R_button=ttk.Button(button_frame, text="R values", command=yieldr,state=tk.DISABLED)
    R_button.grid(row=3,column=0, padx=5, pady=5,columnspan=2)



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
 


    """Left frame"""


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
       # filtered_sheets = [sheet for sheet in all_sheets if "SDB" not in sheet and "Tests" not in sheet]
        filtered_sheets = [sheet for sheet in all_sheets if "Tests" not in sheet]
       
        sheet_list = list(filtered_sheets)
        self.checkbox_vars = {}
        for header in sheet_list:
          var = tk.BooleanVar(value=False)
          checkbox = ttk.Checkbutton(right_frame, text=header, variable=var)
          self.checkbox_vars[header] = var
          checkbox.pack(anchor="center", pady=2,padx=50)

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

              chk.pack(anchor="w")
          def get_selected_checks():   
            selected = [header for header, var in self.bvars.items() if var.get()]
            selected.append(self.selected_calc_mat.get())
            return selected

          btn = ttk.Button(window, text="OK", command=lambda:frac_compare_caller(var,get_selected_checks()))
          btn.pack()


        def frac_compare_caller(var,materials):
          print(materials)
  
          bufs=[]
          for header in var:
            bufs.append(im.fracture_compare(path,  header,materials))
             

          for b in bufs:
            buffer.add_photo(b)
          ImageGrid(self,buffer)

        
        def force_displacement(path,quality):
          buffer.add_photo(im.Normalized_plot(path,quality))
          ImageGrid(self,buffer)

# Give better names

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(padx=50, pady=5)

        confirm_button = ttk.Button(button_frame, text="Confirm", command=lambda: frac_calculate(path, get_selected()))           
        compare_button = ttk.Button(button_frame, text="Compare", command=lambda: frac_compare(path, get_selected()))           
        summary_button = ttk.Button(button_frame, text="Summary", command=lambda: frac_summary(path, get_selected()))           
        summary_button_compare = ttk.Button(button_frame, text="Diection Comp", command=lambda: frac_summary_multiple(path, get_selected()))           
        confirm_compare_button = ttk.Button(button_frame, text="ForceComp", command=lambda: frac_one_name(path, get_selected()))           
        force_direction_button = ttk.Button(button_frame, text="Force/Dir", command=lambda: force_displacement(path, "Force"))           
        displacement_direction_button = ttk.Button(button_frame, text="Displacement/Dir", command=lambda: force_displacement(path, "Displacement"))           

        confirm_button.grid(row=0, column=0, padx=5, pady=5)
        compare_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        summary_button.grid(row=0, column=1, padx=5, pady=5)
        summary_button_compare.grid(row=1, column=1, padx=5, pady=5)
        confirm_compare_button.grid(row=1, column=0, padx=5, pady=5)
        
        force_direction_button.grid(row=2, column=1, padx=5, pady=5)
        displacement_direction_button.grid(row=2, column=0, padx=5, pady=5)

    for material in (materials):  #Add materials
      radio = ttk.Radiobutton(left_frame, text=material, value=material, variable=self.selected_calc_mat, command=frac_repeat)
      radio.pack(anchor="w")
    settings_button = ttk.Button(left_frame, text="Settings", command=lambda:Settings(self))
    settings_button.pack(pady=30)

    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)




 


class CompTab(ttk.Frame):
  def __init__(self,parent, notebook,materials,buffer):
    super().__init__(parent)

 


      
    notebook.add(self, text="Comparasion")

    mat_title = ttk.Label(self, text="Materials", font=("Arial", 15))
    mat_title.pack(pady=20,anchor="nw",padx=37)

    canvas=tk.Canvas(self, 
                     scrollregion=(0,0,0,len(materials)*33),
                     width=10,
                     highlightthickness=0)
    canvas.pack(side="left",expand=True,fill="both")
    
    def validate():
      if any(var.get() for var in self.material_vars.values()) and  any(var.get() for var in self.property_vars.values()):
        compare_button_DD.config(state=tk.NORMAL)
        compare_button_TD.config(state=tk.NORMAL)
        compare_button_RD.config(state=tk.NORMAL)

      else:
        compare_button_DD.config(state=tk.DISABLED)
        compare_button_TD.config(state=tk.DISABLED)
        compare_button_RD.config(state=tk.DISABLED)




    left_frame=ttk.Frame(canvas)
    canvas.create_window((20,20), window=left_frame, anchor="nw")
 


    self.selected_mat = tk.StringVar(value="")

    self.material_vars = {}
    for idx, material in enumerate(materials):
      var = tk.BooleanVar(value=False)   
      chk = ttk.Checkbutton(left_frame, text=material, variable=var,command=validate)
      chk.grid(row=idx+1, column=0, sticky="w")
      self.material_vars[material] = var

    def compare_caller(angle):
      selected_materials = [mat for mat, var in self.material_vars.items() if var.get()]
      selected = [prop for prop, var in self.property_vars.items() if var.get()]

   
      
   
      for p in selected:
        buffer.add_photo(im.compare(address()[1],selected_materials,p,angle))



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
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var,command=validate)
      self.property_vars[prop] = var
      chk.pack(anchor="s", pady=2) 


  
    
    prop_separator = ttk.Separator(properties_frame, orient="horizontal")
    prop_separator.pack(pady=1)  



    compare_button_RD=ttk.Button(properties_frame,text="Compare RD",command=lambda :compare_caller("RD"),state=tk.DISABLED)
    compare_button_RD.pack(pady=10)  
    compare_button_TD=ttk.Button(properties_frame,text="Compare TD",command=lambda :compare_caller("DD"),state=tk.DISABLED)
    compare_button_TD.pack(pady=10)  
    compare_button_DD=ttk.Button(properties_frame,text="Compare DD",command=lambda :compare_caller("TD"),state=tk.DISABLED)
    compare_button_DD.pack(pady=10)  




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
 
    def validate():
      if self.selected_mat.get() and any(var.get() for var in self.property_vars.values()):
            anisotropy_button.config(state=tk.NORMAL)

      else:
          anisotropy_button.config(state=tk.DISABLED)





    self.selected_mat = tk.StringVar(value="")

    for material in (materials):
      radio = ttk.Radiobutton(left_frame, 
                              text=material,
                               value=material,
                                 variable=self.selected_mat
                                 ,command=validate)
      radio.pack(anchor="sw",pady=3)
    settings_button = ttk.Button(left_frame, text="Settings", command=lambda:Settings(self))
    settings_button.pack(pady=30)


    """Middle Frame"""




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
      chk = ttk.Checkbutton(properties_frame, text=prop, variable=var,command=validate)
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


    anisotropy_button=ttk.Button(properties_frame,text="Anisotropy",command=lambda:orientation(),state=tk.DISABLED)
    anisotropy_button.pack(pady=3)  

    scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)





# class PlasTab2(ttk.Frame):
#   def __init__(self,parent, notebook,materials,buffer):
#     super().__init__(parent)
#     Excel_processed=address()[1]

#     notebook.add(self, text="ORGANIZE")

#     mat_title = ttk.Label(self, text="Materials", font=("Arial", 15))
#     mat_title.pack(pady=20,anchor="nw",padx=37)

#     canvas=tk.Canvas(self, 
#                      scrollregion=(0,0,0,len(materials)*45),
#                      width=10,
#                      highlightthickness=0)
#     canvas.pack(side="left",expand=True,fill="both")
    
    
#     left_frame=ttk.Frame(canvas)
#     canvas.create_window((20,20), window=left_frame, anchor="nw")
 


#     self.selected_mat = tk.StringVar(value="")

#     for material in (materials):
#       radio = ttk.Radiobutton(left_frame, 
#                               text=material,
#                                value=material,
#                                  variable=self.selected_mat)
#       radio.pack(anchor="sw",pady=3)


#     """Middle Frame"""
    

#     properties_frame=ttk.Frame(self)
#     properties_frame.pack(side="left",padx=15,expand=True,fill="both",anchor="n")


#     prop_title = ttk.Label(properties_frame, text="Graph", font=("Arial", 15))
#     prop_title.pack(pady=20)

#     prop_separator = ttk.Separator(properties_frame, orient="horizontal")
#     prop_separator.pack(pady=1)  

#     properties = ["engineering", "true", "effective plastic strain","r-value"] 
#     self.property_vars = {}
#     for prop in (properties):
#       var = tk.BooleanVar(value=False)   
#       chk = ttk.Checkbutton(properties_frame, text=prop, variable=var)
#       self.property_vars[prop] = var
#       chk.pack(anchor="sw", pady=2) 


    
    
#     prop_separator = ttk.Separator(properties_frame, orient="horizontal")
#     prop_separator.pack(pady=1)  






   
 

#     scrollbar=ttk.Scrollbar(self,orient="vertical",command=canvas.yview)
#     scrollbar.pack(side="right", fill="y")
#     canvas.configure(yscrollcommand=scrollbar.set)


 

def main(): 
  ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix scaling so text isn't blurry on windows. Test on other devices
  App()


if __name__ == "__main__":
  main()

