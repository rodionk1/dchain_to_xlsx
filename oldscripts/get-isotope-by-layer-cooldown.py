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
    print("time_steps input_file")
    sys.exit(2)
#regno=int(sys.argv[1])
time_steps = int(sys.argv[1])
#time=sys.argv[2]
#timeUnit=sys.argv[3]
#print ('Outputting table for region ', sys.argv[1]) #,' and time ',sys.argv[2],sys.argv[3])
infile=sys.argv[2]
#fin1 = open(infile)
try:
    samplename=sys.argv[3]
except:
    samplename=''
volume = 0.0
times = []
isotopes = dict()


activitydfs=[]
atomsdfs=[]

def getisotopelist(infile,regno=0):
    fin1 = open(infile)
    isotope=[]
#get all isotopes
    lines = fin1.readlines()
    for line in lines:
        ls=line.split()
        if len(ls)>10:
            if ls[0] in elist:
                isotope.append(ls[0]+'-'+ls[1])
                print("found isotope ", ls[0]+'-'+ls[1])
            elif ls[0][:2] in elist and (ls[0][2]=='1' or ls[0][2]=='2'):
                isotope.append(ls[0][:2]+'-'+ls[0][2:])
                print("found isotope ", ls[0][:2]+'-'+ls[0][2:])
    fin1.close()
    return set(isotope)



def getregionlist(infile):
    fin1 = open(infile)
    regionlist=[]
#get all isotopes
    lines = fin1.readlines()
    for line in lines:
        if 'region number' in line:
            ls=line.split()
            regionlist.append(ls[3])
    fin1.close()
    return regionlist
#    fin1.close()
#    return set(isotope)

def getisotable():
    totactdict=dict()
    atomsdict=dict()
    dose1mdict=dict()
    t12dict=dict()
    times = 0.0
    for line in fin1:
        if  '--- output time ---' in line:
            time=float(line.split()[7])
            #print (time)
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
                dose1m=float(ls[-1])
                t12s = float(ls[-2])
            else:
                iso = ls[0][:2]+'-'+ls[0][2:]
                isotopes_local.append(iso)
                atomscc=float(ls[1])
                totact=float(ls[3])
                dose1m=float(ls[-1])
                t12s = float(ls[-2])
               # print ('**',iso)
               # print (ls)
               # print (atomscc, totact)

            atomsdict[iso]=atomscc*volume
            totactdict[iso] =totact
            dose1mdict[iso]=dose1m
            if t12s > 31536000:
                t12dict[iso] = [t12s, str( round(t12s/31536000,2))+' [y]']
            elif t12s > 2*86400:
                t12dict[iso] = [t12s, str( round(t12s/86400,2))+' [d]']
            elif t12s > 7200:
                t12dict[iso] = [t12s, str( round(t12s/3600,2))+' [h]']
            elif t12s > 120:
                t12dict[iso] = [t12s, str( round(t12s/60,2))+' [m]']
            else:
                t12dict[iso]= [t12s, str(t12s)+' [s]']
        else:
            break
    return times, atomsdict, totactdict, dose1mdict, t12dict
                
def get_isomax(df,num):
    c=df.columns
    cols = [x for x in c if not 'Time' in x]
    #print("isomax")
#    print(cols)
    maxval = dict()
    for col in cols:
        maxval[col] = df[col].max()
    
#    print(maxval)
    maxvalues=list(maxval.values())
    maxvalues=sorted(maxvalues, key=float, reverse=True)
    print(maxvalues)
    outputvals = maxvalues[:num]

    outputcols=list()

    for col in cols:
        if maxval[col] in outputvals:
            outputcols.append(col)
    return outputcols

print ("functions defined")


isotope_set = getisotopelist(infile)

print (isotope_set)

isotope_list=[]
for el in elistdash:
    for el1 in isotope_set:
        if el in el1:
#            print(el, el1)
            isotope_list.append(el1)

#print (isotope_list)


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

regions = getregionlist(infile)

print(regions)


import pandas as pd
import numpy as np

fin1 = open(infile)


for region in regions:
    totactdict=dict()
    totactdict['Time, s']=[]
    totactdict['Time, h']=[]
    totactdict['Time, d']=[]

    atomsdict=dict()
    atomsdict['Time, s']=[]
    atomsdict['Time, h']=[]
    atomsdict['Time, d']=[]

    dose1mdict=dict()
    dose1mdict['Time, s']=[]
    dose1mdict['Time, h']=[]
    dose1mdict['Time, d']=[]

    for iso in isotope_list:
        totactdict[iso]=[]
        atomsdict[iso]=[]
        dose1mdict[iso]=[]

    regno = int(region)
    for line in fin1:
        if 'region volume .....' in line:
#        a,b,c,d,e = line.split()
#        print(line.split())
            volume = float(line.split()[3])
            #print("reg = ", regno)
        if region in line.split() and 'region number .....' in line:
            break
