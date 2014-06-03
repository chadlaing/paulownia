#!/usr/bin/env python

import argparse
import os
from subprocess import call
import shutil


"""Runs blast based on the 286 query genes, creates a concatenated alignment \
    for the new genome and launches clearcut to generate a new tree"""

parser = argparse.ArgumentParser()
parser.add_argument("new_genome", help="Location of the new genome \
    fasta file")
parser.add_argument("query", help="The input query genes used for \
    construction of the phylogeny")
parser.add_argument("-c", "--clearcut_exe", help="The location of the \
    clearcut fast-nj executable", default="/usr/bin/clearcut")
parser.add_argument("-b", "--blast_dir", help="The location of the blast \
    program program", default="/usr/bin/")
parser.add_argument("-a", "--alignment_file", help="The alignment file of all \
    currently aligned genomes", default="./data/universal_combined.aln")
parser.add_argument("-o", "--out_tree", help="The tree based on all genomes",
                    default="./data/universal_combined.tre")
parser.add_argument("-z", "--clustal_exe", help="The location of the clustal \
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
          args.new_genome, "-title", "new_genome", "-out",
          args.tmp_dir + "new_genome"])

    call([args.blast_dir + "blastn", "-db", args.tmp_dir + "new_genome",
          "-query", args.query,
          "-outfmt", '6 " qseqid qlen sseqid length pident sseq "', "-out",
          args.tmp_dir + "new_genome_blast.out", "-max_target_seqs", "1"])
    return (args.tmp_dir + "new_genome_blast.out")


def parse_blast_results(blast_out_file):
    "The blast results are output in the same order as the input query string.\
        We check to ensure that all the queries are present in the result at a\
        total percent identity >= 90. If everything passes, we create a \
        temporary file to be used as an alignment against the current \
        universal alignment"
    in_fh = open(blast_out_file, 'r')

    alignment_string = ""
    total_query = 0
    name = None
    temp_file_name = None
    genome_names = {}

    for line in in_fh:
        clean = line.strip()
        columns = clean.split()

        genome_name = columns[0]

        #check for a genome that is already present
        if genome_name in genome_names:
            continue

        #get the percent id based on the total length of the query
        total_percent_id = float(columns[3])\
                         * float(columns[4])\
                         / float(columns[1])
        print(total_percent_id)
        if name is None:
            name = columns[2]

        if total_percent_id >= 90:
            alignment_string += columns[5]
            total_query += 1
            genome_names[genome_name] = 1

    if total_query == args.number_query_genes:
        temp_file_name =  args.tmp_dir + "temp.aln"
        aln_fh = open(temp_file_name, 'w')
        aln_fh.write(">" + name + "\n" + alignment_string + "\n")
    else:
        print('Only ' + str(total_query) + ' genes present in the genome '\
            + str(name) + '. Expected '  + str(args.number_query_genes))
        raise SystemExit(0)

    return temp_file_name


def create_new_alignment(temp_aln):
    "Based on the current universal alignment, add the new genome to it."
    temp_new_aln = args.tmp_dir + "temp_universal.aln"
    call([args.clustal_exe, "--dealign", "-i", temp_aln,
          "-o", temp_new_aln, "--threads", "3",
          "--profile1", args.alignment_file])


def create_temp_all_alignment(new_genome_aln):
    "Takes the concatenated string of universal genes and appends it to the\
        bottom of the universal alignment file for use in Clustal Omega"

    combined_temp_file = args.tmp_dir + "combined_tmp.fasta"
    
    shutil.copyfile(args.alignment_file,combined_temp_file)

    new_aln_fh = open(new_genome_aln, 'r')
    combined_out_fh = open(combined_temp_file, 'a')

    for line in new_aln_fh:
        combined_out_fh.write(line)

    return combined_temp_file


blast_file = run_blast()
new_aln = parse_blast_results(blast_file)
all_tmp_aln = create_temp_all_alignment(new_aln)
create_new_alignment(all_tmp_aln)
