import os
import cv2
from skimage.metrics import structural_similarity as ssim


def compare_images(image_a, image_b):
    # Convert the images to grayscale
    gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)

    # Compute the Structural Similarity Index (SSIM) between the two images
    (score, diff) = ssim(gray_a, gray_b, full=True)

    # return the SSIM score
    return score


# Get the current working directory
cwd = os.getcwd()
# Set a flag to indicate if the chessboard is white or not
is_white = True
# Load the image of a chessboard screenshot
screenshot_img = cv2.imread("screenshot.png")

# Convert the image to grayscale
gray = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2GRAY)

# Threshold the image to extract the chessboard
ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Find contours in the thresholded image
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Find the contour with the largest area (assuming that it is the chessboard)
max_area = 0
best_cnt = None
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > max_area:
        max_area = area
        best_cnt = cnt

# Draw the contour on the original image
cv2.drawContours(screenshot_img, [best_cnt], 0, (0, 255, 0), 3)

# Extract the chessboard from the original image using the contour
x, y, w, h = cv2.boundingRect(best_cnt)
screenshot_img = screenshot_img[y: y + h, x: x + w]
# Define number of rows and columns in a chessboard
rows = 8
cols = 8
# Calculate size of each square in a chessboard
square_size = screenshot_img.shape[1] // rows

# Loop through each square and save as separate image
extracted_squares = []

for i in range(rows):
    for j in range(cols):
        x = j * square_size
        y = i * square_size
        square = screenshot_img[y: y + square_size, x: x + square_size]
        if is_white:
            position = chr(ord("a") + j) + str(8 - i)
        else:
            position = chr(ord("h") - j) + str(i + 1)
        extracted_squares.append([position, square])

# Set the path to the directory containing the chess pieces images
directory_pieces = os.path.join(cwd, "figures")
differences = []
resized_images = {}

# Loop through the entries in the directory containing the chess pieces images
with os.scandir(directory_pieces) as entries:
    for entry in entries:
        # Read the image of a chess piece
        image_a = cv2.imread(f"{directory_pieces}\\{entry.name}")
        # Split the name of the image file to get the piece notation
        piece_notation_split = entry.name.split("_")[0]
        # Set the piece notation based on whether it is a white or black piece
        piece_notation = (
            piece_notation_split[1].upper()
            if piece_notation_split[0] == "w"
            else piece_notation_split[1]
        )
        # Store the resized chess piece image in the dictionary
        resized_images[piece_notation] = cv2.cvtColor(image_a, cv2.COLOR_BGR2RGB)
# Loop through each extracted square
for i in range(len(extracted_squares)):
    # Get the image of an extracted square
    image_b = extracted_squares[i][1]
    # Initialize variables to store the maximum value and name of a chess piece
    max_value = 0
    max_name = "m"
    # Loop through each resized chess piece image
    for name, image_a in resized_images.items():
        # Compare the resized chess piece image with the extracted square image and get the SSIM score
        value = compare_images(
            cv2.resize(image_a, (image_b.shape[1], image_b.shape[0])), image_b
        )
        if value > max_value:
            max_value = value
            max_name = name
    # Set the difference to be the name of the chess piece with the highest SSIM score
    diff = max_name
    # Append the difference to the list of differences
    differences.append(diff)

def to_fen(pieces, white) -> str:
    fen = ""
    empty_squares = 0
    for i in range(8):
        for j in range(8):
            if white:
                piece = pieces[8 * i + j]
            else:
                piece = pieces[8 * (7 - i) + j]
            if piece == "m":
                empty_squares += 1
            else:
                if empty_squares > 0:
                    fen += str(empty_squares)
                    empty_squares = 0
                fen += piece
        if empty_squares > 0:
            fen += str(empty_squares)
            empty_squares = 0
        if i < 7:
            fen += "/"
    return fen


print(to_fen(differences, is_white))