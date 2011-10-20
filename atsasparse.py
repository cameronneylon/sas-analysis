from pyparsing import *

# Set up parsing of integers and reals and dates
cvtInt = lambda toks: int(toks[0])
cvtReal = lambda toks: float(toks[0])

integer = Combine(Optional(oneOf("+ -")) + Word(nums))\
    .setParseAction( cvtInt )

real = Combine(Optional(oneOf("+ -")) + Word(nums+'.') +
               Optional(Word(nums)) +
               Optional(oneOf("e E")+Optional(oneOf("+ -")) +Word(nums)))\
    .setParseAction( cvtReal )

date = Combine(integer + oneOf("/ -") + (integer | Word(alphas)) + 
                     oneOf("/ -") + integer)
time = Combine(integer + ":" + integer + ":" + integer)

# Set up parsing of paths
foldername = Word(alphanums)
upfolder = Literal("..")
pathelement = Combine(foldername | upfolder) + Literal("/")
path = Combine(OneOrMore(pathelement))

# Parser for PDB codes
pdbcode = Combine(Optional(path) + Word(alphanums) + Literal('.pdb'))

# Parser for parameter names, fillers and colons in log file
paramname = OneOrMore(Word(alphas, alphanums)).setParseAction(
                            lambda tokens : "_".join(tokens))
filler = OneOrMore('.').suppress()
colon = Literal(':').suppress()

# Parse name and value of parameters
nameAndValue = paramname + Optional(filler) + colon + (pdbcode | real | integer)

# Parse the log file header
def collapseprogname(tokens):
    text = "".join(tokens)
    return text.replace(" ", "").lower()

programname = Combine(Literal("C R Y S O ") + oneOf("N L")).setParseAction(collapseprogname)

versionnum = Combine(integer + "." + integer)
version = Literal("Version").suppress() + versionnum

hyphenfiller = Combine(Literal("-") + OneOrMore("-")).suppress()
spacer = hyphenfiller + OneOrMore(Word(alphas+"9 ( ) ,")).suppress() + hyphenfiller

headfoot = programname + version + hyphenfiller + date \
       + hyphenfiller + Group(OneOrMore(Word(alphas))) + date + time + hyphenfiller

# Parse angular scale and units
angularscale = Combine(Literal("in s =") + Word(alphanums+"/ ( ) *") +
                       Literal("[") + Word(alphanums+"/") + Literal("]"))

# Parse perdeuteration parameters
chainperd = Literal("Perdeuteration, chain [") + Word(alphas, max=1) + \
                    Literal("] (0<y<1)") + filler + colon + real

# Parse geometric centre
geomcenter = Literal("Geometric Center") + colon + \
                    real + real + real

# Parse the 
rgfromatomicstructure = Literal("olume + Shell ) "
                                ) + filler + colon + real
                       
# Parse output files
outputfiles = Word(alphas) + Literal("saved to file").suppress() + \
             Combine(Word(alphanums) + Literal('.') + Word(alphanums, min=3, max=3))

def parse(text):

    dict = {}
    for token, start, end in nameAndValue.scanString(text):
        dict[token[0]] = token[1]

    for token, start, end in outputfiles.scanString(text):
        dict[token[0]] = token[1]

    for token, start, end in rgfromatomicstructure.scanString(text):
        print token, start, end
        dict['Rg_from_atomic_structure'] = token[1]

    dict['perdeuteration'] = {}
    for token, start, end in chainperd.scanString(text):
        dict['perdeuteration'][token[1]] = token[3]

    headerfooter = headfoot.searchString(text)
    dict['program'] = headerfooter[0][0]
    dict['version'] = headerfooter[0][1]
    dict['start_date'] = headerfooter[0][4]
    dict['start_time'] = headerfooter[0][5]
    dict['terminate_date'] = headerfooter[1][4]
    dict['terminate_time'] = headerfooter[1][5]

    return dict
        



