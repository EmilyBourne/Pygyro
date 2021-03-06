from shlex  import split
import subprocess
import os

# ~ bashCommand = "pytest pygyro --cov=pygyro --cov-report=term -k='not long' > cov_out.txt 2> cov_err.txt"
bashCommand = "coverage report -m > cov_out.txt 2> cov_err.txt"
try:
    process = subprocess.run(bashCommand, shell=True, check=True)
except:
    file = open("cov_out.txt", "r") 
    out = file.read()
    file.close()
    os.remove("cov_out.txt")
    out = out[2:-1]
    out = out.replace("\\n","\n")
    print(out)
    
    file = open("cov_err.txt", "r") 
    err = file.read()
    file.close()
    os.remove("cov_err.txt")
    err = err[2:-1]
    err = err.replace("\\n","\n")
    print(err)
    raise
else:
    file = open("cov_out.txt", "r") 
    out = file.read()
    file.close()
    os.remove("cov_out.txt")
    out = out[2:-1]
    out = out.replace("\\n","\n")
    print(out)

    file = open("cov_err.txt", "r") 
    err = file.read()
    file.close()
    os.remove("cov_err.txt")
    err = err[2:-1]
    err = err.replace("\\n","\n")
    print(err)

    if (process.returncode==0):
        i = out.find("TOTAL")
        totline = out[i:]
        pc=float(totline[totline.rfind(" "):totline.rfind("%")])
        assert(pc>=90)
