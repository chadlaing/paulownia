#!/usr/bin/env python

import warnings
import argparse
import os
from subprocess import call
import shutil

"""Runs blast based on the 286 query genes, creates a concatenated alignment \
    for the new genome, adds to the existing universal alignment using MAFFT \
    and launches clearcut to generate a new tree"""

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("new_data", help="Location of the new genome \
    fasta file(s). Can be a file or directory. If directory, assumes \
    only fasta files inside, with consistently labelled headers.")
parser.add_argument("query", help="The input query genes used for \
    construction of the phylogeny")
parser.add_argument("-c", "--clearcut_exe", help="The location of the \
    clearcut fast-nj executable", default="/usr/bin/clearcut")
parser.add_argument("-b", "--blast_dir", help="The location of the blast \
    program directory", default="/usr/bin/")
parser.add_argument("-a", "--alignment_file", help="The alignment file of all \
    currently aligned genomes",
    default=SCRIPT_DIRECTORY + "/data/universal_combined.aln")
parser.add_argument("-o", "--out_tree", help="The new tree based on all \
    previous genomes and the newly added one",
    default=SCRIPT_DIRECTORY+ "/data/universal_combined.tre")
parser.add_argument("-m", "--mafft_exe", help="The location of the MAFFT \
    executable", default="/usr/bin/mafft")
parser.add_argument("-t", "--tmp_dir", help="Location of temporary file \
    construction.", default="/tmp/")
parser.add_argument("-n", "--number_query_genes", help="The total number of \
    query genes to expect.", default=286)
parser.add_argument("-p", "--percent_id_cutoff", help="The minimum percent \
    identity that a blast hit must have to be considered 'present'",
    default=90)
args = parser.parse_args()


def create_blast_query_file():
    "If new_data is a directory, combine all the files into a query file for \
    blast. If not, use the supplied file directly."

    if os.path.isdir(args.new_data):
        blast_query_file = args.tmp_dir + 'blast_query.fasta'
        all_files = [f for f in os.listdir(args.new_data)
            if os.path.isfile(os.path.join(args.new_data,f))]
        out_FH = open(blast_query_file, 'a')

        for f in all_files:
            out_FH.write(f.read())

            #ensure each fasta sequence starts on a new line
            out_FH.write("\n")
        return blast_query_file
    else:
        return args.new_data



def run_blast(new_file):
    "Makes a new blast database based on the input genome. Runs blast against \
        this genome using the core query genes as input."
    db_name = args.tmp_dir + "new_genome"
    call([args.blast_dir + "makeblastdb",  "-dbtype",  "nucl", "-in",
          new_file, "-title", "new_genome", "-out",
          db_name])

    blast_output = args.tmp_dir + "new_genome_blast.out"
    call([args.blast_dir + "blastn", "-db", db_name,
          "-query", args.query,
          "-outfmt", '6 " qseqid qlen sseqid length pident sseq "', "-out",
          blast_output, "-max_target_seqs", "1"])
    return (blast_output)


def parse_blast_results(blast_out_file):
    "The blast results are output in the same order as the input query string.\
        We check to ensure that all the queries are present in the result at a\
        total percent identity >= ID. If everything passes, we create a \
        temporary file to be used as an alignment against the current \
        universal alignment"
    in_FH = open(blast_out_file, 'r')

    alignment_string = ""
    total_query = 0
    name = None
    temp_file_name = None
    genome_names = {}

    for line in in_FH:
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
        name = columns[2]

        if total_percent_id >= args.percent_id_cutoff:
            alignment_string += columns[5]
            total_query += 1
            genome_names[genome_name] = 1

    if total_query == args.number_query_genes:
        temp_file_name =  args.tmp_dir + "temp.aln"
        aln_FH = open(temp_file_name, 'w')
        aln_FH.write(">" + name + "\n" + alignment_string + "\n")
    else:
        print('Only ' + str(total_query) + ' genes present in the genome '\
            + str(name) + '. Expected '  + str(args.number_query_genes))
        raise SystemExit(0)

    return temp_file_name


def create_new_alignment(temp_concat):
    "Based on the current universal alignment, add the new genome to it."
    temp_new_aln = args.tmp_dir + "temp_universal.aln"
    aln_out_FH = open(temp_new_aln,"w")

    call([args.mafft_exe, "--thread", "3", "--add", temp_concat,
          args.alignment_file],stdout=aln_out_FH)
    return temp_new_aln


def replace_old_file(old_file,new_file):
    "Given a new file, check that the file size of the new file \
    is greater than the old (indicating successful addition of information). \
    Otherwise keep the original file and print a warning. Creates a backup \
    version of the file (.bak) for posterity."

    print("Old file: " + old_file)
    print("New file: " + new_file)

    old_file_stat = os.stat(old_file)
    old_size = old_file_stat.st_size

    new_file_stat = os.stat(new_file)
    new_size = new_file_stat.st_size

    if new_size > old_size:
        print("Replacing old file with one containing new data.")
        shutil.copyfile(old_file,old_file + ".bak")
        shutil.copyfile(new_file,old_file)
    else:
        warnings.warn("The newly generated file has a problem. \
            Reverting to old file")


def create_new_tree(new_aln):
    "Runs clearcut on the new alignment. Return the filename."
    temp_new_tree = args.tmp_dir + "temp_new.tre"
    call([args.clearcut_exe,"--verbose", "--alignment","--DNA",
            "--in=" + new_aln, "--out=" + temp_new_tree])
    return(temp_new_tree)


#start of program execution
blast_file = run_blast()
new_concat = parse_blast_results(blast_file)
new_aln = create_new_alignment(new_concat)
new_tree = create_new_tree(new_aln)
#replace_old_file(args.alignment_file,new_aln)
#replace_old_file(args.out_tree,new_tree)

