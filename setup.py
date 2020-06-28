from cx_Freeze import setup, Executable 
  
build_exe_options = {
                     "packages": ["talib"],
                     }
                     
setup(name = "SuperBot-IQ" , 
      version = "0.1" , 
      description = "" , 
      options = {"build_exe": build_exe_options},
      executables = [Executable("WinTrader-SuperBot.py", icon="icon.ico")]) 