#!/usr/env python

import argparse
import os

"""Gathers all aligned fasta files for single genes to create a concatenated \
    alignment file"""

parser = argparse.ArgumentParser()
parser.add_argument("aln_dir", help="The directory where the \
    single gene alignment files are stored")
parser.add_argument("out_dir", help="Output directory for combined aln file")

args = parser.parse_args()
print(args.aln_dir)

genome_names = {}

for file in sorted(os.listdir(args.aln_dir)):
    if file.endswith(".aln"):
        in_fh = open(args.aln_dir + file, 'r')
        print(file)

        current_name = "default"
        for line in in_fh:
            line = line.strip()
            if line[:1] is ">":
                current_name = line[1:]
                genome_names.setdefault(current_name, "")
            else:
                genome_names[current_name] += line

out_fh = open(args.out_dir, 'w')

for key, value in genome_names.iteritems():
    out_fh.write('>' + key + "\n" + value + "\n")
