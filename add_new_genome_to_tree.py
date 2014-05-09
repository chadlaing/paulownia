#!/usr/bin/env python

import argparse
#import os
from subprocess import call
#from subprocess import check_output

"""Runs blast based on the 286 query genes, creates a concatenated alignment \
    for the new genome and launches clearcut to generate a new tree"""

parser = argparse.ArgumentParser()
parser.add_argument("new_genome", help="Location of the new genome \
    fasta file")
parser.add_argument("query", help="The input query genes used for \
    construction of the phylogeny")
parser.add_argument("-c", "--clearcut_exe", help="The location of the \
    clearcut fast-nj executable", default="/usr/bin/")
parser.add_argument("-b", "--blast_dir", help="The location of the blast \
    program program", default="/usr/bin/")
parser.add_argument("-o", "--out_tree", help="The new tree, with new genome \
    included", default="new.tre")
parser.add_argument("-t", "--tmp_dir", help="Location of temporary file \
    construction.", default="/tmp/")
args = parser.parse_args()


def run_blast():
    "Makes a new blast database based on the input genome. Runs blast against \
        this genome using the core query genes as input."
    call([args.blast_dir + "makeblastdb",  "-dbtype",  "nucl", "-in",
          args.new_genome, "-title", "new_genome", "-out", "new_genome"])

    call([args.blast_dir + "blastn", "-db", "new_genome", "-query", args.query,
          "-outfmt", '6 " qseqid qlen sseqid length pident sseq "', "-out",
          args.tmp_dir + "new_genome_blast.out", "-max_target_seqs", "1"])
    return


run_blast()