test = """
   C R Y S O N    Version 2.7  -- 06/11/09 
 
 
 -- Program  started  at   30-Sep-2011   16:25:10--
 
 --------  Real space resolution and grid  -------- 
 
  Maximum order of harmonics ............................ : 15
  Order of Fibonacci grid ............................... : 17
  Total number of directions ............................ : 2585
 
 ------------  Reciprocal space grid  -------------
 
   in s = 4*pi*sin(theta)/lambda [1/angstrom] 
  Maximum scattering angle .............................. : 0.5000
  Number of angular points .............................. : 51
 Perdeuteration, chain [A] (0<y<1) ...................... : 0.0
 Perdeuteration, chain [D] (0<y<1) ...................... : 0.0
 Perdeuteration, chain [E] (0<y<1) ...................... : 0.0
 Perdeuteration, chain [F] (0<y<1) ...................... : 0.0
 D2O fraction in solvent ................................ : 0.0
 
 --- Structural parameters (sizes in angstroms) --- 
 
 PDB file name .......................................... : ../3Q8L.pdb
  Number of atoms read .................................. : 3462
  Number of skipped rotamers ............................ : 72
  Number of discarded waters ............................ : 402
 Geometric Center:   24.336  -10.155    2.125
 Atomic     Rg   :  23.49       Envelope   Rg      :  23.17    
 Shape      Rg   :  23.48       Envelope  volume   : 0.7331E+05
 Shell    volume : 0.2656E+05   Envelope  surface  :  7909.    
 Shell      Rg   :  29.88       Envelope  radius   :  44.40    
 Shell    width  :  3.000       Envelope  diameter :  80.53    
 Molecular Weight: 0.5103E+05   Dry volume         : 0.6184E+05
 Displaced volume: 0.6023E+05   Average atomic rad.:  1.607    
 Solvent density : -.5620       Particle contrast  :  2.626    
 Number of residuals :               341
 Number of bases :               37
 
 -- No data fitting, parameters entered manually --
 
 Contrast of the solvation shell ........................ : -5.620e-2
 Average atomic radius .................................. : 1.608
 Excluded Volume ........................................ : 6.023e+4
 Solvent density ........................................ : -0.5620
 Average atomic volume .................................. : 17.40
 Radius of gyration from atomic structure
 Rg ( Atoms - Excluded Volume + Shell ) ................. : 23.42
 Rg from the slope of net intensity ..................... : 23.35
  
 ----------------  Output files  ------------------
  
 Coefficients   saved to file 3Q8L00.flm
 CRYSON data    saved to file 3Q8L00.sav
Intensities    saved to file 3Q8L00.int
Net amplitudes saved to file 3Q8L00.alm
 
   C R Y S O N    Version 2.7  -- 06/11/09  ----  terminated at   30-Sep-2011   16:25:11--
"""
test2= """
   C R Y S O L    Version 2.7  -- 11/03/10 
 
 
 -- Program  started  at   04-Oct-2011   18:33:41--
 
 --------  Real space resolution and grid  -------- 
 
  Maximum order of harmonics ............................ : 15
  Order of Fibonacci grid ............................... : 17
  Total number of directions ............................ : 2585
 
 ------------  Reciprocal space grid  -------------
 
   in s = 4*pi*sin(theta)/lambda [1/angstrom] 
  Maximum scattering angle .............................. : 0.5000
  Number of angular points .............................. : 51
 
 --- Structural parameters (sizes in angstroms) --- 
 
 PDB file name .......................................... : 4hhb.pdb
  Number of atoms read .................................. : 4558
  Number of discarded waters ............................ : 221
 Geometric Center:    0.004   -0.490   -0.004
  Number of carbons read ................................ : 2954
  Number of nitrogens read .............................. : 780
  Number of oxigens read ................................ : 806
  Number of sulfur atoms read ........................... : 12
  Number of phospor atoms read .......................... : 2
  Number of iron atoms read ............................. : 4
 For   17  zero directions radius    2.35 assumed
 Center of the excess electron density:  0.001  0.045  0.001
 Electron   Rg   :  23.53       Envelope   Rg      :  23.19    
 Shape      Rg   :  23.52       Envelope  volume   : 0.9572E+05
 Shell    volume : 0.3266E+05   Envelope  surface  :  9819.    
 Shell      Rg   :  30.98       Envelope  radius   :  36.56    
 Shell    width  :  3.000       Envelope  diameter :  72.02    
 Molecular Weight: 0.6451E+05   Dry volume         : 0.7819E+05
 Displaced volume: 0.8136E+05   Average atomic rad.:  1.621    
 Number of residuals :     574
 
 -- No data fitting, parameters entered manually --
 
 Solvent density ........................................ : 0.3340
 Contrast of the solvation shell ........................ : 3.000e-2
 Average atomic radius .................................. : 1.621
 Excluded Volume ........................................ : 8.136e+4
 Average atomic volume .................................. : 17.85
 Radius of gyration from atomic structure
 Rg ( Atoms - Excluded volume + Shell ) ................. : 24.63
 Rg from the slope of net intensity ..................... : 24.91
 Average electron density ............................... : 0.4235
  
 ----------------  Output files  ------------------
  
 Coefficients   saved to file 4hhb01.flm
 CRYSOL data    saved to file 4hhb01.sav
 Intensities    saved to file 4hhb01.int
 Net amplitudes saved to file 4hhb01.alm
 
   C R Y S O L    Version 2.7  -- 11/03/10  ----  terminated at   04-Oct-2011   18:33:43--
"""

if __name__ == "__main__":
    print parse(test)
    print "\n"
    print parse(test2)
