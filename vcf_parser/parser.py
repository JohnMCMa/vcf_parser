#!/usr/bin/env python
# encoding: utf-8
"""
vcf_parser.py


Parse a vcf file.

Includes a header class for storing information about the headers.
Create variant objects and a dictionary with individuals that have a dictionary with genotypes for each variant.

Thanks to PyVCF for heaader parser and more...:

Copyright (c) 2011-2012, Population Genetics Technologies Ltd, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. Neither the name of the Population Genetics Technologies Ltd nor the names of
its contributors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Copyright (c) 2011 John Dougherty

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



Created by Måns Magnusson on 2013-01-17.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

from __future__ import print_function, unicode_literals

import sys
import os
import gzip
import re
import pkg_resources
import click
import locale
import logging


from codecs import open, getreader


from vcf_parser import (Genotype, HeaderParser)
from vcf_parser.utils import (format_variant, split_variants)

####            Parser:         ####

class VCFParser(object):
    """docstring for VCFParser"""
    def __init__(self, infile=None, fsock=None, split_variants=False):
        super(VCFParser, self).__init__()
        self.logger = logging.getLogger(__name__)
        
        if not (fsock or infile):
            raise IOError('You must provide at least fsock or filename')
        
        if fsock:
            if not infile and hasattr(fsock, 'name'):
                if sys.version_info < (3, 0):
                    self.logger.info("Using codecs to read stdin")
                    sys.stdin = getreader('utf-8')(fsock)
                
                self.logger.info("Reading vcf form stdin")
                self.vcf = sys.stdin
        
        else:
            file_name, file_extension = os.path.splitext(infile)
            if file_extension == '.gz':
                self.vcf = getreader('utf-8')(gzip.open(infile), errors='replace')
            elif file_extension == '.vcf':
                self.vcf = open(infile, mode='r', encoding='utf-8', errors='replace')
            else:
                raise IOError("File is not in a supported format!\n"
                                    " Or use correct ending(.vcf or .vcf.gz)")
        
        self.split_variants = split_variants
        self.logger.info("Split variants = {0}".format(self.split_variants))
        
        self.logger.info("Initializing HeaderParser")
        self.metadata = HeaderParser()
        # These are the individuals described in the header
        self.individuals = []
        # This is the header line of the vcf
        self.header = []
        
        self.next_line = self.vcf.readline().rstrip()
        self.current_line = self.next_line
        self.metadata.parse_meta_data(self.next_line)
        self.beginning = True
        
        while self.next_line.startswith('#'):
            if self.next_line.startswith('##'):
                self.metadata.parse_meta_data(self.next_line)
            elif self.next_line.startswith('#'):
                self.metadata.parse_header_line(self.next_line)
            self.next_line = self.vcf.readline().rstrip()
        
        self.individuals = self.metadata.individuals
        self.header = self.metadata.header
        self.vep_header = self.metadata.vep_columns
            
    def __iter__(self):
        for line in self.vcf:
            line = line.rstrip()
            # These are the variant(s) found in one line of the vcf
            # If there are multiple alternatives and self.split_variants
            # There can be more than one variant in one line
            variants = []
            if self.beginning:
                first_variant = format_variant(
                    next_line, self.individuals, self.header, self.vep_header
                )
                # If only one alternative or NOT split_variants we use only this variant
                if not (self.split_variants and len(first_variant['ALT'].split(',')) > 1):
                    variants.append(first_variant)
                    
                # If multiple alternative and split_variants we must split the variant                 
                else:
                    for variant in split_variants(first_variant, self.metadata):
                        variants.append(variant)
                
                self.beginning = False
            
            if len(line.split('\t')) >= 8:
                
                variant = format_variant(line)
                
                if not (self.split_variants and len(variant['ALT'].split(',')) > 1):
                    variants.append(variant)
                
                else:
                    for splitted_variant in split_variants(variant, self.metadata):
                        variants.append(splitted_variant)
            
            for variant in variants:
                yield variant


    def __str__(self):
        """return the headers header lines to screen."""
        return '\n'.join(self.metadata.print_header())
        

@click.command()
@click.argument('variant_file',
        type=click.Path(),
        metavar='<vcf_file> or -'
)
@click.option('--vep', 
                    is_flag=True,
                    help='If variants are annotated with the Variant Effect Predictor.'
)
@click.option('-s' ,'--split', 
                    is_flag=True,
                    help='Split the variants with multiallelic calls.'
)
def cli(variant_file, vep, split):
    """Parses a vcf file.\n
        \n
        Usage:\n
            parser infile.vcf\n
        If pipe:\n
            parser - 
    """
    from datetime import datetime
    if variant_file == '-':
        my_parser = VCFParser(fsock=sys.stdin, split_variants=split)
    else:
        my_parser = VCFParser(infile = variant_file, split_variants=split)
    start = datetime.now()
    nr_of_variants = 0
    # for line in my_parser.metadata.print_header():
    #     print(line)
    for variant in my_parser:
        pp(variant)
        nr_of_variants += 1
    # print('Number of variants: %s' % nr_of_variants)
    # print('Time to parse: %s' % str(datetime.now()-start))
    # pp(my_parser.metadata.extra_info)
    

if __name__ == '__main__':
    cli()
