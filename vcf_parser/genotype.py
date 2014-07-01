#!/usr/bin/env python
# encoding: utf-8
"""
genotype.py

This is a class with information about genotypecalls that follows the (GATK) .vcf standard.

The indata, that is the genotype call, is allways on the form x/x, so they look like 0/0, 1/2, 1/1 and so on.
The first sign inidcates what we find on the first allele, the second is a separator on the form '/' or '|' and the third indicates what is seen on the second allele.
The alleles are unordered.

Attributes:

    - genotype STRING (Same as in VCF-standard)
    - allele_1 STRING (Base on allele 1)
    - allele_2 STRING (Base on allele 2)
    - nocall BOOL
    - heterozygote BOOL 
    - homo_alt BOOL (If individual is homozygote alternative)
    - homo_ref BOOL (If individual is homozygote reference)
    - has_variant BOOL (If individual is called and not homozygote reference)
    - ref_depth INT
    - alt_depth INT
    - phred_likelihoods LIST with FLOAT
    - depth_of_coverage INT
    - genotype_quality FLOAT
    - phased BOOL

If a variant is present, that is if homo_alt or heterozygote is true, then has_variant is True
    
When dealing with phased data we will see the '|'-delimiter


#TODO:
Should we allow '1/2', '2/2' and so on? This type of call looses it's point when moving from vcf -> bed since bed files only have one kind of variant on each line.
For now we will only allow './.', '0/0', '0/1', '1/1'   

Created by Måns Magnusson on 2014-06-30.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os


class Genotype(object):
    """Holds information about a genotype"""
    def __init__(self, GT='./.', AD='.,.', DP='0', GQ='0', PL=None):
        super(Genotype, self).__init__()        
        # These are the different genotypes:
        self.heterozygote = False
        self.homo_alt = False
        self.homo_ref = False
        self.has_variant = False
        self.genotyped = False
        self.phased = False
        if '|' in GT:
            self.phased = True
        
        if len(GT) < 3: #This is the case when only one allele is present(eg. X-chromosome) and presented like '0' or '1'.
            self.allele_1 = GT
            self.allele_2 = '.'
        else:
            self.allele_1 = GT[0]
            self.allele_2 = GT[-1]
        
        self.genotype = self.allele_1 +'/'+ self.allele_2 # The genotype should allways be represented on the same form
        
        if self.genotype != './.':
            self.genotyped = True
            #Check allele status
            if self.genotype == '0/0':
                self.homo_ref = True
            elif self.allele_1 == self.allele_2:
                self.homo_alt = True
                self.has_variant = True
            else:
                self.heterozygote = True
                self.has_variant = True
        
        self.ref_depth = AD[0]
        self.alt_depth = AD[-1]
        
        #Genotype info:
        if len(AD) > 2:
            if AD[0].isdigit():
                self.ref_depth = int(AD.split(',')[0])
            if AD[2].isdigit():
                self.alt_depth = int(AD.split(',')[1])
        try:
            self.depth_of_coverage = int(DP)
        except ValueError:
            pass
        try:
            self.genotype_quality = float(GQ)
        except ValueError:
            pass
        self.phred_likelihoods = []
        if PL:
            self.phred_likelihoods = [int(score) for score in PL.split(',')]
        
    def __str__(self):
        """Specifies what will be printed when printing the object."""
        return self.allele_1+'/'+self.allele_2

def main():
    pass


if __name__ == '__main__':
    main()

