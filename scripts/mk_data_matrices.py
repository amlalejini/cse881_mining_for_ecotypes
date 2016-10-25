#!/usr/bin/python2

"""
This script will look through specified treatment/reps analysis detail files,
building data matrices.

Matrix Columns:
-- Meta data --
Organism ID
Abundance
Tree Depth

-- Genotype data --
Genome Length
Genome Sequence

instr--a
instr--b
instr--c
instr--d
instr--e
instr--f
instr--g
instr--h
instr--i
instr--j
instr--k
instr--l
instr--m
instr--n
instr--o
instr--p
instr--q
instr--r
instr--s
instr--t
instr--u
instr--v
instr--w
instr--x
instr--y
instr--z

-- Phenotype data --
Is Viable
Gestation Time ()
Fitness
Phenotype Signature: NOT, NAND, AND, ORNOT, OR, ANDNOT, NOT, XOR, EQU
NOT
NAND
AND
ORNOT
OR
ANDNOT
NOR
XOR
EQU
"""

import json, os, subprocess

def main():
    """
    Main Script
    """
    pass

if __name__ == "__main__":
    main()
