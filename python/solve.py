"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
from pathlib import Path
from typing import Callable, Dict

from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper
from cover import Cover
from point import Point
from typing import Iterable, List, TYPE_CHECKING
from centroid import Centroid 

def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

def solve_greedy(instance: Instance) -> Solution:
    D = instance.grid_side_length
    R_s = instance.coverage_radius
    R_p = instance.penalty_radius
    cities = instance.cities

    # For each integer grid point, assume there is a tower on this point, find all cities it can cover 
    all_sets = []
    t = [[[] for i in range(D)] for j in range(D)]
    for city in cities: 
        for i in range(max(0,city.x-R_s),min(D-1,city.x+R_s)+1):
            for j in range(max(0,city.y-R_s),min(D-1,city.y+R_s)+1):
                if ((i-city.x)**2+(j-city.y)**2)**0.5 <= R_s:
                    t[i][j].append(city)

    for i in range(len(t)):
        for j in range(len(t)):
            if t[i][j] != []:
                cover = Cover()
                cover.center = [i,j]
                cover.add_tower(cover.set_tower())
                for city in t[i][j]:
                    cover.put(city)
                all_sets.append(cover)

    
    # Some tower loctions may cover the same cities 
    # We remove the duplicate, and record all possible tower points for this city set in one Cover
    all_sets_no_duplicate = []
    while len(all_sets) != 0:
        c1 = all_sets.pop(0)
        for c2 in all_sets:
            if c1.size != c2.size:
                continue
            if Cover.same_cover(c1, c2):
                c1.add_tower(c2.set_tower())
                all_sets.remove(c2)
        all_sets_no_duplicate.append(c1)


    # Sort covers by size decreasing
    def list_length(l):
        return l.size

    #all_sets_no_duplicate.sort(reverse=True, key=list_length)
    all_sets.sort(reverse=True, key=list_length)


    # Greedy helper functions
    def overlap_size(l1, l2):
        size = 0
        for x in l1:
            if x in l2.points:
                size += 1
        return size

    
    def can_greedy(sets):
        all_elements = sum([set.points for set in sets], [])
        for c in cities:
            if c not in all_elements:
                return False
        return True


    def is_penalty(i,j,present):
        count = 0
        for n in range(max(0,i-3),min(D,i+4)):
            for m in range(max(0,j-3),min(D,j+4)):
                if (present[n][m] == 1) and ((n-i)**2+(m-j)**2)**0.5 <= 2*R_p:
                    count = count + 1
        return count 

    def is_valid(i,j):
        if i < 0 or j < 0:
            return False
        if i >= D or j >= D:
            return False
        return True 
    
    def find_tower(set_cover):
        t = []
        # initiate the graph 
        graph = []
        group = 0 
        for s in set_cover:
            i = 0 
            for c in s.towers: 
                graph.append(Centroid(group,c.x,c.y))
                i = i + 1 
            group = group + 1 

        #add edges
        for g in graph: 
            for k in graph: 
                if not g.group == k.group: 
                    g.add_penalty(k, R_p)
                else:
                    g.gs = g.gs + 1 
        
        #greedy 
        while group > 0: 
            min_index = 0 
            min_penalty = float('inf')
            for i in range(len(graph)): 
                if graph[i].valid and graph[i].size() + corner(graph[i].x,graph[i].y) + 1.1 * graph[i].gs< min_penalty:
                    min_index = i 
                    min_penalty = graph[i].size() + corner(graph[i].x,graph[i].y) + 1.1 * graph[i].gs
            t.append(Point(graph[min_index].x,graph[min_index].y))
            group = group - 1
            g = graph[min_index].group
            #record all centroids to be removed 
            gra = []
            for a in graph: 
                if a.devalid(g) and a != graph[min_index]:
                    gra.append(a)
            # remove edges from the remaining centroids
            for a in graph: 
                for b in gra: 
                    a.remove_penalty(b)
    
        return t

    def corner(i,j):
        #calculate the distance from the edge --> we try to put it closer to the edges
        x = min(i,D-i)
        y = min(j,D-j)
        return 0.001 * (x+y)

    def greedy_set_cover(sets):
        uncovered = cities.copy()
        set_cover = []
        
        while len(uncovered)!=0:
            max_overlap = -1
            max_index = -1
            for i in range(len(sets)):
                os = overlap_size(uncovered, sets[i])
                if os > max_overlap:
                    max_overlap = os
                    max_index = i
            pop_set = sets.pop(max_index)
            #print(pop_set.size)
            set_cover.append(pop_set)
            for c in pop_set.points:
                if c in uncovered:
                    uncovered.remove(c)

        #towers = [c.set_tower() for c in set_cover]
        #return Solution(instance=instance, towers=towers)
        return set_cover

    sets_for_greedy = all_sets_no_duplicate.copy()
    greedy_solutions = []
    while can_greedy(sets_for_greedy):
        set_cover = greedy_set_cover(sets_for_greedy.copy())
        soluu = find_tower(set_cover)
        solu = Solution(instance=instance, towers = soluu)
        if solu.valid():
            greedy_solutions.append(solu)
        sets_for_greedy.pop(0)

    penalties = [solution.penalty() for solution in greedy_solutions]
    min_penalty = float("inf")
    min_index = -1
    for i in range(len(penalties)):
        if penalties[i] < min_penalty:
            min_penalty = penalties[i]
            min_index = i

    print(min_index, len(penalties))
    return greedy_solutions[min_index]

SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "greedy": solve_greedy
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")


def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")


def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
