## OVERVIEW

PAULOWNIA is a python wrapper around [BLAST](http://blast.ncbi.nlm.nih.gov/Blast.cgi), the alignment program [MAFFT](http://mafft.cbrc.jp/alignment/software/) and the the fast neighbor-joining method implemented in [clearcut](http://bioinformatics.hungry.com/clearcut/). The purpose of the script is to efficiently add a new genome to an existing alignment, based on a set of query sequences. 

## USAGE

> python paulownia.py <new_genome / directory_of_genomes> <query_fasta_sequences>

This assumes a single file for the new_genome, or a directory containing only fasta formatted genomes in directory_of_genomes. The query_fasta_sequences are a list of query sequences / genes for which a phylogeny should be built.

Given the query fasta sequences, paulownia generates a new concatenated alignment for each genome, based on the order of the sequences in the query_fasta_sequences file.

If an existing alignment file is specified, the new genome(s) will be added to it; if no existing alignment file is specified, a new alignment is created. In both cases a new tree is generated.

## OPTIONAL ARGUMENTS and their [DEFAULTS]

-h,--help               Displays usage information
-c,--clearcut_exe       The location of the clearcut executable [/usr/bin/clearcut]
-b,--blast_dir          The directory of the blast+ program suite [/usr/bin/]
-a,--alignment_file     The previous alignment to which the new genomes(s) should be added. [paulownia/previous.aln]
-o,--out_tree           The location where the newly generated tree should be output. [paulownia/new_paulownia.tre]
-m,--mafft_exe          The location of the MAFFT executable [/usr/bin/mafft]
-t,--tmp_dir            The location of created temporary files [/tmp/]
-p,--percent_id_cutoff  The percent identity that a query sequence must exist at in a genome for it to be considered present and used in the alignment [90]
-n,--number_of_threads  The number of threads to use in the creation of the new tree [1]

## EXAMPLE with *Salmonella enterica*
584 *Salmonella enterica* genomes are present in the paulownia/Data/ folder.
330 core genes were previously identified, however, they were not universally present in all genomes.

> for i in *.aln; do if [ $(grep -c '>' $i) = 584 ]; then cp $i ~/workspace/core_tree/universal/; fi done

286 genes were determined to be universally present, which were used for subsequent tree building `paulownia/data/query.fasta`. The alignment of these genes for the 584 genomes is found in `palownia/data/universal_combined.aln`.

To add one of the test genomes in `paulownia/data/salmonella_fasta_files/`:





