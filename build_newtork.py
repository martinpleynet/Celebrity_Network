'''
This script takes the output of the scrape_relationships script and builds
a network graph with all celebrities as nodes and edges between to
celebrities that have been in a relationship.
'''

import networkx as nx
import matplotlib.pyplot as plt
import argparse
import json

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('target_celebs', help='json file with target celebs as keys and their partners as values')
    args = parser.parse_args()

    # Parse target_celebs file
    with open(args.target_celebs) as f:
        parsed_celebs = json.load(f)
        
    targets = list(parsed_celebs.keys())

    # Create network graph
    G = nx.Graph()

    # add all of the target celebs as nodes to the graph
    for i in targets:
        G.add_node(i)

    # add all of the partners as nodes and then add an edge between target and partner
    for target in parsed_celebs:
        for partner in parsed_celebs[target]:
            G.add_node(partner)
            G.add_edge(target, partner)

    # set the color of target nodes different from partner nodes
    color_map = []
    for node in G:
        if node in targets:
            color_map.append('red')
        else:
            color_map.append('skyblue')

    # draw network graph with all the features
    nx.draw(G, node_color=color_map, with_labels=True, font_size=6, edge_color = '#d9d9d9')

    plt.savefig("celeb_network.png")
    
if __name__ == '__main__':
    main()
