import os
import re
import getopt
import sys

from periodictable import elements


elist=[el.symbol for el in elements]
elistdash=[]
for el in elist:
    if not el == 'n':
        elistdash.append(el+'-')
#print(elistdash)

if len(sys.argv)<3:
    print("Use arguments:")
    print("cellNo time_steps input_file")
    sys.exit(2)
regno=int(sys.argv[1])
time_steps = int(sys.argv[2])
#time=sys.argv[2]
#timeUnit=sys.argv[3]
print ('Outputting table for region ', sys.argv[1]) #,' and time ',sys.argv[2],sys.argv[3])
infile=sys.argv[3]
#fin1 = open(infile)
volume = 0.0
times = []
isotopes = dict()


def getisotopelist(infile,regno):
    fin1 = open(infile)
    isotope=[]
#get all isotopes
    lines = fin1.readlines()
    for line in lines:
        ls=line.split()
        if len(ls)>10:
            if ls[0] in elist:
                isotope.append(ls[0]+'-'+ls[1])
    fin1.close()
    return set(isotope)


'''                
    while fin1.readline():
        for line in fin1:
            if 'region number .....' in line:
#        a,b,c,d,e = line.split()
                print("reg = ", regno)
            if 'volume .....' in line:
                print(line.split())
                volume = float(line.split()[3])
                print("vol = ", volume)
            if sys.argv[1] in line and 'region number .....' in line:
                break
#now looking up moving to the relevant time
#for line in fin1:
#    if  'after the last' in line and sys.argv[2] in line and sys.argv[3] in line:
#        break
#    isotope=[]
        for line in fin1:
            if  '--- output time ---' in line:
                time=float(line.split()[7])
                print(line.split())
                times.append(time)
                break
        for line in fin1:
            if  '[atoms/cc]' in line and '[uSv*m^2/h]' in line:
                break

#now getting table for the time
        i=-1
        for line in fin1:
            i=1
            ls = line.split()
#        for e in ls:
#            print(i,e)
#            i+=1
            if len(ls)>10:
                print(line)
                iso = ls[0]+'-'+ls[1]
                isotope.append(iso)
            else:
                break
    fin1.close()
    return set(isotope)
'''

'''
        try:
#         a1+a2= nuclide    a3=    atoms/cc      a5 =  radioactivity total[Bq]
        #a6=   relative err  a7=    rate[%]       a8-= decay heat [W/cc]  a11=half-life [s]   a12=dose dose-rate
            a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12 = line.split()
            i=i+1
            if len(a1)<3:
                iso = a1+'-'+a2
            else:
                iso = a1
            isotope.append(iso)
            print('13', iso)
        except ValueError or AttributeError:
            try:
                a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a12,a13 = line.split()
                i=i+1
                if len(a1)<3:
                    iso = a1+'-'+a2
                else:
                    iso = a1
                isotope.append(iso)
                print('12',iso)
#        print ('1',isotope[i],hlife[i])
#            print ('2',isotope[i],hlife[i])
            except ValueError or AttributeError:
                try:
                    a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11 = line.split()
                    i=i+1
                    if len(a1)<3:
                        iso = a1+'-'+a2
                    else:
                        iso = a1
                    isotope.append(iso)
               
                except ValueError or AttributeError:
                    break
'''
#    fin1.close()
#    return set(isotope)

def getisotable():
    totactdict=dict()
    atomsdict=dict()
    times = 0.0
    for line in fin1:
        if  '--- output time ---' in line:
            time=float(line.split()[7])
            print (time)
            times=time
            break
    for line in fin1:
        if  '[atoms/cc]' in line and '[uSv*m^2/h]' in line:
            break
    isotopes_local=[]
    #now getting table for the time
    i=-1
    for line in fin1:
        ls = line.split()

        if len(ls)>10:
            if len(ls[0])<3:
                iso = ls[0]+'-'+ls[1]
                #print(iso)
                isotopes_local.append(iso)
                atomscc=float(ls[2])
                totact=float(ls[4])
            else:
                iso = ls[0]
                isotopes_local.append(iso)
                atomscc=float(ls[2])
                totact=float(ls[4])
            atomsdict[iso]=atomscc #*volume
            totactdict[iso] =totact
        else:
            break
    return times, atomsdict, totactdict
