from collections import Counter
from xml.dom import minidom
import sys

def print_node_html(root,rid):
    """traverse the entire xml DOM and print out everything with html element tags"""
    #rid=Counter()
    cloud='<span class="entity_type"><i title="abstract" class="fa fa-cloud"></i></span>'
    if root.childNodes:
        
        for node in root.childNodes:
            #node is a tag with attribute
            if node.nodeType == node.ELEMENT_NODE:
                rid[id]+=1
                cid=node.attributes['ID'].value
                #print node
                print '<div id="referent_'+str(rid[id]) +"""" onmouseover="highlight_group('"""+ cid + """')" onmouseout="unhighlight_group('""" +   cid   + """')" class="referent" group=\"""" + cid +'">' + cloud    
            text=node.nodeValue

            #node is plain text
            if text:
                print text.strip()

            print_node_html(node,rid)
            if node.nodeType == node.ELEMENT_NODE:
                #cid=node.attributes['ID'].value
                print "</div>"


#usage of print_node_html
header="""<html>
<head>
	<link rel="stylesheet" href="./css/renner.css" type="text/css" charset="utf-8"/>
	<link rel="stylesheet" href="./css/font-awesome-4.2.0/css/font-awesome.min.css"/>
</head>
<body>
<script src="./script/jquery-1.11.3.min.js"></script>
<script src="./script/chroma.min.js"></script>
<script src="./script/renner.js"></script>

"""

footer="""
</body>
</html>"""



#header boilerplate
print header

#parse and print the body of html
xmlfile=sys.argv[1]
xmldoc = minidom.parse(xmlfile)
root = xmldoc.documentElement
rootn=root.childNodes[1]
rid=Counter()
print_node_html(rootn,rid)

#print closing tags
print footer