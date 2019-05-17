#!/usr/bin/env python
import argparse
import sys




parser = argparse.ArgumentParser()
parser.add_argument("-user", "-u", help="Your email account for Transkribus")
parser.add_argument("-password", "-p", help="Your password for Transkribus")
parser.add_argument("-colId", "-c", help="The collection ID you wan to modify")
parser.add_argument("-docId", "-d", help="The document id you want to modify")
args = parser.parse_args()
print("Hello " + args.user)
print("your password is :", args.password)

if not args.colId and not args.docId:
    print("you need to specify a collection and a document.")
    exit(0)