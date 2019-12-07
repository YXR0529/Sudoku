'''
Project: Sudoku
Authors: Xinru Yun, Tianjun Tang(Don)

Course: Software Carpentry
Johns Hopkins University


This is our Final Project of Software Carpentry,
in which we decided to apply BFS (Breadth First Search)
method to solve various kinds of sudoku games.

Our data source is Conceptis, which is a series of games
that can be downloaded from Appstore, and contains six kinds
of Sudoku to play with, that are, standard, curve, diagonal,
odd/even, multi and killer sudoku.

Based on standard sudoku rules, they added different extra rules
like, in odd/even, some places can only be odd or even numbers, or,
in killer sudoku, blocks have been devided into even smaller groups
while requiring their sum to be a given number.

Generally, to solve a sudoku, you need a .sdk file, which
basically looks like following:

TYPE: STANDARD_SUDOKU # indicates type of sudoku

NUMBER_START # shows the numbers on the map, 0 if it's blank
502090100
000100080
300006002
040000700
600000001
005000090
900700004
060003000
007020503
NUMBER_END

MAP_START # shows how numbers are divided into different groups
a a a b b b c c c # in each group numbers should all be different
a a a b b b c c c
a a a b b b c c c
d d d e e e f f f
d d d e e e f f f
d d d e e e f f f
g g g h h h i i i
g g g h h h i i i
g g g h h h i i i
MAP_END

Further nomenclatures can be found in our repository under main folder.

'''
import functools
from itertools import combinations


