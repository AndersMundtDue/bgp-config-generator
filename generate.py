#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import fnmatch
import sys
import os
import json
from jinja2 import Environment, FileSystemLoader

def render_template(template_filename, templatespath, context):
  TEMPLATE_ENVIRONMENT = Environment(
      autoescape=False,
      loader=FileSystemLoader(templatespath),
      trim_blocks=False)
  return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def loadjson(fname):
  with open(fname) as data_file:
    data = json.load(data_file)
  return data

if __name__=='__main__':
  PATH = os.path.dirname(os.path.abspath(__file__))
  TEMPLATES = os.path.join(PATH, 'templates')
  parser = OptionParser()
  parser.add_option("-T", "--templatepath", dest="templatepath", help="path to search for templates, default to templates", default=TEMPLATES)
  parser.add_option("-t", "--templatename", dest="templatename", help="default template, cisco default is cisco.j2, junos default is juniper-set.j2", default=None)
  parser.add_option("-r", "--router", dest="router", help="router name to match", default="*")
  parser.add_option("-l", "--list", action="store_true", help="list peers found in json input", dest="listpeers", default=False)
  parser.add_option("-p", "--peers", dest="peers", help="peer fnmatch(3) expression", default="*")
  parser.add_option("-i", "--input", dest="source", help="json input", default="peerings.json")
  parser.add_option("-o", "--output", dest="output", help="output file", default="output.cfg")
  parser.add_option("-c", "--cisco", action="store_true", dest="cisco", help="short for -t cisco.j2", default=False)
  parser.add_option("-j", "--juniper", action="store_true", dest="juniper", help="short for -t juniper-set.j2", default=False)
  (options, args) = parser.parse_args()
  peersettings = loadjson(options.source)
  if options.listpeers:
    print("Found the following peers in %s," % options.source)
    for x in list(peersettings.keys()):
      print("\t",x)
    sys.exit(0)
  if options.cisco:
    if options.juniper:
      print("Can't do both cisco and juniper, sorry..")
      sys.exit(0)
    else:
      template="cisco.j2"
  else:
    template="juniper-set.j2"
  if options.templatename:
    template=options.templatename
  print("Generating from %s to %s using %s as template" % (options.source,options.output,template))
  if options.output=='-':
    f=sys.stdout
  else:
    f=open(options.output, 'w')
  for x in list(peersettings.keys()):
    for router in list(peersettings[x]['peerings'].keys()):
      if not fnmatch.fnmatch(router,options.router):
        peersettings[x]['peerings'].pop(router)
    if len(list(peersettings[x]['peerings'].keys()))>=1 and fnmatch.fnmatch(x,options.peers):
      cfg = render_template(template, options.templatepath, peersettings[x])
      f.write(cfg)
      f.write('\n')
