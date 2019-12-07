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
import numpy as np
from PIL import Image, ImageDraw


class multi_sudoku():
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
        file["original_map"] = number
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
                    lst.append(y)
                map.append(lst)
        # append diffrent original groups to the dictionary.
        file['original_groups'] = {}
        for y, row in enumerate(map):
            for x, z in enumerate(row):
                if z != 'oo':
                    file['original_groups'][z] = []
        for y, row in enumerate(map):
            for x, z in enumerate(row):
                if z != 'oo':
                    file['original_groups'][z].append((x, y))
        # Close the file
        f.close()
        return file

    def load_sdk_map(self, info_dict):
        '''
        This part is written by Don.

        This function reads raw informations info_dict after read_sdk()
        and convert them into more useful and processable forms, which
        contains:

        *** groups ***
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

        *** sub map ***
        An extra dictionary that divides the whole map into several
        different standard sudoku maps.

        '''
        # Initialize all blank positions on the map
        info_dict['original_numbers'] = {}
        info_dict['fixed_number'] = {}
        info_dict['groups'] = {}
        info_dict['possibility'] = {}
        info_dict['sub_map'] = {}
        # all points serves same function as 'blank_positions'
        # in standard sudoku
        all_points = []
        for gp in info_dict['original_groups']:
            for pt in info_dict['original_groups'][gp]:
                all_points.append(pt)
        for apt in all_points:
            info_dict['possibility'][apt] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # Input infos about both given points and blank positions
        for row in range(len(info_dict['original_map'])):
            for column in range(len(info_dict['original_map'][row])):
                if info_dict['original_map'][row][column] != 0:
                    info_dict['original_numbers'][(column, row)] =\
                        info_dict['original_map'][row][column]
                    info_dict['possibility'].pop((column, row))
        # Generate different standard maps
        info_dict['groups'] = {}
        for g in ['a', 'b', 'c', 'd', 'e']:
            info_dict['groups'][g] = {}
            info_dict['sub_map'][g] = []
            for orgrp in info_dict['original_groups']:
                if g in orgrp:
                    info_dict['groups'][g][orgrp] =\
                        info_dict['original_groups'][orgrp]
                    info_dict['sub_map'][g] +=\
                        info_dict['original_groups'][orgrp]
        return info_dict

    def sub_points(self, info_dict):
        '''
        This part is written by Don.

        This function removes those impossible 'possibilities' of each
        position, whose rules varies and gets increasingly complicated when
        solving more advanced problems.

        Following code contains three parts:
        # remove im_possibilities at each row/column
        # remove im_possibilities within each group
        # generate a position whose possibility list is shortest, which
            ## can be used for BFS growth
            ## shows wrong combination when it's []
        '''
        info_dict['fixed_number'].update(info_dict['original_numbers'])
        # loops through each sub map
        # other processes are the same
        for fp in info_dict['fixed_number']:
            if fp in info_dict['possibility']:
                info_dict['possibility'].pop(fp)
            fp_x, fp_y = fp[0], fp[1]
            for grp in info_dict['sub_map']:
                if fp in info_dict['sub_map'][grp]:
                    # Sub Row Possibilities
                    test_x = 21
                    while test_x >= 0:
                        if (test_x, fp_y) in info_dict['possibility'] and\
                                (test_x, fp_y) in info_dict['sub_map'][grp]:
                            if info_dict['fixed_number'][fp] in\
                                    info_dict['possibility'][(test_x, fp_y)]:
                                info_dict['possibility'][
                                    (test_x, fp_y)
                                ].remove(info_dict['fixed_number'][fp])
                        test_x -= 1
                    # Sub Column Possibilities
                    test_y = 21
                    while test_y >= 0:
                        if (fp_x, test_y) in info_dict['possibility'] and\
                                (fp_x, test_y) in info_dict['sub_map'][grp]:
                            if info_dict['fixed_number'][fp] in\
                                    info_dict['possibility'][(fp_x, test_y)]:
                                info_dict['possibility'][
                                    (fp_x, test_y)
                                ].remove(info_dict['fixed_number'][fp])
                        test_y -= 1
                    # Sub Group Possibilities
                    for single_gp in info_dict['groups'][grp]:
                        if fp in info_dict['groups'][grp][single_gp]:
                            for point in info_dict['groups'][grp][single_gp]:
                                if point in info_dict['possibility']:
                                    if info_dict['fixed_number'][fp] in\
                                            info_dict['possibility'][point]:
                                        info_dict['possibility'][point].remove(
                                            info_dict['fixed_number'][fp])
        # Get shortest possibility
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
        info_dict = multi_sudoku.sub_points(self, info_dict)
        new_list = []
        for p in next_list:
            info_dict = multi_sudoku.load_sdk_map(self, info_dict)
            info_dict['fixed_number'].update(p)
            info_dict = multi_sudoku.sub_points(self, info_dict)
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
        info_dict = multi_sudoku.sub_points(self, info_dict)
        next_list = []
        for n in info_dict['possibility'][info_dict['shortest']]:
            next_list.append({info_dict['shortest']: n})
        while info_dict['possibility'] != {}:
            next_list = multi_sudoku.next_number(self, info_dict, next_list)
            if next_list == []:
                break
        info_dict['final'] = {}
        info_dict['final'].update(next_list[0])
        return info_dict

    def save_sdk_txt(self, info_dict, filename):
        '''
        This is a function used to generate a .txt
        file of the solution from the dictionary.
        (Written by Xinru)

        **Parameters**

            info_dict: *dictionary*
            filename: *string*

        **Returns**

            f: *.txt file*
        '''

        f = open(filename, 'w')
        map = info_dict['original_map']
        for (p_x, p_y) in info_dict['final']:
            map[p_y][p_x] = info_dict['final'][(p_x, p_y)]
        for y in range(len(map)):
            for x in range(len(map[0])):
                if map[y][x] == 0:
                    f.write('  ')
                else:
                    f.write(str(map[y][x]) + ' ')
            f.write('\n')
        f.close()
        return f

    def set_color(self, img, x0, y0, dim, gap, color):
        '''
        This is a function used to change the color of a certain block.
        (Written by Xinru)

        **Parameters**

            img: *image*
            x0: *integer*
            y0: *integer*
            dim: *integer*
            gap: *integer*
            color: *tuple*

        '''
        for x in range(dim):
            for y in range(dim):
                img.putpixel((dim * x0 + x + gap, dim * y0 + y + gap), color)

    def save_sdk_img(self, info_dict, filename):
        '''
        This is a function used to generate a .png
        file of the solution from the dictionary.
        (Written by Xinru)

        **Parameters**

            info_dict: *dictionary*
            filename: *string*

        **Returns**

            image: *.png file*
        '''
        # Put all the numbers in the indo_dict['map']
        map = info_dict['original_map']
        for (p_x, p_y) in info_dict['final']:
            map[p_y][p_x] = info_dict['final'][(p_x, p_y)]

        # Create a new image.
        w_blocks = len(map[0])
        h_blocks = len(map)
        size = (w_blocks * 50 + 40, h_blocks * 50 + 40)

        image = Image.new("RGB", size, color=(255, 255, 255))

        # Change the color of different groups.
        for n in info_dict['groups']:
            color = tuple(np.random.choice(range(200, 256), size=3))
            for n2 in info_dict['groups'][n]:
                for x, y in info_dict['groups'][n][n2]:
                    dim = 50
                    gap = 20
                    multi_sudoku.set_color(
                        self, image, x, y, dim, gap, color
                    )

        # Draw the grid.
        draw = ImageDraw.Draw(image)
        y_i = 20
        y_f = image.height - 20
        step_size_x = int((image.width - 40) / len(map[0]))
        step_size_y = int((image.height - 40) / len(map))

        for x in range(20, image.width, step_size_x):
            line = ((x, y_i), (x, y_f))
            draw.line(line, 'black')

        x_i = 20
        x_f = image.width - 20

        for y in range(20, image.height, step_size_y):
            line = ((x_i, y), (x_f, y))
            draw.line(line, 'black')

        # Draw the numbers.
        for y, lst in enumerate(map):
            for x, i, in enumerate(map[y]):
                if i != 0:
                    w, h = draw.textsize(str(i))
                    draw.text(
                        (20 + (50 - w) / 2 + x * 50,
                            20 + (50 - h) / 2 + y * 50),
                        str(i), 'black'
                    )
        image.save(filename)

if __name__ == "__main__":
    a = multi_sudoku()
    b = a.read_sdk("multi_hard_24_0.sdk")
    c = a.load_sdk_map(b)
    d = a.sub_points(c)
    e = a.solve_sdk(c)
    print(e)
    a.save_sdk_txt(e, "multi_hard_24_0.txt")
    a.save_sdk_img(e, "multi_hard_24_0.png")
