#! /usr/bin/env python

# converts dot files to ipe through fig

import xml.dom.minidom, sys, xml.sax.saxutils, re, tempfile, os


def which(program):
  import os
  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program):
      return program
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return exe_file

  return None

def getText(nodelist):
  rc = ""
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      rc = rc + node.data
  return rc

# from http://code.activestate.com/recipes/303061-remove-whitespace-only-text-nodes-from-an-xml-dom/
def remove_whilespace_nodes(node, unlink=False):
    """Removes all of the whitespace-only text decendants of a DOM node.
    
    When creating a DOM from an XML source, XML parsers are required to
    consider several conditions when deciding whether to include
    whitespace-only text nodes. This function ignores all of those
    conditions and removes all whitespace-only text decendants of the
    specified node. If the unlink flag is specified, the removed text
    nodes are unlinked so that their storage can be reclaimed. If the
    specified node is a whitespace-only text node then it is left
    unmodified."""
    
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whilespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()

dot = which("dot")
if dot == None:
  print """This program relies on graphviz, but seems to be missing. 
  To install it in ubuntu type: sudo apt-get install graphviz"""
  sys.exit(-1)

figtoipe = which("figtoipe")
if figtoipe == None:
  print """This program relies on figtoipe, but seems to be missing. 
  To install it in ubuntu type: sudo apt-get install figtoipe"""
  sys.exit(-1)



# open dot and escape labels

def encode(m):
  line = m.group(0).replace('<', '\\\\verb+<+')
  line = line.replace('>', '\\\\verb+>+')
  line = line.replace('&', '\\\\verb+&+')
  return xml.sax.saxutils.escape(xml.sax.saxutils.escape(line))


if sys.argv[2] == "-":
  in_fd = sys.stdin
else:
  in_fd = open(sys.argv[2])
_, dot_fn = tempfile.mkstemp()
dot_fd = open(dot_fn, 'w')
re_label = re.compile(r'label\s*=\s*"([^"\\]|\\.)*"')
for line in in_fd:
  line = line.lstrip()
  line = re_label.sub(encode, line) 
  print >> dot_fd, line
dot_fd.close()
_, fig_fn = tempfile.mkstemp()
os.system("dot -Tfig %s > %s" % (dot_fn, fig_fn)) 
#print >> sys.stderr, dot_fn
os.unlink(dot_fn)
_, ipe_fn = tempfile.mkstemp()
os.system("figtoipe %s %s" % (fig_fn, ipe_fn)) 
os.unlink(fig_fn)
#print >> sys.stderr, fig_fn
  

# open template and generated ipe
template = xml.dom.minidom.parse(sys.argv[1])
dot      = xml.dom.minidom.parse(ipe_fn)
print >> sys.stderr, ipe_fn
#os.unlink(ipe_fn)


# get page node for merging
temp_page = template.getElementsByTagName("page")[0]
dot_page = dot.getElementsByTagName("page")[0]
remove_whilespace_nodes(dot_page, True)

# remove white background box
dot_page.removeChild(dot_page.childNodes[0])

# merge children from dot to template
children = []
child_it = dot_page.childNodes.__iter__()
pos = 0
for elem in child_it:
  accept_node = True 
  # disable transmformable in text
  if elem.nodeName == "text":
    elem.setAttribute("transformable", "no")

  # remove arrow path and merge with edge 
  if elem.nodeName == "path":
    elem.setAttribute("stroke", "black")
    elem.setAttribute("pen", "normal")
    elem.setAttribute("arrow", "normal/tiny")
    count = getText(elem.childNodes).count("l")
    if count > 2 and dot_page.childNodes[pos+1].nodeName == "path":
      arrow = child_it.next()
      pos += 1
      edge_pos  = getText(elem.childNodes).strip().split('\n')
      arrow_pos = getText(arrow.childNodes).strip().split('\n')
      elem.firstChild.data = "\n".join(['', edge_pos[0], arrow_pos[1], ''])


  if accept_node:
    children.append(elem)
  pos += 1

for elem in children:
  temp_page.appendChild(elem)

print template.toxml()

