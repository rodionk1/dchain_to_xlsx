import os
import re
import getopt
import sys
if len(sys.argv)<4:
    print("Use arguments:")
    print("time [time_unit] data_file output_file")
    sys.exit(2)
#regno=int(sys.argv[1])
time=sys.argv[1]
timeUnit=sys.argv[2]
totfact=0.0
print ('Outputting source terms for all regions and time ',sys.argv[1],sys.argv[2])
infile=sys.argv[3]
outfile=sys.argv[4]
fin1 = open(infile)
fo1=open(outfile,"w+")

fo1.write('[Source]\n')


for line in fin1:
    if sys.argv[1]+' '+sys.argv[2]+')' in line  and 'after the last' in line:
        # read spectrum
        print(line)
#        fo1.write(line)
        sourceLine=''
        while 'region=' not in sourceLine:
            # reading spectrum
            sourceLine=next(fin1)
#            print(sourceLine)
#            if 'S o u r c e' in sourceLine:
                #lineOut=sourceLine.replace('[ S o u r c e ]' ,'<source>')
#                fo1.write('<source>\n')
#            else if 'region=' not in sourceLine:
#                fo1.write(sourceLine)
            if 'totfact' in sourceLine:
                a,b,c,d,e,f,g,h,i,j,k,l=sourceLine.split()
                print (c, totfact)
                totfact=totfact+float(c)

fo1.write('totfact=')
fo1.write(str(totfact))
fo1.write('\n')
fin1.close()
fin1=open(infile)

for line in fin1:
    if sys.argv[1]+' '+sys.argv[2]+')' in line and 'region=' in line and 'after the last' in line:
        # read spectrum
        print(line)
        fo1.write(line)
        sourceLine=''
        while 'region=' not in sourceLine:
            # reading spectrum
            sourceLine=next(fin1)
#            print(sourceLine)
            if 'S o u r c e' in sourceLine:
                #lineOut=sourceLine.replace('[ S o u r c e ]' ,'<source>')
#                fo1.write('<source> ')
                fo1.write('\n')
            elif 'totfact' in sourceLine:
                a,b,c,d,e,f,g,h,i,j,k,l=sourceLine.split()
                if float(c)==0:
                    break
                fo1.write('<source> ')
                sourceLine1=sourceLine.replace('totfact',' ')
                fo1.write(sourceLine1)                
                fo1.write('ntmax = 500000 \n')
            elif 'x0' in sourceLine:
                sourceLine1=sourceLine.replace('=','=2319')
                fo1.write(sourceLine1)
            elif 'x1' in sourceLine:
                sourceLine1=sourceLine.replace('=','=2445')
                fo1.write(sourceLine1)
            elif 'y0' in sourceLine:
                sourceLine1=sourceLine.replace('=','=-13.5')
                fo1.write(sourceLine1)
            elif 'y1' in sourceLine:
                sourceLine1=sourceLine.replace('=','=6')
                fo1.write(sourceLine1)
            elif 'z0' in sourceLine:
                sourceLine1=sourceLine.replace('=','=4')
                fo1.write(sourceLine1)
            elif 'z1' in sourceLine:
                sourceLine1=sourceLine.replace('=','=23')
                fo1.write(sourceLine1)
            elif 'region=' not in sourceLine:
                fo1.write(sourceLine)
print (totfact)
fin1.close()


fo1.close()



