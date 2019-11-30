'''
'''


class standard_sudoku():

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
        file["numbers"] = number
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
                for y in line.strip():
                    if y != " ":
                        lst.append(y)
                map.append(lst)
        for y, row in enumerate(map):
            for x, z in enumerate(row):
                file[z] = []
        for y, row in enumerate(map):
            for x, z in enumerate(row):
                file[z].append((x + 1, y + 1))
        # Close the file
        f.close()
        return file

    def load_sdk_map(self):
        pass

    def sub_points(self):
        pass

    def solve_sdk(self):
        pass

    def show_solution(self):
        pass


if __name__ == "__main__":
    a = standard_sudoku()
    b = a.read_sdk("standard_hard_8_0.sdk")
    print(b)
