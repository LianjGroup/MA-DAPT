# **MA-DAPT**  

**Material Analysis - Data Processing & Tensile Testing**  

MA-DAPT is a powerful yet user-friendly application designed to visualize tensile test data with an intuitive graphical interface. It simplifies the process of analyzing material properties by generating stress-strain graphs effortlessly.  

## **Features**  
- **Graphical Visualization** – Easily generate and analyze stress-strain curves.  
- **Built-in Material Database** – Comes preloaded with **9 materials**.  
- **User-Friendly Interface** – No coding required; just import your data and start analyzing.  

## **Screenshot**  
![MA-DAPT Screenshot](https://github.com/user-attachments/assets/04986549-523f-45ea-8e60-07a19a3c5e79)  

## Installation
💻 Windows: Precompiled executable available.  
🍏🐧 Mac & Linux: Builds must be created manually.  
### Building instructions

1. Install python 
2. Run this to install all needed modules
```Bash
pip install -r requirements.txt
```
3. Download and extract source code
4. Open folder in code editor
   
5. Build executable:
```bash  
pip install pyinstaller
pyinstaller --onefile --windowed FinalGUI.py
```
NOTE: Release will be in Dist folder. The config file and data banks need to be moved manually.


