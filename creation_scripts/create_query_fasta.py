#!/usr/bin/env python

import argparse
import os

"""Gathers a single fasta sequence from each alignment file to use as a \
    query in the BLAST searches"""

parser = argparse.ArgumentParser()
parser.add_argument("aln_dir", help="The directory where the \
    single gene alignment files are stored")
parser.add_argument("out_file", help="Output file for query fasta")

args = parser.parse_args()
print(args.aln_dir)

out_fh = open(args.out_file, 'w')

for file in sorted(os.listdir(args.aln_dir)):
    if file.endswith(".aln"):
        in_fh = open(args.aln_dir + file, 'r')
        print(file)

        counter = 0
        for line in in_fh:
            line = line.strip()
            if line[:1] is ">":
                counter += 1
                line = '>' + file[0:file.find('.aln')]

            if counter > 1:
                break

            out_fh.write(line + "\n")
