import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils

from student_utils import *
"""
======================================================================
  Complete the following function.
======================================================================
"""

def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A list of (location, [homes]) representing drop-offs
    """
    G = nx.Graph()
    numLocations = len(list_of_locations)
    start_vertex = 0
    for i in range(numLocations):
        if list_of_locations[i].strip() == starting_car_location.strip() :
            start_vertex = i
            print("strt vertex:")
            print(start_vertex)
            break

    for i in range(numLocations):
        for j in range(numLocations):
            if adjacency_matrix[i][j] != 'x':
                wt = float(adjacency_matrix[i][j])
                G.add_edge(i, j, weight=wt)

    for i in range(numLocations):
        G.nodes[i]['name'] = list_of_locations[i]
        # G.nodes[i]['stops'] = []
        if (list_of_locations[i] in list_of_homes):
            G.nodes[i]['type'] = 'Home'
        else:
            G.nodes[i]['type'] = "Location"

    T = nx.minimum_spanning_edges(G)
    G1 = nx.Graph()
    for edge in T:
        G1.add_edge(edge[0], edge[1])
    for node in G1:
        G1.nodes[node]["dropoff"] = []
        G1.nodes[node]["name"] = G.nodes[node]["name"]
        G1.nodes[node]["type"] = G.nodes[node]["type"]


    def nodes_to_remove(type="Location"):
        nodes_to_remove = []
        for node in G1:
            # print("children of " + str(node))
            children = G1.neighbors(node)
            # convert key_iterator to list to make len() work
            # note: key_iterator can only be iterated once
            children = list(children)
            num_children = len(children)
            # print("number of children = " + str(num_children) + " for node " + str(node))
            # for child in list(children):
            #     print(child)

            if num_children == 1:
                # print("leaf node: " + str(node))
                # nodes_to_remove.append(node)
                if (G.nodes[node]['type'] == type):
                    nodes_to_remove.append(node)
        return nodes_to_remove


    while True:
        loc_nodes_to_remove = nodes_to_remove("Location")
        #we should not remove the starting vertex even though it's presented as leaf node in the graph
        if start_vertex in loc_nodes_to_remove:
            loc_nodes_to_remove.remove(start_vertex)
        print("nodes to remove: ")
        print(loc_nodes_to_remove)
        if len(loc_nodes_to_remove) == 0:
            print("NO node to remove")
            break
        # make a copy of all edges in G1
        # to avoid "RuntimeError: dictionary changed size during iteration"
        edges_cpy = []
        for edge in G1.edges():
            edges_cpy.append(edge)

        # remove all leaf locations(non-home) repeatedly until no locations(non-home) are leaves
        for edge in edges_cpy:
            for node in loc_nodes_to_remove:
                if edge[0] == node or edge[1] == node:
                    # G1.remove_edge(edge[0],edge[1])
                    if G.nodes[node]['type'] == 'Location':
                        G1.remove_edge(edge[0], edge[1])
        for node in loc_nodes_to_remove:
            try:
                G1.remove_node(node)
            except:
                print("node does not exist: " + str(node))
    # if leaf nodes are TA Homes, add them as dropoff of their parents
    home_nodes_to_remove = nodes_to_remove("Home")

    if start_vertex in home_nodes_to_remove:
        home_nodes_to_remove.remove(start_vertex)
    edges_cpy = []
    for edge in G1.edges():
        edges_cpy.append(edge)

    for edge in edges_cpy:
        for node in home_nodes_to_remove:
            if edge[0] == node or edge[1] == node:
                # G1.remove_edge(edge[0],edge[1])
                if G.nodes[node]['type'] == 'Home':
                    if edge[0] == node:
                        G1.nodes[edge[1]]['dropoff'].append(node)
                    else:
                        # print("dropoff")
                        # print(edge[0])
                        # print(G1.nodes[edge[0]])
                        G1.nodes[edge[0]]['dropoff'].append(node)
                    G1.remove_edge(edge[0], edge[1])

    print(home_nodes_to_remove)
    # remove all leaf nodes
    for node in home_nodes_to_remove:
        G1.remove_node(node)

    #If a stop itself is Home, insert itself in the front of "dropoff" list
    #create a dictionary/map to ensure a home can serve as dropoff only once
    home_as_dropoffs = {}
    for node in G1.nodes():
        if G1.nodes[node]['type'] == 'Home' :
            #add self to dropoffs only once when it first appears in the route
            if node not in home_as_dropoffs:
                G1.nodes[node]['dropoff'].insert(0, node)
                home_as_dropoffs[node] = 1

    G1.nodes(data=True)
    # for ele in G1.nodes.data():
    #     print("data : " + str(ele))


    visited = [False] * len(G.nodes())
    #define a 2XN array and initialize it with all 'x'
    euler = ['x'] * 2 * len(G.nodes())
    # use idx[0] in the recursive eulerTree method to ensure pass by reference for index
    idx = []
    # set idx[0] = 0
    idx.append(0)


    def eulerTree(vertex, idx):
        visited[vertex] = True
        euler[idx[0]] = vertex
        idx[0] += 1
        for node in G1.neighbors(vertex):
            if not visited[node]:
                eulerTree(node, idx)
                euler[idx[0]] = vertex
                idx[0] += 1


    def createEulerTour(start, N):
        eulerTour = []
        eulerTree(start_vertex, idx)
        for i in range(2 * N - 1):
            # print("euler i = " + str(i) + ", euler[i]=" + str(euler[i]))
            if (euler[i] != 'x'):
                eulerTour.append(euler[i])
        return eulerTour


    # print("G1")
    # print(G1.nodes())
    tour = createEulerTour(start_vertex, len(G1.nodes()))

    # output
    # stops = ""
    # for stop in tour:
    #     if stops == "":
    #         stops = list_of_locations[stop]
    #     else:
    #         stops = stops + " " + list_of_locations[stop]
    # print(stops)
    # output number of dropoffs
    #calculate number of stops with dropoffs(TA homes)>0
    num_stops = 0
    for stop in G1.nodes():
        if len(G1.nodes[stop]['dropoff']) > 0:
            num_stops += 1
    # print(num_stops)

    dropoff_list = []
    dropoff_mapping = {}
    for stop in G1.nodes():
        if len(G1.nodes[stop]['dropoff']) > 0:
            dropoff_mapping[stop] = G1.nodes[stop]['dropoff']
            dropoff_list.append(stop)

    drop_offs = ""
    for dropoff in dropoff_mapping.keys():
        strDrop = list_of_locations[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_of_locations[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        drop_offs += strDrop
    #return tour, dropoff_mapping


    print("******************optimized route*******************")
    #dropoffs will not change for the following optimization; only paths betwen two
    #continuous dropoffs are optimized
    prev_dropoff = start_vertex
    opt_route = []
    for stop in tour:
        if len(G1.nodes[stop]['dropoff']) > 0 and stop != start_vertex:
            shortest_path = nx.dijkstra_path(G, prev_dropoff, stop, "weight")
            # print(shortest_path)
            # print(G[shortest_path[0]][shortest_path[1]]['weight'])
            # path_str = ""
            # for node in shortest_path:
            #     path_str = path_str + " " + list_of_locations[node]
            # print(path_str)
            num_nodes_shortest_path = len(shortest_path)
            for i in range(num_nodes_shortest_path):
                #skip the last node in the path; it will be added in next path calculation
                if i < num_nodes_shortest_path - 1:
                    opt_route.append(shortest_path[i])
            prev_dropoff = stop
            dropoffs = list_of_locations[stop]
            # for ta in G1.nodes[stop]['dropoff'] :
            #     dropoffs += " " + list_of_locations[ta]
            # print(dropoffs)

    #find shortest path between prev_dropoff and start vertex
    last_dropoff = prev_dropoff
    shortest_path = nx.dijkstra_path(G, last_dropoff, start_vertex, "weight")
    for node in shortest_path:
        opt_route.append(node)


    stops = ""
    for stop in opt_route:
        if stops == "":
            stops = list_of_locations[stop]
        else:
            stops = stops + " " + list_of_locations[stop]


    print(stops)
    print(num_stops)
    print(drop_offs)
    return opt_route, dropoff_mapping

"""
======================================================================
   No need to change any code below this line
======================================================================
"""

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')
    print(input_files)

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
