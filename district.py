import sys
import urllib2
import copy
import re
import collections
from getclubs import *
import datetime
import pytz
import pickle

def byarea(c):
   return [c.area, c.order]

class District:
   def __init__(self, district):
      zoneName = 'America/Los_Angeles'
      now = datetime.datetime.now(pytz.timezone(zoneName))
      nowtt = now.timetuple()
      self.dashdate = '%4d%02d%02d' % (nowtt.tm_year, nowtt.tm_mon, nowtt.tm_mday)
      try:
         pklfp = open('district%d_%s.pkl' % (district, self.dashdate), 'r')
         dobj = pickle.load(pklfp)
         pklfp.close()
         self.clubs = dobj.clubs
         self.divs = dobj.divs
         self.areas = dobj.areas
#        print ('self.clubs = ', self.clubs)
         return
      except IOError:
         pass
      self.clubs = []
      clublist = getclubs(district)
#     print 'clublist = ', clublist
      iorder = 0
      for c in clublist:
         cluburl = 'http://dashboards.toastmasters.org/ClubReport.aspx?id=%08d' % (c[0])
         f = urllib2.urlopen(cluburl)
         ac = f.read()
         bodystart = ac.find('body start')
         bodyend = ac.find('body end')
         body = ac[bodystart:bodyend]
         dcpl = []
         for m in re.finditer("<td class='goalDescription'>", body):
            dcpl.append(m.start())
         dcpl.append(len(body))
# getclubs.py:Club = collections.namedtuple('Club', 'number name div area dcppts dcpcc dcpal dcpldr dcpnew dcptli dcpadmin nmember nbase')
         for i in range(len(dcpl)-1):
            if body[dcpl[i]:dcpl[i+1]].find("Competent Communicator (CC) awards") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[6] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">More Competent Communicator (CC) awards<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[6] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">Advanced Communicator (ACB, ACS, ACG) awards<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[7] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">More Advanced Communicator (ACB, ACS, ACG) awards<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[7] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">Leadership Awards (CL, ALB, ALS) or Distinguished Toastmaster (DTM) award<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[8] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">More CL, ALB, ALS, or DTM award <") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[8] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">New members<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[9] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">More new members<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[9] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">Club officers trained June-August<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[10] += 1
            elif body[dcpl[i]:dcpl[i+1]].find(">Membership-renewal dues on time<") > -1:
               if body[dcpl[i]:dcpl[i+1]].find("<img src='images/checkMark4.png' />") > -1:
                  c[11] += 1
         gmstr = "Goals Met<br /><span class='chart_table_big_numbers'>"
         igm = ac.find(gmstr)
         if igm > -1:
            lab = ac[igm+len(gmstr):igm+len(gmstr)+100].find('<')
            dcppts = int(ac[igm+len(gmstr):igm+len(gmstr)+lab])
            c[5] = dcppts
         memberstart = ac.find("<td class='chart_table_content'>Base</td>")
         memberend = ac.find("<td style='text-align:center; padding:1px;'>20 members or <br />a net growth of 5 new members</td></tr></table></td></tr></table></div>")
         members = ac[memberstart:memberend]
         ctbn = "<td class='chart_table_big_numbers'>"
         imbr = 0
         for m in re.finditer(ctbn, members):
            lab = members[m.start()+len(ctbn):].find('<')
            if imbr == 0:
               c[12] = int(members[m.start()+len(ctbn):m.start()+len(ctbn)+lab])
               print 'c[13] = ', c[12]
            elif imbr == 1:
               c[13] = int(members[m.start()+len(ctbn):m.start()+len(ctbn)+lab])
               print 'c[12] = ', c[13]
            imbr += 1
         c[4] = iorder
         iorder += 1
         self.clubs.append(Club(*c))
         print 'c = ', c
      self.divs = {}
      self.areas = {}
      for c in self.clubs:
         if not c.area in self.areas.keys():
            self.areas[c.area] = []
         self.areas[c.area].append(c)
      for a in self.areas.keys():
         div = getdivid(a)
         if not div in self.divs.keys():
            self.divs[div] = {}
         self.divs[div][a] = self.areas[a]

      print ('self.clubs = ', self.clubs)
      pklfp = open('district%d_%s.pkl' % (district, self.dashdate), 'w')
      pickle.dump(self, pklfp)
      pklfp.close()

   def dcpsort(self):
      bydcpd = collections.defaultdict(list)
      for c in self.clubs:
         bydcpd[c.dcppts].append(c)
      for i in range(11):
         bydcpd[i].sort(key=byarea)
      return bydcpd

   def areasort(self):
      byaread = collections.defaultdict(list)
      for c in self.clubs:
         byaread[c.area].append(c)
#     for i in bydcpd.keys():
#        byaread[i].sort(key=byarea)
      return byaread

   def get_dashdate(self):
      return self.dashdate
