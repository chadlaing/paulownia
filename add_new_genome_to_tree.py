#!/usr/bin/env python

import argparse
import os
from subprocess import call


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
parser.add_argument("-a", "--alignment_file", help="The alignment file of all \
    currently aligned genomes", default="universal_combined.aln")
parser.add_argument("-o", "--out_tree", help="The tree based on all genomes",
                    default="universal_combined.tre")
parser.add_argument("-c", "--clustal_exe", help="The location of the clustal \
    omega executable", default="/usr/bin/clustalo")
parser.add_argument("-t", "--tmp_dir", help="Location of temporary file \
    construction.", default="/tmp/")
parser.add_argument("-n", "--number_query_genes", help="The total number of \
    query genes to expect.", default=286)
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


def parse_blast_results():
    "The blast results are output in the same order as the input query string.\
        We check to ensure that all the queries are present in the result at a\
        total percent identity >= 90. If everything passes, we create a \
        temporary file to be used as an alignment against the current \
        universal alignment"
    in_fh = open(args.out_file, 'r')

    alignment_string = None
    total_query = 0
    name = None
    for line in in_fh:
        columns = line.strip.split()

        #get the percent id based on the total length of the query
        total_percent_id = columns[3] * columns[4] / columns[1]

        if name is None:
            name = columns[0]

        if total_percent_id >= 90:
            total_query += 1
            alignment_string += columns[5]

    if total_query == args.number_query_genes:
        temp_file_name = "temp.aln"
        aln_fh = open(args.tmp_dir + temp_file_name, 'r')
        aln_fh.write(">" + name + "\n" + alignment_string + "\n")

    return temp_file_name


def create_new_alignment(temp_aln):
    "Based on the current universal alignment, add the new genome to it."


run_blast()
create_new_alignment(
    parse_blast_results())
