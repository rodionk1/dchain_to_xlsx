import os
import re
import getopt
import sys
if len(sys.argv)<4:
    print("Use arguments:")
    print("cellNo time [time_unit] input_file")
    sys.exit(2)
regno=int(sys.argv[1])
time=sys.argv[2]
timeUnit=sys.argv[3]
print ('Outputting table for region ', sys.argv[1],' and time ',sys.argv[2],sys.argv[3])
infile=sys.argv[4]
fin1 = open(infile)
for line in fin1:
    if sys.argv[1] in line and 'region number .....' in line:
        break
#now moving to the relevant shutdown time
for line in fin1:
    if  'after the last' in line and sys.argv[2] in line and sys.argv[3] in line:
        break
# now getting lifetimes
for line in fin1:
    if  '[atoms/cc]' in line:
        break
#now at the start of lifetime table
isotope=list()
hlife=list()
i=-1
for line in fin1:
    try:
        a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12 = line.split()
        i=i+1
        if len(a1)<3:
            isotope.append(a1+a2)
            htime=float(a11)
            if htime<60:
                hlife.append("{:.2E}".format(htime)+'[s]')
            elif htime<3600:
                hlife.append("{:.2E}".format(htime/60.)+'[m]')
            elif htime<24*3600:
                hlife.append("{:.2E}".format(htime/3600.)+'[h]')
            elif htime<24*3600*365:
                hlife.append("{:.2E}".format(htime/3600./24.)+'[d]')
            else:
                hlife.append("{:.2E}".format(htime/3600./24./365)+'[y]')
        else:
            isotope.append(a1)
            htime=float(a11)
            if htime<60:
                hlife.append("{:.2E}".format(htime)+'[s]')
            elif htime<3600:
                hlife.append("{:.2E}".format(htime/60.)+'[m]')
            elif htime<24*3600:
                hlife.append("{:.2E}".format(htime/3600.)+'[h]')
            elif htime<24*3600*365:
                hlife.append("{:.2E}".format(htime/3600./24.)+'[d]')
            else:
                hlife.append("{:.2E}".format(htime/3600./24./365)+'[y]')
#        print ('1',isotope[i],hlife[i])
    except ValueError or AttributeError:
        try:
            a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13 = line.split()
            i=i+1
            isotope.append(a1+a2)
            htime=float(a12)
            if htime<60:
                hlife.append("{:.2E}".format(htime)+'[s]')
            elif htime<3600:
                hlife.append("{:.2E}".format(htime/60.)+'[m]')
            elif htime<24*3600:
                hlife.append("{:.2E}".format(htime/3600.)+'[h]')
            elif htime<24*3600*365:
                hlife.append("{:.2E}".format(htime/3600./24.)+'[d]')
            else:
                hlife.append("{:.2E}".format(htime/3600./24./365)+'[y]')
#            print ('2',isotope[i],hlife[i])
        except ValueError or AttributeError:
            try:
                a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11 = line.split()
                i=i+1
                isotope.append(a1)
                htime=float(a10)
                if htime<60:
                    hlife.append("{:.2E}".format(htime)+'[s]')
                elif htime<3600:
                    hlife.append("{:.2E}".format(htime/60.)+'[m]')
                elif htime<24*3600:
                    hlife.append("{:.2E}".format(htime/3600.)+'[h]')
                elif htime<24*3600*365:
                    hlife.append("{:.2E}".format(htime/3600./24.)+'[d]')
                else:
                    hlife.append("{:.2E}".format(htime/3600./24./365)+'[y]')
 #               print ('3',isotope[i],hlife[i])
            except ValueError or AttributeError:
                break

for line in fin1:
    if  'no. nuclide' in line:
        break
