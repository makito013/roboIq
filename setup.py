from cx_Freeze import setup, Executable 
  
setup(name = "SuperBot-IQ" , 
      version = "0.1" , 
      description = "" , 
      executables = [Executable("bot.py", icon="icon.ico")]) 