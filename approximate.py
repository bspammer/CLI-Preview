from PIL import Image
import argparse

LOW_DETAIL = " .:-=+*#%@"
HIGH_DETAIL = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

parser = argparse.ArgumentParser(description="Approximate images on the command line.")
parser.add_argument("filenames", type=str, nargs="+",
        help="List of files to process")
parser.add_argument("-d", "--detail", dest="detail", choices=["low", "high"],
        default="high", help="Choice of low or high detail")
parser.add_argument("-x", "--width", dest="width", type=int, default=80,
        help="Width of output text")
parser.add_argument("-y", "--height", dest="height", type=int, default=0,
        help="Height of output text (0 for automatic scaling)")

args = parser.parse_args()

if args.detail == "low":
    intensity_chrs = LOW_DETAIL
if args.detail == "high":
    intensity_chrs = HIGH_DETAIL

for filename in args.filenames:
    img = Image.open(filename)
    px = img.load()

    width = args.width
    height = args.height
    if height == 0:
        # Terminal characters are roughly half as wide as they are tall
        height = int((width * img.height/img.width)/2)

    if img.width < width or img.height < height:
        print("Image too small")
        exit()

    out_string = ""
    for y in range(height):
        out_string += "|"
        for x in range(width):
            top_left_region_x = int(x*img.width/width)
            top_left_region_y = int(y*img.height/height)
            bottom_right_region_x = min(int((x+1)*img.width/width), img.width-1)
            bottom_right_region_y = min(int((y+1)*img.height/height), img.height-1)
            intensities = []
            for img_x in range(top_left_region_x, bottom_right_region_x):
                for img_y in range(top_left_region_y, bottom_right_region_y):
                    pixel = px[img_x, img_y]
                    intensity = sum(pixel)/3.
                    intensities.append(intensity)
            avg_intensity = (sum(intensities)/len(intensities))/255.
            out_string += intensity_chrs[int(avg_intensity*len(intensity_chrs))]
        out_string += "|\n"
    out_string = "|" + "-"*(width) + "|\n" + out_string + "|" + "-"*(width) + "|"
    print(out_string)
