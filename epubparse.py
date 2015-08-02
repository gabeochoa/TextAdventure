#!/usr/bin/python
import epub

book = epub.open_epub('rpo.epub')

for item in book.opf.manifest.values():
    # read the content
    data = book.read_item(item)
    # get chapter 1

print data
import xml.etree.ElementTree as ET
tree = ET.fromstring(data)
print tree.findall('content')

# item = book.get_item('chapter')
# # display the same thing
# print book.read_item(item)

