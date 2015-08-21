from HTMLParser import HTMLParser
def tr(s):
  for i, o in \
    { '\xc3\xa4':'ae', '\xc3\xb6':'oe', '\xc3\xbc':'ue', '\xc3\x9f':'ss', '\xc2\x80':'EUR' }.iteritems():
      s = s.replace(i, o)
  return s

class BilanzParser(HTMLParser):
  def bilanz(self, data):
    self._tag = ''
    self._bilanz = { 'Einnahmen': [], 'Ausgaben': [] }
    self._seite, self._posten, self._accumulator = [], [], []
    self._translate = { 'auml':'ae', 'ouml':'oe', 'uuml':'ue', 'szlig':'ss',
                        'Auml':'Ae', 'Ouml':'Oe', 'Uuml':'Ue', 'euro':'EUR' }
    self.feed(data)
    return self._bilanz
  def handle_starttag(self, tag, attrs):
    self._tag = tag
    if tag == 'tr':
      self._posten = [attrs]
      self._seite.append(self._posten)
    if tag == 'td': self._accumulator = []
  def handle_endtag(self, tag):
    if tag == 'td': self._posten.append("".join(self._accumulator))
    if tag == 'tr': self._posten = []
    if tag == 'table': self._seite = []
  def handle_data(self, data):
    data = tr(data)
    if self._tag == 'th' and data in self._bilanz: self._seite = self._bilanz[data]
    if self._tag == 'td': self._accumulator.append(data)
  def handle_entityref(self, name):
    self._accumulator.append(self._translate.get(name, name))

def echteEinnahme(text):
  return text.find('taatlich') == -1 and text.find('uschuss') == -1 and text.find('uschuess') == -1
def euros(data):
  return float(data.replace('.','').replace('EUR','').replace(' ','').replace(',','.'))

P = BilanzParser()

gliederung = {}
for l in open('gliederungen', 'r').read().split('\n'):
  if l.find(':') > -1:
    [key, value] = l.split(':')
    gliederung[key] = tr(value)

totalincome = {}
totalincomefilt = {}
ys = ['2012', '2013', '2014', '2015']

print "%40s  %s\n" % ("", "".join([" %10s " % y for y in ys]))
for vb, vn in sorted(gliederung.iteritems(), key=lambda item:item[1], reverse=True):
# gliederung.iteritems():
 print "%40s:" % vn,
# rel = 0
 for y in ys:
  data = open('%s/%s.txt' % (y, vb), 'r').read()
  bilanz = P.bilanz(data)

  #import pprint
  #pprint.PrettyPrinter(indent=4).pprint(bilanz)
  bilanz['Einnahmen'] = [l[1:3] + [euros(l[3])] for l in bilanz['Einnahmen'] if len(l)==4 and l[0]==[]]
#  for n in bilanz['Einnahmen']:
#    print n
#  totalincome += sum([l[2] for l in bilanz['Einnahmen']])
#  print sum([l[2] for l in bilanz['Einnahmen']])
  realeinnahme = sum([l[2] for l in bilanz['Einnahmen'] if echteEinnahme(l[1])])
  totalincomefilt[y] = totalincomefilt.get(y, 0) + realeinnahme
  print " %10.2f" % realeinnahme,
  if y == "2015":
    print " %10.2f" % (12 * realeinnahme / 6),
    totalincomefilt["2015b"] = totalincomefilt.get("2015b", 0) + (12 * realeinnahme / 6)
#  if rel == 0:
#    rel = realeinnahme
#  else:
#    print " (%5.1f%%)" % (100 * realeinnahme / rel),
 print
print
print "%40s:%s" % ("Gesamt", "".join(["  %10.2f" % totalincomefilt[y] for y in ys])),
print " %10.2f" % totalincomefilt["2015b"]
# %9.2f" % ("Gesamt", totalincomefilt)
# print totalincome
# print totalincomefilt
