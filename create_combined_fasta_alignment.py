#!/usr/env python

#from subprocess import call
import argparse
import os

"""Gathers all aligned fasta files for single genes to create a concatenated \
    alignment file"""

parser = argparse.ArgumentParser()
parser.add_argument("aln_dir", help="The directory where the \
    single gene alignment files are stored")

args = parser.parse_args()
print(args.aln_dir)

genome_names = {}

for file in os.listdir(args.aln_dir):
    if file.endswith(".aln"):
        print(file)
        in_fh = open(args.aln_dir + file, 'r')

        current_name = ""
        for line in in_fh:
            line = line.strip()
            if line[:1] is ">":
                current_name = line[2:]
                genome_names.setdefault(current_name, "")
            else:
                genome_names[current_name] += line

out_fh = open("testout", 'w')

for key, value in genome_names.iteritems():
    out_fh.write('>' + key + "\n" + value + "\n")
