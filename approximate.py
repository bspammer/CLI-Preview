#!/usr/bin/env python
from PIL import Image
import sys
import argparse

LOW_DETAIL = " .:-=+*#%@"
HIGH_DETAIL = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
TOP_LEFT = u"\u250c"
TOP_RIGHT = u"\u2510"
BOT_LEFT = u"\u2514"
BOT_RIGHT = u"\u2518"
VERTICAL = u"\u2502"
HORIZONTAL = u"\u2500"

parser = argparse.ArgumentParser(description="Approximate images on the command line.")
parser.add_argument("filenames", type=str, nargs="+",
        help="List of files to process")
parser.add_argument("-d", "--detail", dest="detail", choices=["low", "high"],
        default="high", help="Choice of low or high detail, only relevant for non-color")
parser.add_argument("-x", "--width", dest="width", type=int, default=80,
        help="Width of output text")
parser.add_argument("-y", "--height", dest="height", type=int, default=0,
        help="Height of output text (0 for automatic scaling)")
parser.add_argument("-c", "--color", dest="color", action="store_true",
        help="Enable color output (truecolor terminals only)")
parser.add_argument("-n", "--noborder", dest="border", action="store_false",
        default=True, help="Disable border around output")
args = parser.parse_args()

if args.detail == "low":
    intensity_chrs = LOW_DETAIL
if args.detail == "high":
    intensity_chrs = HIGH_DETAIL

def to_console_color_str(r, g, b):
    return "\x1b[48;2;%d;%d;%dm \x1b[0m" % (r, g, b)

if __name__ == "__main__":
    for filename in args.filenames:
        try:
            img = Image.open(filename)
        except IOError:
            sys.stderr.write("Error: File '%s' does not exist\n" % filename)
            continue
        px = img.getdata()

        width = args.width
        height = args.height
        if height == 0:
            # Terminal characters are roughly half as wide as they are tall
            height = int((width * img.height/img.width)/2)

        if img.width < width or img.height < height:
            sys.stderr.write("Error: Image too small")
            exit()

        out_string = ""
        for y in range(height):
            out_string += VERTICAL*args.border
            for x in range(width):
                top_left_region_x = int(x*img.width/width)
                top_left_region_y = int(y*img.height/height)
                bottom_right_region_x = min(int((x+1)*img.width/width), img.width-1)
                bottom_right_region_y = min(int((y+1)*img.height/height), img.height-1)
                intensities = []
                for img_x in range(top_left_region_x, bottom_right_region_x):
                    for img_y in range(top_left_region_y, bottom_right_region_y):
                        pixel = px[img_x + img_y*img.width]
                        if args.color:
                            intensity = pixel
                        else:
                            intensity = sum(pixel)/3.
                        intensities.append(intensity)
                if args.color:
                    r_list = [i[0] for i in intensities]
                    g_list = [i[1] for i in intensities]
                    b_list = [i[2] for i in intensities]
                    r = int(min(255., sum(r_list)/len(r_list)))
                    g = int(min(255., sum(g_list)/len(g_list)))
                    b = int(min(255., sum(b_list)/len(b_list)))
                    out_string += to_console_color_str(r, g, b)
                else:
                    avg_intensity = (sum(intensities)/len(intensities))/255.
                    intensity_index = min(len(intensity_chrs)-1, int(avg_intensity*len(intensity_chrs)))
                    out_string += intensity_chrs[intensity_index]
            out_string += VERTICAL*args.border + "\n"
        out_string = (TOP_LEFT + HORIZONTAL*(width) + TOP_RIGHT + "\n")*args.border \
        + out_string \
        + (BOT_LEFT + HORIZONTAL*(width) + BOT_RIGHT)*args.border
        sys.stdout.write((out_string + "\n").encode("utf-8"))
