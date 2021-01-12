'''
This script scrapes the relationships on the Who's Dated Who pages of
celebrities listed in a config file along with the path to a cache.
'''

import argparse
from bs4 import BeautifulSoup
import json
import requests
import os
import os.path as osp
import hashlib

def get_url_contents(url, cache_dir):
    fname = hashlib.sha1(url.encode('utf-8')).hexdigest()
    full_fname = osp.join(cache_dir, fname)

    contents = None
    # from cache
    if osp.exists(full_fname):
        contents = open(full_fname, 'r').read()
    # from source
    else:
        r = requests.get(url)
        contents = r.text
        with open(full_fname, 'w') as fh:
            fh.write(contents)
            
    return full_fname


def extract_relationships_from_candidate_links(candidates, person_url):
        relationships = []

        for link in candidates:
                if 'href' not in link.attrs:
                        continue

                href = link['href']

                if href.startswith('/dating') and href != person_url:
                        relationships.append(href.replace('/dating/', ''))

        return relationships

    
def extract_relationships(filename, person_url):

    relationships = []
        
    soup = BeautifulSoup(open(filename, 'r'), 'html.parser')

    ###
    # get current relationship
    
    # grab the h4 with class= ff-auto-status
    status_h4 = soup.find('h4', 'ff-auto-status')

    # grab the nxt sibling
    key_div = status_h4.next_sibling

    # grab all the a elements
    candidate_links = key_div.find_all('a')

    # 
    relationships.extend(extract_relationships_from_candidate_links(candidate_links, person_url))

    # sanity check for number of relationships
    if len(relationships) > 1:
        raise Exception('Too many relationships - should have only one')
    
    ###
    # get all prior relationships
    rels_h4 = soup.find('h4', 'ff-auto-relationships')
    sib = rels_h4.next_sibling

    while sib is not None and sib.name == 'p':
        candidate_links = sib.find_all('a')
        sib=sib.next_sibling
            

        relationships.extend(extract_relationships_from_candidate_links(candidate_links, person_url))
            
    return relationships


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file')
    parser.add_argument('-o', '--output_file')
    args = parser.parse_args()

    # open config file and load json
    with open(args.config_file) as f:
        
        parsed_data = json.load(f)

    cache_dir = osp.join(osp.dirname(__file__), parsed_data['cache_dir'])

    url_stem = 'https://www.whosdatedwho.com/dating/'
    celeb_list = parsed_data['target_people']

    r_dict={}

    # iterate through celeb list and extract relationships
    for celeb in celeb_list:

        url = url_stem + celeb
        
        cur_fname = get_url_contents(url, cache_dir)
            
        person = '/dating/' + celeb
        
        relationships = extract_relationships(cur_fname, person)
        r_dict[person.split('/')[-1]] = relationships

    # write out dict of all celebs and their relationships
    with open(args.output_file, 'w') as f:
        json.dump(r_dict, f, indent=2)
        

if __name__ == "__main__":
    main()
    
       
