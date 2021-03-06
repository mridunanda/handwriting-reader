import numpy as np
import random

# Extract vectors from a SVG path
def get_vectors(path):
    vectors = []
    prev_point = (0, 0)
    i = 0

    # Split path on whitespace
    split = path.split()
    while(True):
        try:    
            # Set a new start point if this is a "M" command
            if split[i] == "M":
                start = (split[i + 1], split[i + 2])
                i = i + 3
            else:
                start = prev_point

            # Skip over the "L"
            i = i + 1

            # Get the second coordinate
            end = (split[i], split[i + 1])
            prev_point = end
            i = i + 2

            vectors.append((start, end))

        # If end of path, stop  
        except IndexError:
            break
        
    return vectors

# Construct a raster image represented as a matrix of pixels
def make_image(path):
    SIDE_LENGTH = 28

    # Make a 2D array to represent image
    # Start with white image, all pixels 0
    image = [[0.0 for i in range(SIDE_LENGTH)] for j in range(SIDE_LENGTH)]

    vectors = get_vectors(path)

    for vector in vectors:

        # Extract basic info
        start_x = int(vector[0][0])
        start_y = int(vector[0][1])
        end_x = int(vector[1][0])
        end_y = int(vector[1][1])

        # Switch coordinates so x always goes left to right
        if start_x > end_x:
            start_x, end_x = end_x, start_x
            start_y, end_y = end_y, start_y

        # Scale info from the 200x200 dimensions of the SVG
        # to the dimensions of the bitmap
        start_x = round(start_x / 200 * SIDE_LENGTH)
        start_y = round(start_y / 200 * SIDE_LENGTH)
        end_x = round(end_x / 200 * SIDE_LENGTH)
        end_y = round(end_y / 200 * SIDE_LENGTH)

        # Special case if vector is vertical
        if end_x - start_x == 0:
            # Run over all y between beginning and end and turn them black

            # Split up so range works properly
            if end_y > start_y:
                for y in range(start_y, end_y + 1):

                    # Gives the line width 2
                    for pm1 in {0, 1}:
                        for pm2 in {0, 1}:

                            try:
                                image[y + pm1][start_x + pm2] = 1.0

                            # If this goes off the grid, pass
                            except IndexError:
                                pass

            else:
                for y in range(end_y, start_y + 1):

                    # Gives the line width 2
                    for pm1 in {0, 1}:
                        for pm2 in {0, 1}:
                            
                            try:
                                image[y + pm1][start_x + pm2] = 1.0

                            # If this goes off the grid, pass
                            except IndexError:
                                pass

        # Normal sloped vector                        
        else:       
            slope = (end_y - start_y)/(end_x - start_x)

            # Change all the pixels the vector "touches" to black
            for x in range(start_x, end_x + 1):

                #Caluculate y using slope formula
                y = round(start_y + slope * (x - start_x))

                # Gives line width of 2
                for pm1 in {0, 1}:
                    for pm2 in {0, 1}:
                        try:
                            # Runs over all y from whatever the last one was to this y
                            # Split up so range works
                            if prev_y > y:
                                for y_pt in range(y, prev_y + 1):
                                    image[y_pt + pm1][x + pm2] = 1.0
                            else:
                                for y_pt in range(prev_y, y + 1):
                                    image[y_pt + pm1][x + pm2] = 1.0

                        # If this is first y, no previous y to come from
                        except NameError:
                            image[y + pm1][x + pm2] = 1.0

                        # Offscreen
                        except IndexError:
                            pass
                prev_y = y

    return np.array(image)

def blur(image):

    # Make a new array to fill with a new image
    new_image = []

    # Initialize this variable, comes up later
    pass_on = False

    # For each row, make a new row
    for row in image:
        new_row = []

        # For each pixel in the row, do something
        for i in range(len(row)):

            # If we have been told to make this 0.5, do it
            if pass_on:
                new_row.append(0.5)
                pass_on = False

            else:
                try:
                    # If this is a white pixel next to a black pixel
                    if (row[i + 1] == 1.0 or row[i - 1] == 1.0) and row[i] == 0.0:

                        # Randomly chose whether to make this pixel 0.5 or make the
                        # adjacent black pixel 0.5
                        flip = random.random()

                        if flip < 0.5:
                            new_row.append(0.5)

                        elif row[i + 1] == 1.0:
                            # The next pixel should be 0.5
                            pass_on = True
                            new_row.append(row[i])

                        else:
                            # The previous pixel should be changed to 0.5
                            new_row.pop()
                            new_row.append(0.5)
                            new_row.append(row[i])

                    else:
                        # If this is not a white pixel bordering a black pixel, preserve it
                        new_row.append(row[i])

                except IndexError:
                    # If this is the end of a row, preserve it
                    new_row.append(row[i])

        # Add the new row to the image we're building
        new_image.append(new_row)

    return np.array(new_image)