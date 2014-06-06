#!/usr/bin/env python

import warnings
import argparse
import os
from subprocess import call
import shutil
from collections import defaultdict

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
parser.add_argument("-r","--number_of_threads", help="The number of threads \
    to use in the alignment and tree building processes", default="1")
args = parser.parse_args()


def create_blast_data_file(new_data):
    "If new_data is a directory, combine all the files into a file for \
    blast. If not, use the supplied file directly."

    if os.path.isdir(new_data):
        print("Using all files in " + new_data)
        blast_data_file = (os.path.normpath(args.tmp_dir) + os.sep 
            + 'blast_data.fasta')

        all_files = os.listdir(new_data)

        out_FH = open(blast_data_file, 'w')

        for f in all_files:
            full_file = os.path.normpath(new_data) + os.sep + f
            print("File: " + full_file)
            in_FH = open(full_file,'r')
            out_FH.write(in_FH.read())

            #ensure each fasta sequence starts on a new line
            out_FH.write("\n")
        return blast_data_file
    else:
        print("Using the file " + new_data)
        return args.new_data



def run_blast(new_file):
    "Makes a new blast database based on the input genome(s). Runs blast \
    using the core query genes as 'query sequences'."

    db_name = os.path.normpath(args.tmp_dir) + os.sep + "new_genome"
    call([args.blast_dir + "makeblastdb",  "-dbtype",  "nucl", "-in",
          new_file, "-title", "new_genome", "-out",
          db_name])

    blast_output = (os.path.normpath(args.tmp_dir) + os.sep 
        + "new_genome_blast.out")
    call([args.blast_dir + "blastn", "-db", db_name,
          "-query", args.query,
          "-outfmt", '6 " qseqid qlen sseqid length pident sseq "', "-out",
          blast_output, "-max_target_seqs", "1000"])
    return (blast_output)


def parse_blast_results(blast_out_file):
    "The blast results are output in the same order as the input query string.\
        We check to ensure that all the queries are present in the result at a\
        total percent identity >= ID. If everything passes, we create a \
        temporary file to be used as an alignment against the current \
        universal alignment"
    in_FH = open(blast_out_file, 'r')

    
    name = None
    temp_file_name = None
    genome_hits = {}
    genome_concat = defaultdict(str)
    genome_counts = defaultdict(int)
    prev_query = None

    for line in in_FH:
        clean = line.strip()
        columns = clean.split()
        
        curr_query = columns[0]
        curr_hit = columns[2]

        #check for a hit that is already present
        #we only want the top hit of each query sequence
        if (curr_query,curr_hit) in genome_hits:
            continue
        else:
            genome_hits[(curr_query,curr_hit)] = 1


        #get the percent id based on the total length of the query
        total_percent_id = float(columns[3])\
                         * float(columns[4])\
                         / float(columns[1])    

        if total_percent_id >= args.percent_id_cutoff:
            genome_concat[curr_hit] += columns[5]
            genome_counts[curr_hit] += 1

    #check that all new genomes have a hit for all query sequences
    #if they don't, emit warning and remove from further analyses
    temp_file_name =  os.path.normpath(args.tmp_dir) + os.sep + "temp.aln"
    aln_FH = open(temp_file_name, 'w')
    for key, value in genome_counts.iteritems():
        if value == args.number_query_genes:            
            aln_FH.write(">" + key + "\n" + genome_concat[value] + "\n")
        else:
            print('Only ' + str(value) + ' genes present in the genome '
                + str(key) + '. Expected '  + str(args.number_query_genes)
                + " removing " + str(key) + " from alignment")
    return temp_file_name


def create_new_alignment(temp_concat):
    "Based on the current universal alignment, add the new genome to it. \
        If there is no previous alignment, create one based on the provided \
        genomes"
    temp_new_aln = (os.path.normpath(args.tmp_dir) + os.sep
        + "temp_universal.aln")
    aln_out_FH = open(temp_new_aln,"w")

    if os.path.isfile(args.alignment_file):
        call([args.mafft_exe, "--thread", args.number_of_threads,
             "--add", temp_concat, args.alignment_file],stdout=aln_out_FH)
    else:
        warnings.warn("No existing alignment file, creating new alignment")
        call([args.mafft_exe, "--thread", args.number_of_threads,
            temp_concat],stdout=aln_out_FH)
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
    temp_new_tree = os.path.normpath(args.tmp_dir) + os.sep + "temp_new.tre"
    call([args.clearcut_exe,"--verbose", "--alignment","--DNA",
            "--in=" + new_aln, "--out=" + temp_new_tree])
    return(temp_new_tree)


#start of program execution
blast_data = create_blast_data_file(args.new_data)
blast_file = run_blast(blast_data)
new_concat = parse_blast_results(blast_file)
new_aln = create_new_alignment(new_concat)
new_tree = create_new_tree(new_aln)

