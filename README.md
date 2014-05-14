#VCF Parser#
Small library for parsing vcf files. Based on [PyVCF](https://github.com/jdoughertyii/PyVCF)

    pip install vcf_parser

```python3
    from vcf_parser import vcf_parser
    my_parser = vcf_parser('infile.vcf')
    for variant in my_parser:
        print(variant)
```

Returns dictionary with the vcf info.
The genotype information is parsed into a dictionary

    variant['ind_dict']

Vep information, if present is parsed into

    variant['vep_dict']

and looks like:

    'vep_info': {'NOC2L': {'Allele': 'G',
                            'Amino_acids': '',
                            'CDS_position': '',
                            'Codons': '',
                            'Consequence': 'downstream_gene_variant',
                            'DISTANCE': '3084',
                            'EXON': '',
                            'Existing_variation': '',
                            'Feature': 'NM_015658.3',
                            'Feature_type': 'Transcript',
                            'Gene': '26155',
                            'HGVSc': '',
                            'HGVSp': '',
                            'INTRON': '',
                            'PolyPhen': '',
                            'Protein_position': '',
                            'SIFT': '',
                            'STRAND': '-1',
                            'SYMBOL': 'NOC2L',
                            'SYMBOL_SOURCE': '',
                            'cDNA_position': ''},
                  'SAMD11': {'Allele': 'G',
                             'Amino_acids': '',
                             'CDS_position': '',
                             'Codons': '',
                             'Consequence': 'intron_variant',
                             'DISTANCE': '',
                             'EXON': '',
                             'Existing_variation': '',
                             'Feature': 'NM_152486.2',
                             'Feature_type': 'Transcript',
                             'Gene': '148398',
                             'HGVSc': 'NM_152486.2:c.707-25A>G',
                             'HGVSp': '',
                             'INTRON': '7/13',
                             'PolyPhen': '',
                             'Protein_position': '',
                             'SIFT': '',
                             'STRAND': '1',
                             'SYMBOL': 'SAMD11',
                             'SYMBOL_SOURCE': '',
                             'cDNA_position': ''}}

Individual genotypes are parsed into 

    variant['vep_dict']    

and looks like:

    'ind_dict': {'father': {'GQ': '60', 'GT': '0/0'},
                  'mother': {'GQ': '60', 'GT': '0/0'},
                  'proband': {'GQ': '60', 'GT': '0/1'}}