print ('nuclide  Bq/cc  T1/2  %  nuclide  W/cc  %')
for line in fin1:
#        print(line)
        try:
            a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18 = line.split()
            j=-1
            i=-1
            while j<0 and i<len(isotope)-1:
               i=i+1
               if a2+a3==isotope[i]:
                   j=10
            print (a2+a3+' '+a4+' '+hlife[i]+' '+a7+' '+a8+a9+' '+a10+' '+a13)
        except ValueError or AttributeError:
            try:
                a1,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18 = line.split()
                j=-1
                i=-1
                while j<0 and i<len(isotope)-1:
                    i=i+1
                    if a3 == isotope[i]:
                        j=10
                if a3 in isotope and a8+a9 in isotope and a14+a15 in isotope:
                    print (a3+' '+a4+' '+hlife[i]+' '+a7+' '+a8+a9+' '+a10+' '+a13)
                a1,a2,a3,a4,a5,a6,a7,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18 = line.split()
#                print(a1,a2,a3,a4,a5,a6,a7,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18)
#                print(a2+a3,a9,a14+a15)
                j=-1
                i=-1
                while j<0 and i<len(isotope)-1:
                    i=i+1
                    if a2+a3 == isotope[i]:
                        j=10
                if a2+a3 in isotope and a9 in isotope and a14+a15 in isotope:
                    print (a2+a3+' '+a4+' '+hlife[i]+' '+a7+' '+a9+' '+a10+' '+a13)
                a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a15,a16,a17,a18 = line.split()
                j=-1
                i=-1
                while j<0 and i<len(isotope)-1:
                    i=i+1
                    if a2+a3 == isotope[i]:
                        j=10
                if a2+a3 in isotope and a8+a9 in isotope and a15 in isotope:
                    print (a2+a3+' '+a4+' '+hlife[i]+' '+a7+' '+a8+a9+' '+a10+' '+a13)
            except ValueError or AttributeError:
                try:
                    a1,a3,a4,a5,a6,a7,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18 = line.split()
                    j=-1
                    i=-1
                    while j<0 and i<len(isotope)-1:
                        i=i+1
                        if a3 == isotope[i]:
                            j=10
                    if a3 in isotope and a9 in isotope and a14+a15 in isotope:
                        print (a3+' '+a4+' '+hlife[i]+' '+a7+' '+a9+' '+a10+' '+a13)
                    a1,a2,a3,a4,a5,a6,a7,a9,a10,a11,a12,a13,a15,a16,a17,a18 = line.split()
#                print(a1,a2,a3,a4,a5,a6,a7,a9,a10,a11,a12,a13,a14,a15,a16,a17,a18)
#                print(a2+a3,a9,a14+a15)
                    j=-1
                    i=-1
                    while j<0 and i<len(isotope)-1:
                        i=i+1
                        if a2+a3 == isotope[i]:
                            j=10
                    if a2+a3 in isotope and a9 in isotope and a15 in isotope:
                        print (a2+a3+' '+a4+' '+hlife[i]+' '+a7+' '+a9+' '+a10+' '+a13)
                    a1,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a15,a16,a17,a18 = line.split()
                    j=-1
                    i=-1
                    while j<0 and i<len(isotope)-1:
                        i=i+1
                        if a3 == isotope[i]:
                            j=10
#                    print(a3,a8+a9,a15)
                    if a3 in isotope and a8+a9 in isotope and a15 in isotope:
                        print (a3+' '+a4+' '+hlife[i]+' '+a7+' '+a8+a9+' '+a10+' '+a13)
                except ValueError or AttributeError:
                    try:
                        a1,a3,a4,a5,a6,a7,a9,a10,a11,a12,a13,a15,a16,a17,a18 = line.split()
                        j=-1
                        i=-1
                        while j<0 and i<len(isotope)-1:
                            i=i+1
                            if a3 == isotope[i]:
                                j=10
                        print (a3+' '+a4+' '+hlife[i]+' '+a7+' '+a9+' '+a10+' '+a13)
                    except ValueError or AttributeError:
                        break


