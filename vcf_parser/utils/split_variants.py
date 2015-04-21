from __future__ import unicode_literals

import sys

from logging import getLogger

if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

from vcf_parser.utils import build_vep_string, split_genotype

def split_variants(variant_dict, metadata=None):
    """
    Checks if there are multiple alternative alleles and splitts the 
    variant.
    If there are multiple alternatives the info fields, vep annotations 
    and genotype calls will be splitted in the correct way
    
    Args:
        variant_dict: a dictionary with the variant information
    
    Yields:
        variant: A variant dictionary with the splitted information for each
                alternative
    """
    
    alternatives = variant_dict['ALT'].split(',')
    reference = variant_dict['REF']
    number_of_values = 1
    # Go through each of the alternative alleles:
    for alternative_number, alternative in enumerate(alternatives):
        variant = {}
        info_dict = OrderedDict()
        # This is a dict on the form {ALT:[{vep_info_dict}]}
        vep_dict = {}
        genotype_dict = {}
        variant['CHROM'] = variant_dict['CHROM']
        variant['POS'] = variant_dict['POS']
        try:
            # There will not allways be one rsID for each alternative
            variant['ID'] = variant_dict['ID'].split(';')[alternative_number]
        # If only one id is present for multiple alleles they all get the same ID
        except IndexError:
            variant['ID'] = variant_dict['ID']
        
        variant['REF'] = variant_dict['REF']
        variant['ALT'] = alternative
        variant['QUAL'] = variant_dict['QUAL']
        variant['FILTER'] = variant_dict['FILTER']
        

        if 'FORMAT' in variant_dict:
            variant['FORMAT'] = variant_dict['FORMAT']

        for info in variant_dict['info_dict']:
            if info:
                # Check if the info field have one entry per allele:
                if metadata:
                    try:
                        number_of_values = metadata.extra_info[info]['Number']
                    except KeyError:
                        logger.error("One of the FILTER lines is missing in vcf"\
                                "header: {0}".format(info))
                        raise
                
                if info == 'CSQ':
                    try:
                        vep_dict[alternative] = variant_dict['vep_info'][alternative]
                        info_dict['CSQ'] = [
                            build_vep_string(variant_dict['vep_info'][alternative])
                        ]
                    except KeyError:
                        pass
                # If there is one value per allele we need to split it in
                # the proper way
                elif number_of_values == 'A':
                    try:
                        # When we split the alleles we only want to annotate with the correct number
                        info_dict[info] = [variant_dict['info_dict'][info][alternative_number]]
                    except IndexError:
                        # If there is only one annotation we choose that one
                        info_dict[info] = [variant_dict['info_dict'][info][0]]
                # Choose the right vep info from the old variant
                elif number_of_values == 'R':
                    reference_value = variant_dict['info_dict'][info][0]
                    new_info = [reference_value]
                    try:
                        # When we split the alleles we only want to annotate with the correct number
                        new_info.append(variant_dict['info_dict'][info][alternative_number + 1])
                        info_dict[info] = new_info
                    except IndexError:
                        # If annotation is missing we keep the original annotation
                        pass
                    
                else:
                    info_dict[info] = variant_dict['info_dict'][info]
                
            else:
                info_dict[info] = []
        
        variant['INFO'] = build_info_string(info_dict)
        
        for individual in variant_dict['genotypes']:
            new_genotype = split_genotype(
                            variant_dict[individual], 
                            variant['FORMAT'], 
                            alternative_number
                        )
            
            variant[individual] = new_genotype
            genotype_dict[individual] = Genotype(**dict(zip(gt_format.split(':'), variant[individual].split(':'))))
            
        variant['info_dict'] = info_dict
        variant['vep_info'] = vep_dict
        variant['genotypes'] = genotype_dict
        variant['variant_id'] = '_'.join([variant['CHROM'],
                                    variant['POS'],
                                    variant['REF'],
                                    alternative])
        
        yield variant