#now looking up moving to the relevant time
#for line in fin1:
#    if  'after the last' in line and sys.argv[2] in line and sys.argv[3] in line:
#        break
    decaytimesdict = dict()
    t0=0
    for i in range (time_steps):
        
        time, atoms, totact, dose1m, time12 = getisotable()
        if i==0:
            t0=time
        for iso in time12.keys():
            decaytimesdict[iso] = time12[iso]
        print(time, time-t0)
        time-=t0
        totactdict['Time, s'].append(time)

        totactdict['Time, h'].append(time/3600)
        totactdict['Time, d'].append(time/3600/24)
        atomsdict['Time, s'].append(time)
        atomsdict['Time, h'].append(time/3600)
        atomsdict['Time, d'].append(time/3600/24)

        dose1mdict['Time, s'].append(time)
        dose1mdict['Time, h'].append(time/3600)
        dose1mdict['Time, d'].append(time/3600/24)
        for iso in isotope_list:
            if iso in totact.keys():
                totactdict[iso].append(totact[iso])
                atomsdict[iso].append(atoms[iso])
                dose1mdict[iso].append(dose1m[iso])
            else:
                totactdict[iso].append(0.0)
                atomsdict[iso].append(0.0)
                dose1mdict[iso].append(0.0)



    #print('Total activity')
    totactdf = pd.DataFrame(totactdict)
    #print('Total atoms')
    atomsdf = pd.DataFrame(atomsdict)

    dosedf = pd.DataFrame(dose1mdict)

    decaytimesdf = pd.DataFrame(decaytimesdict)
    
    maxcols = get_isomax(totactdf,30)

    totactmaxdf = totactdf[['Time, s','Time, h','Time, d']+maxcols]
    atomsmaxdf = atomsdf[['Time, s','Time, h','Time, d']+maxcols]
    dosemaxdf = dosedf[['Time, s','Time, h','Time, d']+maxcols]
    decaytimesmaxdf = decaytimesdf[maxcols]

    activitydfs.append(totactdf)
    
    try:
        datatoexcel = pd.ExcelWriter('Activation_data_'+samplename+'.xlsx',mode='a')
    except:
        datatoexcel = pd.ExcelWriter('Activation_data_'+samplename+'.xlsx')
    totactdf.to_excel(datatoexcel, sheet_name='Activity in cell '+ str(regno)+', Bq')
    atomsdf.to_excel(datatoexcel, sheet_name='Atoms in cell '+str(regno)+', atoms')

    dosedf.to_excel(datatoexcel, sheet_name='Dose at 1 m,cell '+str(regno)+',uSv.m2.h-1')

# Close the ExcelWriter
    datatoexcel.close()



    try:
        datatoexcel = pd.ExcelWriter('Activation_data_max30_'+samplename+'.xlsx',mode='a')
    except:
        datatoexcel = pd.ExcelWriter('Activation_data_max30_'+samplename+'.xlsx')
    totactmaxdf.to_excel(datatoexcel, sheet_name='Activity in cell '+ str(regno)+', Bq')
    atomsmaxdf.to_excel(datatoexcel, sheet_name='Atoms in cell '+str(regno)+', atoms')
    dosemaxdf.to_excel(datatoexcel, sheet_name='Dose at 1m, cell '+str(regno)+',uSv.m2.h-1')
    decaytimesmaxdf.to_excel(datatoexcel, sheet_name='Half-life times')

# Close the ExcelWriter
    datatoexcel.close()


    #display(totactdf)
    #display(atomsdf)
fin1.close()

totalactivation=totactdf[['Time, s','Time, h','Time, d']]

for df in activitydfs:
    for iso in isotope_list:
        if iso in totalactivation.columns:
            totalactivation[iso]=totalactivation[iso]+df[iso]
        else:
            totalactivation[iso]=df[iso]

print(maxcols)
maxcols = get_isomax(totalactivation,30)
print(maxcols)


for isotope in maxcols:
#now looking up moving to the relevant time
#for line in fin1:
#    if  'after the last' in line and sys.argv[2] in line and sys.argv[3] in line:
#        break
    print(isotope)
    actdict=dict()
    atomdict=dict()
    for regno in regions:
        actdict[regno]=[]
        atomdict[regno]=[]

    for regno in regions:
        fin1 = open(infile)
   
        for line in fin1:
            if 'region volume .....' in line:
#        a,b,c,d,e = line.split()
#        print(line.split())
                volume = float(line.split()[3])
                #print("reg = ", regno)
            if regno in line.split() and 'region number .....' in line:
                break

        for i in range (time_steps):
            time, atoms, totact, dose1m, time12  = getisotable()
            #print(time,totact)
        #totactdict['Time, s'].append(time)
        #atomsdict['Time, s'].append(time)
        #totactdict['Time, h'].append(time/3600)
        #totactdict['Time, d'].append(time/3600/24)
        #atomsdict['Time, h'].append(time/3600)
        #atomsdict['Time, d'].append(time/3600/24)
            
            if isotope in totact.keys():
                actdict[regno].append(totact[isotope])
                atomdict[regno].append(atoms[isotope])
                #print(time,totact[isotope])
            else:
                actdict[regno].append(0.0)
                atomdict[regno].append(0.0)
        
        #print (actdict)
        fin1.close()

    #print('Total activity')
    #print(actdict)
    
    actdf = pd.concat([totactdf[['Time, s','Time, h','Time, d']], pd.DataFrame(actdict)],axis=1)

    atomdf = pd.concat([totactdf[['Time, s','Time, h','Time, d']], pd.DataFrame(atomdict)],axis=1)





    try:
        datatoexcel = pd.ExcelWriter('Activation_data_max30_by_iso_'+samplename+'.xlsx',mode='a')
    except:
        datatoexcel = pd.ExcelWriter('Activation_data_max30_by_iso_'+samplename+'.xlsx')
    actdf.to_excel(datatoexcel, sheet_name=isotope+' activity in layer, Bq')
    atomdf.to_excel(datatoexcel, sheet_name=isotope+' atoms in layer')

# Close the ExcelWriter
    datatoexcel.close()


#    print(totactdf)
#    print(atomsdf)
   
