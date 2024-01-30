from PIL import Image
import os
import glob
import sys

if __name__ == "__main__":
    def set_overwrite():
        '''Prompts user about file overwrite'''

        global overwrite
        overwrite_ans = ""

        while overwrite_ans.lower() not in ('y', 'n', 'yes', 'no'):
            overwrite_ans = input("Do you want to overwrite all files with the same names? (Y/N) ")

        overwrite = overwrite_ans.lower() == "y" or overwrite_ans.lower() == "yes"


    def process_file(name):
        '''Main function to process a single file'''

        file_tuple = os.path.splitext(name)
        lossless = file_tuple[1] in (".png", ".svg", ".gif", ".bmp")
        unwebp = file_tuple[1] == ".webp"
        size = os.path.getsize(name)
        out_format = "jpeg" if unwebp else "webp"
        global total_diff

        def get_pos(num):
            '''Returns 0 if input is not positive'''

            if num > 0:
                return num
            else:
                return 0

        def get_q(base):
            '''Highens lossy quality for smaller images
            
            Takes filesize, color count and resolution into consideration'''

            if lossless:
                return 100
            else:
                # Delayed until needed and counting only every other pixel for performance reasons
                colors = len({im.getpixel((x,y)) for x in range(0,im.size[0],2) for y in range(0,im.size[1],2)})
                resolution = im.size[0]*im.size[1]

                return int(base
                    + (min(5, get_pos((51200  - size)/9000)))            # 0-5% increase for sizes <50KB
                    + (min(25, get_pos((256000 - colors)/2000)))         # 0-25% increase for <256K colors
                    + (min(10, get_pos((1572864 - resolution)/130000)))) # 0-10% increase for resolutions <1.5 MP

        if not os.path.isfile(name):
            print(f"File \"{name}\" not found, skipping...")
            return

        if (not lossless and file_tuple[1] not in (".jpg", ".jpeg", ".tif", ".tiff", ".webp")):
            #print(f"Unrecognized file format ({name}), skipping...")
            return

        pre_out_name = f"{file_tuple[0]}.{out_format}"

        if os.path.isfile(pre_out_name) and not overwrite:
            print(f"\"{pre_out_name}\": File already exists, skipping...")
            return

        im = Image.open(name)
        q = get_q(55 if unwebp else 45)

        im.save(fp=f"{file_tuple[0]}.{out_format}", format=out_format, lossless=lossless, quality=q, method=6)

        diff = get_pos((size - os.path.getsize(f"{file_tuple[0]}.{out_format}"))/1024)
        total_diff += diff

        print(f"\"{name}\" output quality: {q} ({'' if lossless else 'not '}lossless)")
        if unwebp:
            print(f"Converted from WEBP to {out_format} for compatibility")
        else:
            print(f"Data saved: {int(diff)}KB")


    def get_files(args):
        '''Returns either a list of (existing) supplied files, or an entire folder if applicable'''

        files = []
        for arg in args:
            if os.path.isfile(arg):
                files.append(arg)
            elif os.path.exists(arg):
                files = glob.glob(f"{arg}/*")
                break

        return files


    total_diff = 0
    art = ''' _____     _     _   _ _ _ _____ _____ _____         
|     |_ _|_|___| |_| | | |   __| __  |  _  |___ ___ 
|  |  | | | |  _| '_| | | |   __| __ -|   __| -_|  _|
|__  _|___|_|___|_,_|_____|_____|_____|__|  |___|_|  
   |__|                                             \n'''

    files = get_files(sys.argv[1:])
    print(art)
    set_overwrite()
    print("\n")

    for file in files or glob.glob('*'):
        process_file(file)

    if total_diff:
        print(f"\nTotal storage saved: {int(total_diff)}KB\n")
    else:
        print("\nDone!\n")