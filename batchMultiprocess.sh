#!/bin/bash
cd evolution
for ((count=0; count<500; count++))
do
    python batchrun.py --runs=100 
done
exit 0
