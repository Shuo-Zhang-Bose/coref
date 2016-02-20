from xml.dom import minidom
import sys
from itertools import groupby
from operator import itemgetter
import re

def printToFile(content,filename):
    firstname=filename.split(".")[0]
    newname=firstname+"_gold.response"
    f = open(newname, 'a')
    f.write(content)
    f.close()


def groupPos(data):
    t=[]
    for k, g in groupby(enumerate(data), lambda (i, x): i-x):
        t.append(map(itemgetter(1), g))
    return t

def traverse_node(root):
    """traverse the entire xml file recursively and output all tokens in order into a list"""
    output=[]
    if root.childNodes:
        for node in root.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                cid=node.attributes['ID'].value
                # Make IDs like 'wsj_1234.sgm-E1' be strictly numeric by collapsing them into just the numbers
                # also there are IDs like "wsj_2325-E3", so use * here
                cid=re.sub(r'wsj_([0-9]+).*-[A-Z]([0-9])',r'\1\2',cid)
                output.append("("+cid)
            text=node.nodeValue
            if text:
                tokens=text.strip().split(" ")
                for tok in tokens:
                    if tok!=" " and tok!="":
                        output.append(tok)
            output.extend(traverse_node(node)[:])
            if node.nodeType == node.ELEMENT_NODE:
                output.append(cid+")")
    return output
    
def generateLabels(positions,mode,nlist):
    """given a list of positions (starts or ends) of all the tags of form '(123' or '123)', and mode=1 for starts, else for ends, return a list of labels to be inserted for all tokens the same length of nlist, the print out from xml"""
    posp=groupPos(positions)
    posp_item=[]
    for poss in posp:
        if len(poss)==1:
            posp_item.append(nlist[poss[0]])
        elif len(poss)>1:
            item="".join(nlist[i] for i in poss)
            posp_item.append(item)
    starts_tok=[]
    for pos in posp:
        if mode==1:
            ins=pos[-1]+1
        else:
            ins=pos[0]-1
        starts_tok.append(ins)    
    newlist=[[starts_tok[i],posp_item[i]] for i in range(len(posp))]
    stags=['_']*len(nlist)
    for i in newlist:
        stags[i[0]]=i[1]    
    return stags


def modify_labels(start,end):
    """turn end into a list of numbers and turn start into a list of \(\d and check if \
    any number of start is in end, for example, (3 and 1)3) will turn into (3 and 3)1) so that it is merged in the right order"""
    nums_b=end.split(')')
    num_b=map(int, nums_b[:-1])
    a=re.findall("\(\d+",start)
    aa=re.findall("\d+\)",end)
    #print a,aa
    for i in a:
        m=re.search('\d+',i)
        b=int(m.group())
        if b in num_b:
            #print 'found ', b
            a.remove(i)
            a.append(i)
            b_pos=num_b.index(b)
            ins=aa[b_pos]
            del aa[b_pos]
            aa.insert(0,ins)
            break
    
    start_mod=''.join(a)
    #print start_mod
    end_mod=''.join(aa)
    #print end_mod
    return start_mod,end_mod


#merge labels
def mergeLabels(x,y):
    """take a pair of labels (start, end) and output the merged label"""
    if x=="_" and y=="_":
        newlabel="_"
    elif x=="_" and y!="_":
        newlabel=y
    elif x!="_" and y=="_":
        newlabel=x
    else:
        x_mod,y_mod=modify_labels(x,y)
        #print "=========xmod,ymod: ", x_mod,y_mod
        a=x.count("(")
        b=y.count(")")
        x_nums=x_mod.split('(')
        y_nums=y_mod.split(")")

        # (3 4)5) , (3 3)5) , (3(41 41)5)6)
        if a<b:
            if x_nums[-1]==y_nums[0]:
                newlabel="("+y_mod
            else:
                newlabel=x_mod + " " + y_mod
        elif a>b:
            if x_nums[-1]==y_nums[0]:
                newlabel=x_mod+")"
            else:
                newlabel=x_mod + " " + y_mod
        #(3(4 4)5) or (3(4 5)6) or (5 5)
        elif a==b:
            if x_nums[-1]==y_nums[0]:
                if len(x_nums)==1:
                    newlabel=x_mod
                    for g in y_nums[1:]:
                        newlabel=newlabel+g+')'
                else:
                    newlabel=x_mod+')'
            else:
                newlabel=x_mod + " " + y_mod
                
    return newlabel
    



# Main usage
def mainOutput(xmldoc):
    #xmlfile=sys.argv[1]
    #if xmlfile=="-":
    #    xmlfile=sys.stdin
    #xmldoc = minidom.parse(xmlfile)
    root = xmldoc.documentElement
    rootn=root.childNodes[1]
    nlist=traverse_node(rootn)
    outputFormat=[]
    starts=[]
    for i in range(len(nlist)):
        if nlist[i][0]=="(":
            starts.append(i)
    ends=[]
    for i in range(len(nlist)):
        if nlist[i][-1]==")":
            ends.append(i)
    st=generateLabels(starts,1,nlist)
    ed=generateLabels(ends,-1,nlist)

    counter=0
    for i in range(len(nlist)):
        if nlist[i][0]!="(" and nlist[i][-1]!=")":
            merged=mergeLabels(st[i],ed[i])
            #print nlist[i],st[i],ed[i],merged
            tok=str(counter)+"\t"+nlist[i]+"\t"+merged
            outputFormat.append(tok)
            counter+=1
    return outputFormat

#except IndexError:
#    print "Missing argument: this script takes one argument, the xml coref file"