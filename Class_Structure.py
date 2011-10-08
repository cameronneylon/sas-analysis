import subprocess
import os
import os.path
import atsasparse as parse
import matplotlib.pyplot as plt
import urllib2


class Structure:

    def __init__(self, pdb=None):
        """Init method for a toy structure class"""

        self.pdb = pdb
        self.pdbpath = self.pdb + '.pdb'
        self.structurerootpath = os.getcwd()
        
        self.initDir('crysol')
        self.initDir('cryson')
        self.initDir('stuhrmann')

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
            for contrast in range(11):
                contrasts.append(float(contrast)/10)
    

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
            rg = params['Rg_(_Atoms_-_Excluded_Volume_+_She']
            contrast = params['Particle_contrast']
            stuhrvalues.append([contrast, rg])

        return stuhrvalues
        

    def filterLogFiles(self, filename):
        if filename[(len(filename)-3):len(filename)] == 'log': return True



whatPDB=raw_input('What PDB code?  ')
q=Structure(whatPDB)
q.getPDB()

s = q.runStuhrmann()
inv_cont=[]
rg_sq=[]
for point in s:
    inv_cont.append(1/point[0])
    rg_sq.append(point[1]**2)

plt.plot(inv_cont, rg_sq, 'ro')
plt.show()

while True:
    pass
    


#pdb=raw_input('pdb code?  ')
#p=Structure(pdb)
#p.runCrysol()
#p.runCryson()
#x=0.0
#while x<=1.0:
#    p.runCryson(x)
#    x=x+0.1

        
        
        
