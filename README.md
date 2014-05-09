This package does the following:
Before: 
330 core genes were identified, however, they were not universally present
After: for i in *.aln; do if [ $(grep -c '>' $i) = 584 ]; then cp $i ~/workspace/core_tree/universal/; fi done
286 genes universally present, which will be used for tree building.

An alignment using MAFFT of all these genes was created
A single alignment in FASTA format was created from these single alignment files, based on sorted gene name
A single query file of the first element of the aligned file for each of the 330 core genes was created
This combined file is the query file used to search the new genome using BLAST+


-the top hit above threshold is kept for each "first sequence", as the allele for new genome
-a temporary file containing the previous alignment for each genome and the new allele is created and an alignment run
-this new alignment file becomes the "NEW" version, which will be used for subsequent strain addition
-the "new" alignments are combined in asciibetical order and added to the combined fasta alignment file, which contains all previous genomes and the concatenated alignments
-a new tree is built using fast_method


