# -----------------------------------------------------------------------------
# Example: Test Feature Set via Python
# 
# This sample demonstrates how to start the test modules and test 
# configurations via COM API using a Python script.
# The script uses the included PythonBasicEmpty.cfg configuration but is  
# working also with any other CANoe configuration containing test modules  
# and test configurations. 
# 
# Limitations:
#  - only the first test environment is supported. If the configuration 
#    contains more than one test environment, the other test environments 
#    are ignored
#  - the script does not wait for test reports to be finished. If the test
#    reports are enabled, they may run in the background after the test is 
#    finished
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
import subprocess
from subprocess import *
import multiprocessing
import threading
from win32com.client import *
from win32com.client.connect import *
import time, os, msvcrt
import sys
import platform
import pathlib
import ctypes        # module for C data types
import enum
import psutil
import pyvisa as visa 
from timeit import default_timer as timer

start = timer()

if platform.system() == "Windows":
    SYSDIR='C:/T32'
    if platform.machine().endswith('64'):
        #win64
        APIFILE='t32api64.dll'
    else:
        #win32
        APIFILE='t32api.dll'
else:
    print("Unknown OS")
    quit()

APIDIR="C:/Flashing/TEST"
LIBFILE=os.path.join(os.sep,SYSDIR,APIDIR,APIFILE)
t32api=ctypes.cdll.LoadLibrary(LIBFILE)
T32_DEV = 1
t32api.T32_Config(b"NODE=",b"localhost")
t32api.T32_Config(b"PORT=", b"20001")
t32api.T32_Config(b"PACKLEN=",b"1024")


directory=r"C:\Flashing\TEST"
file_name='Logs1.txt'
Log_file_path = os.path.join(directory, file_name)


batch_file_path = r"C:\Flashing\TEST\KillProcesses.bat"

def Check_Disk_Space_available():
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if partition.device.startswith('C:'):
            disk_usage = psutil.disk_usage(partition.mountpoint)
            disk_space_available=int(disk_usage.free/(1024**3))
            
    return disk_space_available  
    
# Function to check if an application is already open
def is_application_open(application_name):
    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == application_name:
            return True
    return False

def applications_to_close(to_closes):
# Close the specified applications
    for app in to_closes:
        if is_application_open(app):
           try:
                subprocess.run(batch_file_path, shell=True, check=True)
                #subprocess.run(['powershell.exe', '-File', batch_file_path], check=True)
                print(f"Batch file {batch_file_path} executed successfully.")
           except subprocess.CalledProcessError as e:
                print(f"Error running the batch file: {e}")
           except FileNotFoundError:
                print(f"Batch file {batch_file_path} not found.")
           
        else:
            print(f"{app} is not open")
            
            
def DebuggerGetVal(variable_name,DebuggerVarName,capture_delay):

    variable_name = ctypes.c_int32(0)
    formatted_string = f"VAR.ADDWATCH.{DebuggerVarName}"
    byte_string = formatted_string.encode("utf-8")
    t32api.T32_Cmd(byte_string)
    time.sleep(capture_delay)

    formatted_string = f"EVAL Var.VALUE({DebuggerVarName})"
    byte_string = formatted_string.encode("utf-8")
    t32api.T32_Cmd(byte_string)
    t32api.T32_EvalGet(ctypes.byref(variable_name))
    loglist.append(variable_name.value)
    time.sleep(2)
    return variable_name.value

def Power_Supply_Reset():

	# Change this variable to the address of your instrument
	VISA_ADDRESS = 'GPIB0::5::INSTR'
		
	#Your instruments VISA address goes here!
	try:
		# Create a connection (session) to the instrument
		resourceManager = visa.ResourceManager()
		session = resourceManager.open_resource(VISA_ADDRESS)
	except visa.Error as ex:
		print('Couldn\'t connect to \'%s\', exiting now...' % VISA_ADDRESS)
		

	# Turn On power

	Output_cmd=':OUTPut:STATe 1'
	print(Output_cmd)
	session.write(Output_cmd)

	time.sleep(2)

	# set range to 30V

	Output_cmd=':SOURce:VOLTage:RANGe P30V'
	print(Output_cmd)
	session.write(Output_cmd)
	time.sleep(2)

	command=':APPLy 12'
	session.write(command)

	Userinput = '1'

	while True:
		 
		if(Userinput == '1'):
			# set voltage to 12V 
			command='OUTP OFF'
			session.write(command)
			time.sleep(1)
			command='OUTP ON'
			session.write(command)
			break
			
	# Close the connection to the instrument
	session.close()
	resourceManager.close()

	print('Power supply reset done.')


def Delete_temp_files(folder_path,file_to_delete):

	Temp_folder_path = folder_path
	Temp_file_to_delete = file_to_delete 
	# Combine the folder path and the file name to get the full file path
	file_path = os.path.join(Temp_folder_path, Temp_file_to_delete)
	# Check if the file exists before attempting to delete it
	if os.path.exists(file_path):
		try:
			
			os.remove(file_path)
			print(f"File '{Temp_file_to_delete}' has been deleted.")
		except OSError as e:
			print(f"Error deleting the file: {e}")
	else:
		#print(f"File '{Temp_file_to_delete}' does not exist in the specified folder.")
		pass

		
def T32_close():	

	rc1 = t32api.T32_Init()
	if(rc1 == 0):
		debugger_init_state = 1
	else:
		debugger_init_state = 0
	for y in range(0,3):
		rc1 = t32api.T32_Attach(T32_DEV)
		if rc1 == 0:
			debugger_open_state = 1
			break	
		else:
			debugger_open_state = 0
			
			
	rc1 = t32api.T32_Ping()
	if(rc1 == 0):
		debugger_ping_state = 1
	else:
		debugger_ping_state = 0

	time.sleep(2)

	if((rc1 == 0 ) and (debugger_init_state == 1) and (debugger_open_state == 1) and (debugger_ping_state == 1)):
		t32api.T32_Cmd(b"QUIT")
		t32api.T32_Exit()
		print("Trace32 closed")
	else:
		print("Trace32 is not opened")
		t32api.T32_Exit()
	
# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if (Check_Disk_Space_available() <=5):
    assert Check_Disk_Space_available() >=5, "Low Disk Space available"
    sys.exit(1)
	

		
          
to_close = ["CANoe64.exe","notepad.exe"] 
applications_to_close(to_close)
T32_close()
Delete_temp_files(r"C:\Users\GID_Honda_SRR6p_1\AppData\Local\Temp\gen_py\3.10","7F31DEB0-5BCC-11D3-8562-00105A3E017Bx0x1x56.py")
Delete_temp_files(r"C:\Users\GID_Honda_SRR6p_1\AppData\Local\Temp\gen_py\3.10\__pycache__","7F31DEB0-5BCC-11D3-8562-00105A3E017Bx0x1x56.cpython-310.pyc")
Delete_temp_files(r"C:\Flashing\TEST","Logs.txt")
Delete_temp_files(r"C:\Flashing\TEST","Logs1.txt")
Power_Supply_Reset()
time.sleep(10)

subprocess.call([r"C:\Flashing\TEST\_start_powerview_SMP.bat"])
time.sleep(90)#90


rc = t32api.T32_Init()
for x in range(0,3):
    rc = t32api.T32_Attach(T32_DEV)
    if rc == 0:
        break
if rc != 0:
   t32api.T32_Exit()
   assert (rc == 0),"Connection to Trace32 Failed"
   sys.exit(1) 
rc = t32api.T32_Ping()
if rc != 0:
   t32api.T32_Exit()
   assert (rc == 0),"Connection to Trace32 Failed after Ping"
   sys.exit(1)
   
