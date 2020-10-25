# Daily network operation

This code is based on Nornir framework, it helps you pull data from your network devices (Cisco). 


## HOW-TO run

First, fill the folowing files (You already find an example in the repo) :
+ input-output/input.csv ( input data for your infrastructure devices)

Then, run:

```
nor_main.py
```

Finaly, you can find output data in : input-output/output.csv
logs will be stored in /log folder (for advanced logs, please check nornir.log)

Note that processed files will be renamed into "dateinput-done.csv", so the program always pick a new file.
Make sure of file name : input.csv

