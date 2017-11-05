import sys
import urllib2
import copy
import collections
import re

AREA     = 0
CLUBNUM  = 1
CLUBNAME = 2
RENEWAL  = 3

renews0 = "<td class='Grid_Table_num_yellow Grid_Title_top4'>"
renews1 = "<td class='Grid_Table_num Grid_Title_top4'>"

Club = collections.namedtuple('Club', 'number name div area order dcppts dcpcc dcpal dcpldr dcpnew dcptli dcpadmin nmember nbase late october april new charter')

def twodigit(s):
   if (len(s) == 2) and (s[0].isdigit()) and (s[1].isdigit()):
      return True
   return False

def getdivid(area):
   divnum = area/10
   return chr(ord('A') + divnum - 1)

def getclubs(district):
   disturl = 'http://dashboards.toastmasters.org/District.aspx?id=%s&hideclub=1'% (district)
   f = urllib2.urlopen(disturl)
   ac = f.read()
   annd = {}
   i = 0
   done = False
   while not done:
      iarea = ac[i:].find('Area')
      if iarea == -1:
         done = True
      else:
         ans = ac[i+iarea:i+iarea+100]
         ansl = ans.split()
         if twodigit(ansl[1]):
            narea = int(ansl[1])
            annd[(i+iarea+5, AREA)] = narea
            i += iarea+7
         else:
            i += iarea+5
   i = 0
   done = False
   while not done:
      icradstem = ac[i:].find('ClubReport.aspx?id=')
      if icradstem == -1:
         done = True
      else:
         nclub = int(ac[i+icradstem+19:i+icradstem+27])
         annd[(i+icradstem+19, CLUBNUM)] = nclub
         i += icradstem+27
   i = 0
   done = False
   while not done:
      iname = ac[i:].find('title=')
      if iname == -1:
         done = True
      else:
         sq0 = ac[i+iname:].find("'")
         sq1 = ac[i+iname+sq0+1:].find("'")
         annd[(i+iname+sq0+1, CLUBNAME)] = ac[i+iname+sq0+1:i+iname+sq0+sq1+1]
         i += iname + sq0 + sq1
   for m in re.finditer(renews0, ac):
      endtd = ac[m.end():].find('</td>')
      annd[(m.end(), RENEWAL)] = int(ac[m.end():m.end()+endtd])
   for m in re.finditer(renews1, ac):
      endtd = ac[m.end():].find('</td>')
      annd[(m.end(), RENEWAL)] = int(ac[m.end():m.end()+endtd])
   als = annd.keys()
   als.sort()
   ia = 0
   clublist = []
   for ia in range(len(als)):
      if als[ia][1] == CLUBNUM:
         nclub = annd[als[ia]]
         ja = ia - 1
         while ja >= 0:
            if als[ja][1] == AREA:
               narea = annd[als[ja]]
               break
            ja -= 1
         ka = ia + 1
         while ka < len(als):
            if als[ka][1] == CLUBNAME:
               clubname = annd[als[ka]]
               break
            ka += 1
         la = ia + 1
         renl = []
         while len(renl) < 7:
            if als[la][1] == RENEWAL:
               renl.append(annd[als[la]])
            if la > len(als):
               print 'did not find seven'
               sys.exit()
            la += 1
         late = renl[0]
         october = renl[1]
         april = renl[2]
         new = renl[4]
         charter = renl[5]
         clubdata = [nclub, clubname, getdivid(narea), narea] + [0] * 10 + [late, october, april, new, charter]
         clublist.append(clubdata)
   return clublist
