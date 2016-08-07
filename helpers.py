from subprocess import call,check_call
import os
import platform
import re
import tempfile
import sys

ENVIRON = os.environ
if platform.system() != 'Windows':
    ENVIRON['PATH'] += ':/usr/local/bin'

DIGRAPH_START = re.compile('.*(digraph([ \t\n\r]+[a-zA-Z\200-\377_][a-zA-Z\200-\3770-9_]*[ \t\n\r]*{|[ \t\n\r]*{).*)', re.DOTALL | re.IGNORECASE)

def surroundingGraphviz(data, cursor):
    '''
    Find graphviz code in source surrounding the cursor.
    '''
    data_before = data[0:cursor]
    data_after = data[cursor:]

    # find code before selector
    code_before_match = DIGRAPH_START.match(data_before)
    if not code_before_match:
        return None
    code_before = code_before_match.group(1)
    unopened_braces = len(code_before.split('{')) - len(code_before.split('}'))

    # cursor must be in the middle of the graphviz code
    if unopened_braces <= 0:
        return None

    # find code after selector
    code_after_match = re.compile('(' + ('.*\\}' * unopened_braces) + ').*', re.DOTALL).match(data_after)
    if not code_after_match:
        return None
    code_after = code_after_match.group(1)

    # done!
    code = code_before + code_after
    return code

def has_dot_installed():
    if check_call(['dot','-?'], env=ENVIRON)!=0:
        raise ValueError("Graphviz is not installed, please add it to your path and restart sublime")

def graphvizPDF(code):
    '''
    Convert graphviz code to a PDF.
    '''
    tmp_folder_path = tempfile.gettempdir()
    grapviz_fname = os.path.join(tmp_folder_path,'sublime_text_graphviz_temp.viz')
    pdf_fname = os.path.join(tmp_folder_path,'sublime_text_graphviz_temp.pdf')
    
    # check if graphviz installed
    has_dot_installed()

    # temporary graphviz file
    grapviz = open(grapviz_fname,'w+b')
    grapviz.write(code.encode('utf-8'))
    grapviz.close()

    print(grapviz_fname)

    # compile pdf
    # 
    print(">>>> COMPILING PDF")
    succeeded = check_call(['dot', grapviz_fname, '-Tpdf', '-o', pdf_fname], env=ENVIRON)
    print("DOTCALL EXIT CODE:",succeeded)
    print("<<<< COMPILING PDF")

    return pdf_fname, tmp_folder_path
