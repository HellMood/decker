import urllib.request
import random
import multiprocessing
import re
import xml.etree.ElementTree
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Rect, Drawing
from PIL import Image as PILImage

customsize = (6.9 * cm, 9.4 * cm)

# doc = SimpleDocTemplate("/home/hel/hello.pdf",pagesize=customsize,
#                         rightMargin=0,leftMargin=0,
#                         topMargin=0.085*cm+0.35/2*cm,bottomMargin=0)

doc = SimpleDocTemplate("/home/hel/hello.pdf", pagesize=customsize,
                        rightMargin=0, leftMargin=0,
                        topMargin=0.1 * cm, bottomMargin=0)
Story = []

decklist = '/home/hel/deckerdata/UR steal hate.cod'

e = xml.etree.ElementTree.parse(decklist).getroot()
cardnamelist = []
cardnumberslist = []

for child in e:
    print(child.tag, child.attrib)
    if child.tag == 'zone':
        if child.attrib['name'] == 'main':
            print('here')
            for subchild in child:
                print(subchild.tag, subchild.attrib)
                cardnamelist.append(subchild.attrib['name'])
                cardnumberslist.append(subchild.attrib['number'])


# cardname = cardnamelist[0]

# query_adress = "http://magiccards.info/query?q=" + cardname.replace(' ', '+') + "&v=card&s=cname"

QUERIES = []
count = len(cardnamelist)

for c in range(0, count):

    query_adress = "http://magiccards.info/query?q=" + cardnamelist[c].replace(' ', '+') + "&v=card&s=cname"
    QUERIES.append([query_adress, 1])

print (QUERIES)

def get_content(url):

    url = url[0]
    number = url[1]

    url = urllib.request.urlopen(url)
    s = url.read()
    content = s.decode('utf-8')
    targetpattern = 'http://magiccards.info/scans/'
    pos1 = str.find(content, targetpattern)
    pos2 = str.find(content, '"', pos1)
    img_adress = content[pos1:pos2]
    print(img_adress)

    img = urllib.request.urlopen(img_adress)
    s = img.read()

    return s


pool = multiprocessing.Pool(processes=128)  # play with ``processes`` for best results
results = pool.map(get_content, QUERIES)  # This line blocks, look at map_async
# for non-blocking map() call
pool.close()  # the process pool no longer accepts new tasks
pool.join()  # join the processes: this blocks until all URLs are processed

pb = PageBreak()

resultlength = len(results)

for r in range(0,resultlength):

    if(r>=55):
        continue

    targetfilename = '/home/hel/deckerdata/'+cardnamelist[r]+'.jpg'
    f = open(targetfilename, 'wb')
    f.write(results[r])
    f.close()
    im2 = PILImage.open(targetfilename)  # 312 * 445
    # print(im2.size)
    if im2.size != (312,445):
        print(im2.size)
        print('CARD SIZE WARNING!')
    custom_offset = 15
    im3 = PILImage.new("RGB", (312 + custom_offset * 2, 445 + custom_offset * 2), "black")
    im3.paste(im2, (custom_offset, custom_offset))
    tempname = "/home/hel/deckerdata/"+cardnamelist[r]+".temp.png"
    im3.save(tempname, 'PNG')
    im = Image(tempname, 6.3 * cm, 8.8 * cm, hAlign='CENTER')


    for i in cardnumberslist[r]:
        Story.append(im)
        Story.append(pb)



doc.build(Story)

# DUMP

# for x in range(0, 100):
# url = urllib.request.urlopen(adress)
# s = url.read()
# f = open('/home/hel/deckerdata/00000001.jpg','wb')
# f.write(s)
# f.close()
# print(x)

# filename = wget.download(adress)
