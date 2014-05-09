#!/usr/bin/env python

import argparse
#import os
from subprocess import call

"""Runs blast based on the 286 query genes, creates a concatenated alignment \
    for the new genome and launches clearcut to generate a new tree"""

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--clearcut_exe", help="The location of the \
    clearcut fast-nj executable", default="/usr/bin/")
parser.add_argument("-b", "--blast_dir", help="The location of the blast \
    program program", default="/usr/bin/")
parser.add_argument("-o", "--out_tree", help="The new tree, with new genome \
    included", default="new.tre")
parser.add_argument("-n", "--new_genome", help="Location of the new genome \
    fasta file")
parser.add_argument("-t", "--tmp_dir", help="Location of temporary file \
    construction.", default="/tmp/")
args = parser.parse_args()


def run_blast():
    "Makes a new blast database based on the input genome. Runs blast against \
        this genome using the core query genes as input."
    makeblastdb_line = args.blast_dir() + "makeblastdb -dbtype nucl -in " \
        + args.new_genome() + " -title new_genome -o new_genome"
    call(makeblastdb_line)
    return
#    blast_line = args.blast_dir() + "blastn "

run_blast()
