"""Translate Yahoo Pipe into Python

   Converts a JSON representation of a pipe into a Python function using generators to build the pipeline
   
   (initial proof of concept)
"""

try:
    import json
except ImportError:
    import simplejson as json
   
from topsort import topological_sort

#for run_pipe
from pipefetch import *
from pipefilter import *
from pipeoutput import *

def parse_pipe(json_pipe):
    """Parse pipe JSON into internal structures
    """
    pipe_def = json.loads(json_pipe)
    
    modules = {}
    graph = {}
    for module in pipe_def['modules']:
        modules[module['id']] = module
        graph[module['id']] = []

    #todo assumes 1 to 1 for now
    for wire in pipe_def['wires']:
        graph[wire['src']['moduleid']].append(wire['tgt']['moduleid'])
        
    return modules, graph

def run_pipe(modules, graph):
    """Convert a pipe into an executable Python pipeline
    """
    module_sequence = topological_sort(graph)
    
    steps = {}
    prev_module = None
    for module_id in module_sequence:
        module = modules[module_id]
        
        module_ref = eval("pipe_" + module['type'])
        
        args = []
        if prev_module:
            args.append(steps[prev_module])
        else:
            args.append(None)
        
        kwargs = {'conf':module['conf']}
       
        
        steps[module_id] = module_ref(*args, **kwargs)

        prev_module = module_id
    
    return steps[prev_module]
    
    
def write_pipe(modules, graph):
    """Convert a pipe into Python script
    """
    pipe = ("""#Pipe generated by pipe2python.py\n"""
            """def pipe_x():\n"""
            """    #demo\n"""
            """\n"""
           )

    module_sequence = topological_sort(graph)
    
    prev_module = None
    for module_id in module_sequence:
        module = modules[module_id]
        pipe += "    %(module_id)s = pipe_%(module_type)s(%(input_module)s, conf=%(conf)s)\n" % {'module_id':module_id, 'module_type':module['type'], 'input_module':prev_module or 'None', 'conf':module['conf']}
        prev_module = module_id
    
    pipe += "    return _OUTPUT\n"
        
    return pipe

def parse_and_write_pipe(json_pipe):
    modules, graph = parse_pipe(json_pipe)
    pw = write_pipe(modules, graph)
    print pw   #TODO print ok?

def parse_and_run_pipe(json_pipe):
    modules, graph = parse_pipe(json_pipe)
    pe = run_pipe(modules, graph)
    for i in pe:
        print i   #TODO print ok?

if __name__ == '__main__':
    pjson = """{"layout":[{"id":"_OUTPUT","xy":[230,366]},{"id":"sw-90","xy":[25,25]},{"id":"sw-102","xy":[77,148]}],
     "modules":[
       {"type":"output","id":"_OUTPUT","conf":[]},
       {"type":"fetch","id":"sw-90","conf":{"URL":{"value":"test/feed.xml","type":"url"}}},
       {"type":"filter","id":"sw-102","conf":{
         "MODE":{"type":"text","value":"permit"},
         "COMBINE":{"type":"text","value":"and"},
         "RULE":[{"field":{"value":"title","type":"text"},"op":{"type":"text","value":"contains"},"value":{"value":"By","type":"text"}}]
         }
         }
     ],
       
     "terminaldata":[
       {"id":"_OUTPUT","moduleid":"sw-90",
         "data":{"_type":"item","_attr":{"link":{"_type":"url","_count":"7"},"y:id":{"_type":"","_attr":{"value":{"_type":"url","_count":"6"},"permalink":{"_type":"text","_count":"7"}}},"slash:comments":{"_type":"number","_count":"7"},"wfw:commentRss":{"_type":"url","_count":"7"},"description":{"_type":"text","_count":"4"},"comments":{"_type":"url","_count":"7"},"dc:creator":{"_type":"text","_count":"7"},"content:encoded":{"_type":"text","_count":"7"},"y:title":{"_type":"text","_count":"7"},"title":{"_type":"text","_count":"7"},"category":{"_type":"text","_count":"7"},"guid":{"_type":"","_attr":{"isPermaLink":{"_type":"text","_count":"7"},"content":{"_type":"url","_count":"6"}}},"pubDate":{"_type":"datetime","_count":"7"},"y:published":{"_type":"datetime","_attr":{"hour":{"_type":"number","_count":"7"},"timezone":{"_type":"text","_count":"7"},"second":{"_type":"number","_count":"7"},"month":{"_type":"number","_count":"7"},"minute":{"_type":"number","_count":"7"},"utime":{"_type":"number","_count":"7"},"day_of_week":{"_type":"number","_count":"7"},"day":{"_type":"number","_count":"7"},"year":{"_type":"number","_count":"7"}}}}}},
       {"id":"_OUTPUT","moduleid":"sw-102",
         "data":{"_type":"item","_attr":{"link":{"_type":"url","_count":"4"},"y:id":{"_type":"","_attr":{"value":{"_type":"url","_count":"3"},"permalink":{"_type":"text","_count":"4"}}},"slash:comments":{"_type":"number","_count":"4"},"wfw:commentRss":{"_type":"url","_count":"4"},"description":{"_type":"text","_count":"4"},"comments":{"_type":"url","_count":"4"},"dc:creator":{"_type":"text","_count":"4"},"content:encoded":{"_type":"text","_count":"4"},"y:title":{"_type":"text","_count":"4"},"title":{"_type":"text","_count":"4"},"category":{"_type":"text","_count":"4"},"guid":{"_type":"","_attr":{"isPermaLink":{"_type":"text","_count":"4"},"content":{"_type":"url","_count":"3"}}},"pubDate":{"_type":"datetime","_count":"4"},"y:published":{"_type":"datetime","_attr":{"hour":{"_type":"number","_count":"4"},"timezone":{"_type":"text","_count":"4"},"second":{"_type":"number","_count":"4"},"month":{"_type":"number","_count":"4"},"minute":{"_type":"number","_count":"4"},"utime":{"_type":"number","_count":"4"},"day_of_week":{"_type":"number","_count":"4"},"day":{"_type":"number","_count":"4"},"year":{"_type":"number","_count":"4"}}}}}}],
         
     "wires":[
       {"id":"_w1","src":{"id":"_OUTPUT","moduleid":"sw-90"},"tgt":{"id":"_INPUT","moduleid":"sw-102"}},
       {"id":"_w3","src":{"id":"_OUTPUT","moduleid":"sw-102"},"tgt":{"id":"_INPUT","moduleid":"_OUTPUT"}}]}"""
    

    parse_and_write_pipe(pjson)
    parse_and_run_pipe(pjson)