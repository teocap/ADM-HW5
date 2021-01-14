import pandas as pd
import numpy as np
import time
from numpy.random import seed
from numpy.random import rand
import missingno as msno 
import plotly.express as px
import networkx as nx
from collections import deque
from statistics import median

# Function to find the set of all edges that a user can reach within d clicks
def reachable_edges_by_clicks(G, v, d):
    # G: Networkx graph
    # v: Initial desired page to look from
    # d: Number of clicks desired
    
    # Get iterator over all neighbors of nodes in G 
    neighbors = G.neighbors
    
    # Inizialize the visited list with the page desired
    visited = {v}
    
    # Initialize the queue list with the neighbors of the page (v) desired
    queue = deque([(v, d, neighbors(v))])
    
    # Loop until queue list is empty
    while queue:
        
        # Separate values of the first position of the queue list 
        actual_node, actual_d, neighbor_nodes = queue[0]
        
        try:
            # Get the actual neighbor (iterator)
            actual_neighbor = next(neighbor_nodes)
            
            # Check if the actual neighbor has been visited
            if actual_neighbor not in visited:
                # If the actual neighbor is not visited then keep the value of the node and the actual neighbor
                yield actual_node, actual_neighbor
                
                # If the actual neighbor is not visited then add it to the visited list
                visited.add(actual_neighbor)
                
                # Check if the desired number of clicks is reached
                if actual_d > 1:
                    # Append the neighbors of the actual neighbor to the queue list
                    queue.append((actual_neighbor, actual_d - 1, neighbors(actual_neighbor)))
        
        except StopIteration:
            # When there is no next neighbor node (iterator stops) then the first value of the stack list is removed
            queue.popleft()
            
            
# Function returning the degree centrality of nodes set V of an undirected graph G
def deg_centr(G):
    d = dict(G.degree(list(G.nodes)))
    l = [round(d[key]/(len(G.nodes)-1), 4) for key in d.keys()]
    return l

# Function returning minimum number of clicks to reach all pages in set p belonging to category C, from central node v
def min_click(U, C, p):
     
    # Finding the most central page of subgraph U
    l = deg_centr(U)
    max_value = max(l)
    v = list(U.nodes)[l.index(max_value)]
    
    flag = 0
    components = list(nx.connected_components(U))
    # Checking if the pages to cover are in the same connected component in order for the function to work
    for component in components:
        if v in p:
            if set.intersection(set(list(component)), set(p))==set(p):
                flag = 1
        else:
            if set.intersection(set(list(component)), set([v]+p))==set([v]+p):
                flag = 1
    if flag==0:
        print("Not Possible!")
    # Exploring U with the previous function; as soon as set p is covered, the function returns the number of clicks
    elif flag==1:
        d = 1
        nodes = []
        while set.intersection(set(p), set(nodes))!=set(p):
            hyper_reached = reachable_edges_by_clicks(U, v, d)
            pages_reached = [v] + [j for i, j in hyper_reached]
            nodes = pages_reached
            if set.intersection(set(p), set(nodes))!=set(p):
                d += 1
        
        return d

# Modified version of function above: v is start node in C0 and p is just one node of arrival in Ci
def min_click_cat(G, v, p):
    
    flag = 0
    components = list(nx.connected_components(G))
    
    for component in components:
        if set.intersection(set(list(component)), set([v]+p))==set([v]+p):
                flag = 1
    if flag==0:
        s = "Not connected!"
        
        return s
    
    elif flag==1:
        d = 1
        nodes = []
        while set.intersection(set(p), set(nodes))!=set(p):
            hyper_reached = reachable_edges_by_clicks(G, v, d)
            pages_reached = [v] + [j for i, j in hyper_reached]
            nodes = pages_reached
            if set.intersection(set(p), set(nodes))!=set(p):
                d += 1
        
        return d

# Function returning the sorted list of categories by their distance from chosen category C0
def sort_cat(ds, G, C0):
    
    Cs = list(set(ds["category"].values))
    d = {}
    nodes_C0 = list(ds[ds["category"]==C0]["pages_code"])
    for Ci in Cs:
        short_paths = []
        nodes_Ci = list(ds[ds["category"]==Ci]["pages_code"])
        nodes = nodes_C0 + nodes_Ci
        inter = set.intersection(set(nodes), set(list(G.nodes)))
        inter_0 = set.intersection(set(nodes_C0), inter)
        inter_i = set.intersection(set(nodes_Ci), inter)
        if inter!=set([]) and inter_0!=set([]) and inter_i!=set([]) and Ci!=C0:
            for node_0 in inter_0:
                for node_i in inter_i:
                    if sorted(list(nx.node_connected_component(G, node_0)))==sorted(list(nx.node_connected_component(G, node_i))):
                        short_paths.append(min_click_cat(G, node_0, [node_i]))
        # Calculation of the distance between C0 and Ci, defined as the median of the shortest paths (minimum number of clicks) from each pair of nodes in the two categories 
        if short_paths!=[]:
            d[C0+"---"+Ci] = median(short_paths)
    
    # Sorting of the dictionary of distances
    dist = {k: v for k, v in sorted(d.items(), key=lambda item: item[1])}

    return list(dist.keys())