reset_count=0
loglist=[]
t32api.T32_Cmd(b"Break.Delete /All")
t32api.T32_Cmd(b"SYStem.Option DUALPORT ON")
time.sleep(2)
t32api.T32_Cmd(b"DO Quit SMP")
time.sleep(25)
t32api.T32_Cmd(b"GO")   
Count_5ms = ctypes.c_int32(0)
t32api.T32_Cmd(b"VAR.ADDWATCH.cnt_5ms")
time.sleep(30)
t32api.T32_Cmd(b"EVAL Var.VALUE(cnt_5ms)")
t32api.T32_EvalGet(ctypes.byref(Count_5ms))	
while(Count_5ms.value < 5000):
    t32api.T32_Cmd(b"system.resettarget")
    time.sleep(3)
    t32api.T32_Cmd(b"GO")
    reset_count = reset_count + 1
    t32api.T32_Cmd(b"Var.DelWatch.cnt_5ms")
    Valx=DebuggerGetVal("Count_5ms","cnt_5ms",30)
    if(Valx > 5000):
        loglist.append(Valx)
        break
	
loglist.append(Count_5ms.value)
print("5 ms count value = " + str(Count_5ms.value))
Wakeup_status = ctypes.c_int32(0)
t32api.T32_Cmd(b"VAR.ADDWATCH.Radar_Data.Init_Status")
time.sleep(5)
t32api.T32_Cmd(b"EVAL Var.VALUE(Radar_Data.Init_Status)")
t32api.T32_EvalGet(ctypes.byref(Wakeup_status))
print("Wake up value = " + str(Wakeup_status.value))
loglist.insert(1,Wakeup_status.value)
time.sleep(2)

val1=DebuggerGetVal("release_version","Release_Revision",2)
val2=DebuggerGetVal("Promote_version","Promote_Revision",2)
val3=DebuggerGetVal("Field_version","SW_Field",2)
sw_version = f"{val1}.{val2}.{format(val3,'x')}"
print(f"SW version = {sw_version}")
print(f"Reset count = {reset_count}")
t32api.T32_Cmd(b"QUIT")

if((loglist[0] >= 5000) and (loglist[1] == 3)):
        if os.path.exists(Log_file_path):
            with open(file_name, 'r') as file:
                first_line = file.readline().strip()
                file.close()
                if(first_line == "ECU Wakeup Failed."):
                    file1open=open(file_name,'w')
                    file1open.write("ECU Wakeup Successful.")
                    file1open.close()
                elif(first_line == "ECU Wakeup Successful."):
                    file2open=open(file_name,'w')
                    file2open.write("ECU Wakeup Successful.")
                    file2open.close()
                    

        else:
            assert "Log file not found"
   
elif((loglist[0] < 5000) and (loglist[1] != 3)):
        if os.path.exists(Log_file_path):
            with open(file_name, 'r') as file:
                first_line = file.readline().strip()
                file.close()
                if(first_line == "ECU Wakeup Failed."):
                    file1open=open(file_name,'w')
                    file1open.write("ECU Wakeup Failed.")
                    file1open.close()
                elif(first_line == "ECU Wakeup Successful."):
                    file2open=open(file_name,'w')
                    file2open.write("ECU Wakeup Failed.")
                    file2open.close()
                    
        else:
            assert "Log file not found"

                                       
content2 = open(r"C:\Flashing\TEST\Logs.txt","r")
content1 = open(r"C:\Flashing\TEST\Logs1.txt","r")
check1=[]
check2=[]
for line in content1:
    check1.append(line.strip()) 
for line1 in content2:
    check2.append(line1.strip())
    
content1.close()
content2.close()  
time.sleep(2)  
if((((loglist[1] == 3) and (loglist[0] >=5000)) or (check1[0] == "ECU Wakeup Successful.")) and (check2[0] == "Flashing Successful.")):
    print("Success")
    end=timer()
    print("Execution time = " + str(end-start) + " Sec")
    sys.exit(0) 
    
elif(loglist[0] < 5000):
    print("Fail Reason ---> Counter 5_ms not updated to value 5000")
    end=timer()
    print("Execution time = " + str(end-start) + " Sec")
    sys.exit(1) 
else:
    print("Fail Reason ---> Flashing Success but ECU wakeup failed")
    end=timer()
    print("Execution time = " + str(end-start) + " Sec")
    sys.exit(1) 
