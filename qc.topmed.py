import csv
import yaml
import os
import csv
import time
import argparse
parser = argparse.ArgumentParser()

parser.add_argument( "file", type=str )
parser.add_argument( "out", type=str )
parser.add_argument( "--ccdg", action='store_true' )
parser.add_argument( "--tm", action='store_true' )

args = parser.parse_args()

results = {}
header_line = []
date = time.strftime( "%m/%d/%Y" )

wd = os.getcwd()
cwd = os.getcwd()

input_fields = [
    'WorkOrder',
    'date_QC',
    'DNA',
    'instrument_data_count',
    'instrument_data_ids',
    'WorkingDirectory'
]
yaml_fields = [
    'ALIGNED_READS',
    'ALIGNMENT_RATE',
    'FIRST_OF_PAIR_MISMATCH_RATE',
    'SECOND_OF_PAIR_MISMATCH_RATE',
    'FREEMIX',
    'CHIPMIX',
    'HAPLOID_COVERAGE',
    'HET_SNP_Q',
    'HET_SNP_SENSITIVITY',
    'MEAN_COVERAGE',
    'MEAN_INSERT_SIZE',
    'STANDARD_DEVIATION',
    'PCT_10X',
    'PCT_20X',
    'PCT_ADAPTER',
    'PF_READS',
    'PF_ALIGNED_BASES',
    'TOTAL_BASES_Q20_OR_MORE',
    'TOTAL_PERCENT_DUPLICATION',
    'TOTAL_READS',
    'discordant_rate',
    'interchromosomal_rate',
    'reads_mapped_as_singleton_percentage',
    'reads_mapped_in_proper_pairs_percentage',
]

pair_header = [ 'PF_HQ_ALIGNED_Q20_BASES', 'STATUS' ]

def get_yaml( path ):
    file_name = '/qc_metrics.yaml'
    new_path = path + file_name
    with open( new_path ) as data:
        yaml_values = yaml.load_all( data )
        for yamlv in yaml_values:
            results[ 'PF_HQ_ALIGNED_Q20_BASES' ] = yamlv[ 'PAIR' ][ 'PF_HQ_ALIGNED_Q20_BASES' ]

            if( args.ccdg ):
                if ( yamlv[ 'FREEMIX' ] < 0.05 and yamlv[ 'HAPLOID_COVERAGE' ] >= 19.5 and yamlv[ 'discordant_rate' ] < 0.05
                     and yamlv[ 'interchromosomal_rate' ] < 0.05 and yamlv[ 'FIRST_OF_PAIR_MISMATCH_RATE' ] < 0.05
                     and yamlv[ 'SECOND_OF_PAIR_MISMATCH_RATE' ] < 0.05 ):
                    results[ 'STATUS' ] = 'pass'
                else:
                    results[ 'STATUS' ] = 'fail'

            elif( args.tm ):
                if (yamlv[ 'FREEMIX' ] < 0.01 and yamlv[ 'HAPLOID_COVERAGE' ] >= 30
                    and yamlv[ 'TOTAL_BASES_Q20_OR_MORE' ] >= 86,000,000,000
                    and yamlv[ 'PCT_10X' ] > 0.95 and yamlv[ 'PCT_20X' ] > 0.90
                    and yamlv[ 'CHIPIX' ] < 0.01):
                    results[ 'STATUS' ] = 'pass'
                else:
                    results[ 'STATUS' ] = 'fail'

            for k, v in yamlv.items():
                for field in yaml_fields:
                    if ( k == field ):
                        results[k] = v
    return results


def get_read_groups( path ):
    file_name = '/verify_bam_id.selfRG'
    new_path =  path + file_name
    read_groups = set()
    with open( new_path ) as data:
        reader = csv.DictReader( data, delimiter="\t" )
        for line in reader:
            read_groups.add( line[ 'RG' ] )
    return read_groups

with open( args.file ) as csvfile, open( args.out, 'w' ) as outfile: 

    reader = csv.DictReader( csvfile, delimiter="\t" )
    header_fields = input_fields + yaml_fields + pair_header
    w = csv.DictWriter( outfile, header_fields, delimiter="\t" )
    w.writeheader()


    for line in reader:
        results[ 'WorkOrder' ] = line[ 'WorkOrder' ]
        results[ 'date_QC' ] = date
        results[ 'DNA' ] = line[ 'DNA' ]
        results[ 'WorkingDirectory' ] = line[ 'WorkingDirectory' ]

        file_name = '/qc_metrics.yaml'
        new_path =  line[ 'WorkingDirectory' ] + file_name

        if  os.path.exists( new_path )==True:

            yaml_dict = get_yaml( line[ 'WorkingDirectory' ] )
            read_groups = get_read_groups( line[ 'WorkingDirectory' ] )
            css = ','.join( sorted( read_groups ) ) # comma-separated string
            count = len( read_groups )

            # Make a new dict using above data, plus fields from line
            results[ 'instrument_data_ids' ] = css
            results[ 'instrument_data_count' ] = count
            # Use csv.DictWriter to write the new dict to outfile.

            w.writerow( results )

        else:
            nofile = 'NA'
            print( results[ 'WorkOrder' ] + "\t" + results[ 'date_QC' ] + "\t" + results[ 'DNA' ]
                  + "\t" + results[ 'WorkingDirectory' ] + "\t" + nofile )
            outfile.write( results[ 'WorkOrder' ] + "\t" + results[ 'date_QC' ] + "\t" + results[ 'DNA' ]
                          + "\t\t\t" + results[ 'WorkingDirectory' ] + "\t" + nofile + "\n" )


exit()