class killer_sudoku():
    def read_sdk(self, filename):
        '''
        This is a function used to read the sudoku file as a dictionary.
        (Written by Xinru)

        **Parameters**

            filename: *string*

        **Returns**

            file: *dictionary*
        '''
        f = open(filename, "r")
        file = {}
        number = []
        map = []
        # Skip the line before "NUMBER_START"
        for line in f:
            if line.strip() == "NUMBER_START":
                break
        for line in f:
            # Skip the line after "NUMBER_END"
            if line.strip() == "NUMBER_END":
                break
            # Generate a list of lists with information of the numbers.
            lst = []
            if line != "\n":
                for x in line.strip():
                    if x != " ":
                        lst.append(int(x))
                number.append(lst)
        # Add number to the dictionary.
        file["map"] = number
        # Skip the line before "MAP_START"
        for line in f:
            if line.strip() == "MAP_START":
                break
        for line in f:
            # Skip the line after "GRID STOP"
            if line.strip() == "MAP_END":
                break
            # Generate a list of lists with information of the map.
            lst = []
            if line != "\n":
                for y in line.strip().split(' '):
                    if y != " " and y != '':
                        lst.append(y)
                map.append(lst)
        file['killer_groups'] = {}
        for y, row in enumerate(map):
            for x, z in enumerate(row):
                file['killer_groups'][z] = []
        for y, row in enumerate(map):
            for x, z in enumerate(row):
                file['killer_groups'][z].append((x, y))
        # Close the file
        file['killer_sum'] = {}
        for line in f:
            if line.strip() == "KILLER_START":
                break
        for line in f:
            # Skip the line after "GRID STOP"
            if line.strip() == "KILLER_END":
                break
            if line != "\n":
                # print(line)
                y = line.strip().split(' ')
                gp, val = y[0], y[-1]
                file['killer_sum'][gp] = int(val)
        f.close()
        return file

    def load_sdk_map(self, info_dict):
        '''
        This part is written by Don.

        This function reads raw informations info_dict after read_sdk()
        and convert them into more useful and processable forms, which
        contains:

        *** original groups ***
        Shows which groups that each point belongs to.

        *** original numbers ***
        The Given numbers on the map, which will be merged
        with manually putted points during solution process.

        *** Blank Positions ***
        A list showing all blank positions on the map, only used
        in this function.

        *** Fixed Number ***
        An empty dictionary to store manually putted points during
        solution.

        *** Possibility ***
        A dictionary showing which numbers can be putted in a given
        position, this part is the key to solve problems.

        *** killer groups ***
        small groups on the map that contains both position and sum
        informations

        *** killer sum ***
        information of the sum number of each killer groups

        *** sum possibility ***
        possible number combinations of each killer group

        '''
        # Initialize all blank positions on the map
        info_dict['original_numbers'] = {}
        info_dict['blank_positions'] = []
        info_dict['fixed_number'] = {}
        # Input infos about both given points and blank positions
        for row in range(len(info_dict['map'])):
            for column in range(len(info_dict['map'][row])):
                if info_dict['map'][row][column] == 0:
                    info_dict['blank_positions'].append((column, row))
                else:
                    info_dict['original_numbers'][(column, row)] =\
                        info_dict['map'][row][column]
        # Generate a dictionary of possibility of all blank points
        info_dict['possibility'] = {}
        for point in info_dict['blank_positions']:
            info_dict['possibility'][point] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # manually add groups as standard sudoku
        info_dict['original_groups'] = {
            'a': [
                (0, 0), (1, 0), (2, 0),
                (0, 1), (1, 1), (2, 1),
                (0, 2), (1, 2), (2, 2)],
            'b': [
                (3, 0), (4, 0), (5, 0),
                (3, 1), (4, 1), (5, 1),
                (3, 2), (4, 2), (5, 2)],
            'c': [
                (6, 0), (7, 0), (8, 0),
                (6, 1), (7, 1), (8, 1),
                (6, 2), (7, 2), (8, 2)],
            'd': [
                (0, 3), (1, 3), (2, 3),
                (0, 4), (1, 4), (2, 4),
                (0, 5), (1, 5), (2, 5)],
            'e': [
                (3, 3), (4, 3), (5, 3),
                (3, 4), (4, 4), (5, 4),
                (3, 5), (4, 5), (5, 5)],
            'f': [
                (6, 3), (7, 3), (8, 3),
                (6, 4), (7, 4), (8, 4),
                (6, 5), (7, 5), (8, 5)],
            'g': [
                (0, 6), (1, 6), (2, 6),
                (0, 7), (1, 7), (2, 7),
                (0, 8), (1, 8), (2, 8)],
            'h': [
                (3, 6), (4, 6), (5, 6),
                (3, 7), (4, 7), (5, 7),
                (3, 8), (4, 8), (5, 8)],
            'i': [
                (6, 6), (7, 6), (8, 6),
                (6, 7), (7, 7), (8, 7),
                (6, 8), (7, 8), (8, 8)]}
        # generate possible combinations of killer group
        # and generate possibility list as usual
        info_dict['sum_possibility'] = {}
        info_dict['possibility'] = {}
        comb = []
        for k_gp in info_dict['killer_sum']:
            n = len(info_dict['killer_groups'][k_gp])
            combination = killer_sudoku.get_comb(
                self, info_dict['killer_sum'][k_gp], n)
            info_dict['sum_possibility'][k_gp] = [c for c in combination]
            num_list = []
            for comb in combination:
                num_list += list(comb)
            num_list = killer_sudoku.delete_duplicated_element(self, num_list)
            for point in info_dict['killer_groups'][k_gp]:
                info_dict['possibility'][point] = [n for n in num_list]
        return info_dict

    def get_comb(self, total, n):
        '''
        This part is written by Don

        get combinations of given number
        '''
        num = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        test = list(combinations(num, n))
        res = [x for x in test if sum(x) == total]
        return res

    def delete_duplicated_element(self, listA):
        '''
        Author: Don

        A little function to delete duplicated functions from
        a list
        '''
        return sorted(set(listA), key=listA.index)

    def sub_points(self, info_dict):
        '''
        This part is written by Don.

        This function removes those impossible 'possibilities' of each
        position, whose rules varies and gets increasingly complicated when
        solving more advanced problems.

        Following code contains five parts:
        # remove im_possibilities at each row/column
        # remove im_possibilities within each group
        # generate a position whose possibility list is shortest, which
            ## can be used for BFS growth
            ## shows wrong combination when it's []
        # remove impossible combinations based on given points
        # remove impossibility based on remaining combinations
        '''
        info_dict['fixed_number'].update(info_dict['original_numbers'])
        for fp in info_dict['fixed_number']:
            if fp in info_dict['possibility']:
                info_dict['possibility'].pop(fp)
            fp_x, fp_y = fp[0], fp[1]
            # Sub Row Possibilities
            test_x = 10
            while test_x >= 0:
                if (test_x, fp_y) in info_dict['possibility']:
                    if info_dict['fixed_number'][fp] in\
                            info_dict['possibility'][(test_x, fp_y)]:
                        info_dict['possibility'][(test_x, fp_y)].remove(
                            info_dict['fixed_number'][fp])
                test_x -= 1
            # Sub Column Possibilities
            test_y = 10
            while test_y >= 0:
                if (fp_x, test_y) in info_dict['possibility']:
                    if info_dict['fixed_number'][fp] in\
                            info_dict['possibility'][(fp_x, test_y)]:
                        info_dict['possibility'][(fp_x, test_y)].remove(
                            info_dict['fixed_number'][fp])
                test_y -= 1
            # Sub Group Possibilities
            for grp in info_dict['original_groups']:
                if fp in info_dict['original_groups'][grp]:
                    for point in info_dict['original_groups'][grp]:
                        if point in info_dict['possibility']:
                            if info_dict['fixed_number'][fp] in\
                                    info_dict['possibility'][point]:
                                info_dict['possibility'][point].remove(
                                    info_dict['fixed_number'][fp])
            # Sub killer Group Possibilities
            # (duplicated elements are not allowed inside a killer group)
            for kl_gp in info_dict['killer_groups']:
                if fp in info_dict['killer_groups'][kl_gp]:
                    for point in info_dict['killer_groups'][kl_gp]:
                        if point in info_dict['possibility']:
                            if info_dict['fixed_number'][fp] in\
                                    info_dict['possibility'][point]:
                                info_dict['possibility'][point].remove(
                                    info_dict['fixed_number'][fp])
            # Remove possible sum combinations based on fixed points
            for kl_gp in info_dict['killer_groups']:
                if fp in info_dict['killer_groups'][kl_gp]:
                    for comb in info_dict['sum_possibility'][kl_gp]:
                        if info_dict['fixed_number'][fp] not in comb:
                            info_dict['sum_possibility'][kl_gp].remove(comb)

        # Remove point possibility based on remaining sum combinations
        for rm_grp in info_dict['sum_possibility']:
            num_list = []
            for rm_comb in info_dict['sum_possibility'][rm_grp]:
                num_list += rm_comb
            num_list = killer_sudoku.delete_duplicated_element(self, num_list)
            for pt in info_dict['killer_groups'][rm_grp]:
                if pt in info_dict['possibility']:
                    for number in info_dict['possibility'][pt]:
                        if number not in num_list:
                            info_dict['possibility'][pt].remove(number)
        # gets shortest point
        info_dict['shortest'] = functools.reduce(
            lambda x, y: x if len(
                info_dict['possibility'][x]
            ) < len(info_dict['possibility'][y])
            else y, info_dict['possibility'])
        return info_dict

    def next_number(self, info_dict, next_list):
        '''
        This part is written by Don.

        This functions is for BFS growth.

        Given current list of combinations, which is stored as a list
        of dictionaries, this function initialize the map and make point
        subtractions, and judges whether the combination is valid.

        If the shortest possibilities is not [], then duplicate current
        combinations and paste different possibility in the end, and
        return a new list of right combinations.
        '''
        info_dict = killer_sudoku.sub_points(self, info_dict)
        new_list = []
        for p in next_list:
            info_dict = killer_sudoku.load_sdk_map(self, info_dict)
            info_dict['fixed_number'].update(p)
            info_dict = killer_sudoku.sub_points(self, info_dict)
            if info_dict['shortest'] != {}:
                for n in info_dict['possibility'][info_dict['shortest']]:
                    possibility = {}
                    for ps in p:
                        possibility[ps] = p[ps]
                    possibility[info_dict['shortest']] = n
                    new_list.append(possibility)
                info_dict['possibility'].pop(info_dict['shortest'])
        return new_list

    def solve_sdk(self, info_dict):
        '''
        This part is written by Don.

        This functions are all the same in different files.
        By subtracting points first, we get an initial possible
        combination to start with.

        Repeat BFS generation until the possibility dictionary
        is empty, and returns the final answer.
        '''
        info_dict = killer_sudoku.sub_points(self, info_dict)
        next_list = []
        for n in info_dict['possibility'][info_dict['shortest']]:
            next_list.append({info_dict['shortest']: n})
        while info_dict['possibility'] != {}:
            next_list = killer_sudoku.next_number(self, info_dict, next_list)
            if next_list == []:
                break
            print(len(next_list))
        info_dict['final'] = {}
        info_dict['final'].update(next_list[0])
        return info_dict


if __name__ == "__main__":
    a = killer_sudoku()
    b = a.read_sdk("killer_simple_1_0.sdk")
    c = a.load_sdk_map(b)
    d = a.sub_points(c)
    e = a.solve_sdk(c)
    print(e)
