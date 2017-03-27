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

doc = SimpleDocTemplate("/home/hel/hello.pdf", pagesize=customsize,
                        rightMargin=0, leftMargin=0,
                        topMargin=0.1 * cm, bottomMargin=0)
Story = []

early_stop_at = 1

decklist = '/home/hel/deckerdata/UR steal hate.cod'

e = xml.etree.ElementTree.parse(decklist).getroot()
cardnamelist = []


childcount = 0

for child in e:
    # print(child.tag, child.attrib)
    if child.tag == 'zone':
        if child.attrib['name'] == 'main':
            # numberofcards = len(child.getchildren())
            # print('numberofcards',numberofcards)
            for subchild in child:
                childcount += 1
                if childcount > early_stop_at:
                    continue

                print(subchild.tag, subchild.attrib)
                for i in range(0,int(subchild.attrib['number'])):
                    cardnamelist.append(subchild.attrib['name'])

QUERIES = []
count = len(cardnamelist)

for c in range(0, count):
    query_adress = "http://magiccards.info/query?q=" + cardnamelist[c].replace(' ', '+') + "&v=card&s=cname"
    QUERIES.append(query_adress)

print (QUERIES)

def get_content(url):

    url = urllib.request.urlopen(url)
    s = url.read()
    content = s.decode('utf-8')
    targetpattern = 'http://magiccards.info/scans/'
    pos1 = str.find(content, targetpattern)
    pos2 = str.find(content, '"', pos1)
    img_adress = content[pos1:pos2]
    print("downloading :",img_adress)

    img = urllib.request.urlopen(img_adress)
    s = img.read()

    return s

pool = multiprocessing.Pool(processes=256)  # play with ``processes`` for best results
results = pool.map(get_content, QUERIES)  # This line blocks, look at map_async
# for non-blocking map() call
pool.close()  # the process pool no longer accepts new tasks
pool.join()  # join the processes: this blocks until all URLs are processed

pb = PageBreak()

resultlength = len(results)

for r in range(0,resultlength):

    targetfilename = '/home/hel/deckerdata/'+cardnamelist[r]+'.jpg'
    f = open(targetfilename, 'wb')
    f.write(results[r])
    f.close()
    im2 = PILImage.open(targetfilename)  # 312 * 445
    # print(im2.size)

    fakeblackwidth = 0

    width, height = im2.size

    im2 = im2.crop((fakeblackwidth,fakeblackwidth,width-fakeblackwidth,height-fakeblackwidth))


    if im2.size != (312, 445):
        print(im2.size)
        print('CARD SIZE WARNING!')
    custom_offset = 15+fakeblackwidth*2


    im3 = PILImage.new("RGB", (312 + custom_offset * 2, 445 + custom_offset * 2), "red")
    im3.paste(im2, (custom_offset, custom_offset))
    tempname = "/home/hel/deckerdata/"+cardnamelist[r]+".temp.png"
    im3.save(tempname, 'PNG')
    im = Image(tempname, 6.3 * cm, 8.8 * cm, hAlign='CENTER')

    Story.append(im)
    print('appending :', tempname)
    Story.append(pb)

doc.build(Story)