'''
        try:
#         a1+a2= nuclide    a3=    atoms/cc      a5 =  radioactivity total[Bq]
        #a6=   relative err  a7=    rate[%]       a8-= decay heat [W/cc]  a11=half-life [s]   a12=dose dose-rate

            a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12 = line.split()
            i=i+1
            if len(a1)<3:
                iso = a1+'-'+a2
                #print(iso)
                isotopes_local.append(iso)
                atomscc=float(a3)
                totact=float(a5)
            else:
                iso = a1
                isotopes_local.append(iso)
                atomscc=float(a3)
                totact=float(a5)
            atomsdict[iso]=[atomscc*volume]
            totactdict[iso] =totact
w

        except ValueError or AttributeError:
            try:
                a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13 = line.split()
                i=i+1
                if len(a1)<3:
                    iso = a1+'-'+a2
                    isotopes_local.append(iso)
                    atomscc=float(a3)
                    totact=float(a5)
                else:
                    iso = a1
                    isotopes_local.append(iso)
                    atomscc=float(a3)
                    totact=float(a5)
                atomsdict[iso]=[atomscc*volume]
                totactdict[iso] =totact
                
#        print ('1',isotope[i],hlife[i])
#            print ('2',isotope[i],hlife[i])
            except ValueError or AttributeError:
                try:
                    a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11 = line.split()
                    i=i+1
                    if len(a1)<3:
                        iso = a1+'-'+a2
                        isotopes_local.append(iso)
                        atomscc=float(a3)
                        totact=float(a5)
                    else:
                        iso = a1
                        isotopes_local.append(iso)
                       
                        atomscc=float(a3)
                        totact=float(a5)
                    atomsdict[iso]=[atomscc*volume]
                    totactdict[iso] =totact
                    
                except ValueError or AttributeError:
                    break
    return times, atomsdict, totactdict

'''
                

    
isotope_set = getisotopelist(infile,regno)

isotope_list=[]
for el in elistdash:
    for el1 in isotope_set:
        if el in el1:
#            print(el, el1)
            isotope_list.append(el1)

print (isotope_list)


totactdict=dict()
totactdict['Time, s']=[]
totactdict['Time, h']=[]
totactdict['Time, d']=[]

atomsdict=dict()
atomsdict['Time, s']=[]
atomsdict['Time, h']=[]
atomsdict['Time, d']=[]
for iso in isotope_list:
    totactdict[iso]=[]
    atomsdict[iso]=[]

fin1 = open(infile)


for line in fin1:
    if 'region volume .....' in line:
#        a,b,c,d,e = line.split()
#        print(line.split())
        volume = float(line.split()[3])
        print("reg = ", regno)
    if sys.argv[1] in line.split() and 'region number .....' in line:
        break
#now looking up moving to the relevant time
#for line in fin1:
#    if  'after the last' in line and sys.argv[2] in line and sys.argv[3] in line:
#        break

for i in range (time_steps):
    time, atoms, totact= getisotable()
    print(time)
    totactdict['Time, s'].append(time)
    atomsdict['Time, s'].append(time)
    totactdict['Time, h'].append(time/3600)
    totactdict['Time, d'].append(time/3600/24)
    atomsdict['Time, h'].append(time/3600)
    atomsdict['Time, d'].append(time/3600/24)
    for iso in isotope_list:
        if iso in totact.keys():
            totactdict[iso].append(totact[iso])
            atomsdict[iso].append(atoms[iso])
        else:
            totactdict[iso].append(0.0)
            atomsdict[iso].append(0.0)


import pandas as pd
import numpy as np
print('Total activity')
totactdf = pd.DataFrame(totactdict)
print('Total atoms')
atomsdf = pd.DataFrame(atomsdict)



try:
    datatoexcel = pd.ExcelWriter('Activation_data.xlsx',mode='a')
except:
    datatoexcel = pd.ExcelWriter('Activation_data.xlsx')
totactdf.to_excel(datatoexcel, sheet_name='Activity in layer '+ str(regno)+', Bq pr mm')
atomsdf.to_excel(datatoexcel, sheet_name='Atoms in layer '+str(regno)+', atoms pr mm')

# Close the ExcelWriter
datatoexcel.close()

print(totactdf)
print(atomsdf)
fin1.close()
