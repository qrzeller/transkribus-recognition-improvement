#!/usr/bin/env python3
import argparse
import sys
from src.controllerTS import controllerTS

parser = argparse.ArgumentParser()
parser.add_argument("--user", "-u", help="Your email account for Transkribus")
parser.add_argument("--password", "-p", help="Your password for Transkribus")
parser.add_argument("--colId", "-c", type=int, help="The collection ID you wan to modify")
parser.add_argument("--docId", "-d", type=int, help="The document id you want to modify")
parser.add_argument("--interline_annotation", "-i", type=str,
                    help="To change the default tag for interline notation, \"footnote\"")
args = parser.parse_args()
print("Hello " + args.user)
print("your password is :", args.password)

if not args.colId or not args.docId:
    print("You need to specify a collection and a document.")
    exit(0)
else:
    print("Your ask to clean the document %d in the collection %d" % (args.docId, args.colId))

global annotation
if args.interline_annotation:
    annotation = args.interline_annotation
else:
    annotation = "footnote"

controllerTS(args.user, args.password, args.colId, args.docId, annotation)
