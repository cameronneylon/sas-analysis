import subprocess
import os
import os.path
import atsasparse as parse
import matplotlib.pyplot as plt
import urllib2

#CLASS for deriving Sturhrmann plots
class Structure:

    def __init__(self, pdb=None):
        """Init method for a toy structure class"""

        self.pdb = pdb
        self.pdbpath = self.pdb + '.pdb'
        self.structurerootpath = os.getcwd()
        
        self.initDir('crysol'+self.pdb)
        self.initDir('cryson'+self.pdb)
        self.initDir('stuhrmann'+self.pdb)

    def initDir(self, dirname):
        if os.path.exists(dirname) and os.path.isdir(dirname):
            pass
        else:
            os.mkdir(dirname)            

    def runCrysol(self):
        """Method for running crysol over the pdb""" 

        # crysol directory should exist and throwing error if not is appropriate
        os.chdir('crysol')
        pdbpath = '../' + self.pdbpath
        if os.path.exists(pdbpath):
            p = subprocess.Popen(['crysol', pdbpath], stdout=subprocess.PIPE)
            p.wait()
        
        else:
            print "Can't find file"
        
        os.chdir('..')
        return

    def getPDB(self):
        pdbcode=(self.pdb+'.pdb')
        pdbURL=('http://www.rcsb.org/pdb/files/'+pdbcode)
        pdb = urllib2.urlopen(pdbURL)
        pdbstring = pdb.read()
        file = open(pdbcode, 'w') 
        file.write(pdbstring)
        file.close() 

        
        
    def runCryson(self, d2o=0.0):
        """Method for running crysol over the pdb"""

        os.chdir('cryson')
        pdbpath = '../' + self.pdbpath
        d2o = str(d2o)
        if os.path.exists(pdbpath):
            p = subprocess.Popen(['cryson', pdbpath, '/d2o', d2o], stdout=subprocess.PIPE)
            p.wait()
        
        else:
            print "Can't find file"

        os.chdir('..')
        return

    def runStuhrmann(self, contrasts=[]):
        """Generating Data for a Sturhmann Plot, defaults to 10 points"""

        if contrasts == []: 
            c=raw_input('Number of Constrasts   ')        
            d=int(c)   #Converts the input to an integer
            e=d+1
            for contrast in range(e):
                contrasts.append(float(contrast)/d)
    

        for contrast in contrasts:
            self.runCryson(contrast)
            print contrast

        outfiles = os.listdir('cryson/')
        logfiles = filter(self.filterLogFiles, outfiles)
        
        stuhrvalues = []
        for log in logfiles:
            f = open(('cryson/' + log), 'r')
            logfile = f.read()
            params = parse.parse(logfile)
            #rg = params['_Excluded_Volume_+_Shell_)']
            rg = params['Rg_from_the_slope_of_net_intensity']
            contrast = params['Particle_contrast']
            stuhrvalues.append([contrast, rg])
        return stuhrvalues,e
        

    def filterLogFiles(self, filename):
        if filename[(len(filename)-3):len(filename)] == 'log': return True


#MAIN PROGRAM CALLS
whatPDB=raw_input('What PDB code?  ')
q=Structure(whatPDB)
q.getPDB()

s,e = q.runStuhrmann()
inv_cont=[]
rg_sq=[]
for point in s:
    inv_cont.append(1/point[0])
    rg_sq.append(point[1]**2)




#Regression analysis on plotted data
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from pylab import plot, title, show , legend

#Assign n and t to the inverse contrast and Rg**2 values
n=inv_cont
t=rg_sq

#Define function for sorting the values into consecutive order for the Stuhrmann plots
def cmp(a,b): 
    return int(100*a[0]-100*b[0])

#Take calculated Stuhrvalues and order them according to increasing inverse contrast
newlist =[]
for j in range(e):
    newlist.append([n[j],t[j]])


newlist.sort(cmp)

for j in range(e):
    n[j] = newlist[j][0]
    t[j] = newlist[j][1]

print(n[j],t[j])

#Linear regressison and plotting
xdata = n
ydata = t
polycoeffs = polyfit(xdata, ydata, 2)
print polycoeffs

#compute the mean square error
err=sqrt(sum((yfit-ydata)**2)/e)
print('Linear regression using polyfit')
print err

#plotting
yfit = polyval(polycoeffs, xdata)
title('Linear Regression Example')
plot(xdata, ydata, 'k.')
plot(xdata, yfit, 'r-')
legend(['original', 'regression'])
show()



while True:
    pass
    


        
        
        
