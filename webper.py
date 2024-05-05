from PIL import Image
import os
import glob
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilenames

if __name__ == "__main__":
    def log(*content):
        '''Console logs (only for CLI)'''
        if cli_logs:
            for line in content:
                print(line)

    def set_overwrite():
        '''Prompts user about file overwrite'''

        global overwrite
        overwrite_ans = ""

        while overwrite_ans.lower() not in ('y', 'n', 'yes', 'no'):
            overwrite_ans = input("Allow overwriting ALL files with the same names? (Y/N) ")

        overwrite = overwrite_ans.lower() == "y" or overwrite_ans.lower() == "yes"


    def process_file(name, quality_scale=0):
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
            log(f"File \"{name}\" not found, skipping...")
            return

        if (not lossless and file_tuple[1] not in (".jpg", ".jpeg", ".tif", ".tiff", ".webp")):
            log(f"Unrecognized file format ({name}), skipping...")
            return

        pre_out_name = f"{file_tuple[0]}.{out_format}"

        if os.path.isfile(pre_out_name) and not overwrite:
            log(f"\"{pre_out_name}\": File already exists, skipping...")
            return

        im = Image.open(name)
        q = get_q((55 if unwebp else 45) + quality_scale)

        im.save(fp=f"{file_tuple[0]}.{out_format}", format=out_format, lossless=lossless, quality=q, method=6)

        diff = get_pos((size - os.path.getsize(f"{file_tuple[0]}.{out_format}"))/1024)
        total_diff += diff

        log(f"\"{name}\" output quality: {q} ({'' if lossless else 'not '}lossless)")
        if unwebp:
            log(f"Converted from WEBP to {out_format} for compatibility")
        else:
            log(f"Data saved: {int(diff)}KB")

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
    
    def run_gui():
        '''Runs Tk-based GUI'''

        # Initialize everything
        window = tk.Tk()
        window.wm_title("QuickWEBPer GUI")
        window.iconbitmap("icon.ico")
        btn_var = tk.IntVar()
        scl_var = tk.IntVar()
        status_var = tk.StringVar()
        status_var.set("Idle")
        window.resizable(width=False, height=False)
        padding = 5
        intro_frame = tk.Frame()
        intro_frame.pack()
        main_frame = tk.Frame()
        main_frame.pack()
        out_frame = tk.Frame()
        out_frame.pack(fill=tk.X)
        global gui_files
        gui_files = None

        # Create widgets
        lbl_intro = ttk.Label(master=intro_frame, text="Welcome to QuickWEBPer GUI!")
        btn_open = ttk.Button(master=intro_frame, text="Select file(s)")
        lbl_quality = ttk.Label(master=main_frame, text="Quality bias:")
        scl_quality = ttk.Scale(master=main_frame, from_=-5, to=5, value=5, variable=scl_var)
        lbl_lowq = ttk.Label(master=main_frame, text="-")
        lbl_highq = ttk.Label(master=main_frame, text="+")
        btn_overwrite = tk.Checkbutton(master=intro_frame, text="Overwrite all files with the same names", variable=btn_var)
        btn_run = ttk.Button(state="disabled", master=out_frame, text="Start")
        lbl_status = ttk.Label(master=out_frame, textvariable=status_var)
        btn_overwrite.deselect()

        # Render widgets
        lbl_intro.pack(padx=padding, pady=padding)
        btn_open.pack(padx=padding, pady=padding)
        lbl_quality.grid(row=0, column=1, sticky="n")
        scl_quality.grid(row=1, column=1, padx=padding, pady=padding)
        lbl_lowq.grid(row=1, column=0)
        lbl_highq.grid(row=1, column=2)
        btn_overwrite.pack(padx=padding, pady=padding)
        btn_run.pack(padx=padding, pady=padding)
        lbl_status.pack(side=tk.LEFT, padx=padding, pady=padding)

        # Bindings and routines
        def get_filename(*args):
            '''Get files from GUI button'''
            global gui_files
            gui_files = askopenfilenames()
            if gui_files:
                btn_run["state"] = "normal"

        def set_overwrite(*args):
            global overwrite
            overwrite = not btn_var.get()

        def process_gui(*args):
            global gui_files
            if gui_files is not None:
                status_var.set("Processing...")
                window.update()
                for file in gui_files:
                    process_file(file, int(scl_var.get()))
            status_var.set("Done!")

        btn_open.bind("<Button-1>", get_filename)
        btn_overwrite.bind("<Button-1>", set_overwrite)
        btn_run.bind("<Button-1>", process_gui)
        global overwrite
        overwrite = False

        window.mainloop()

    total_diff = 0
    art = ''' _____     _     _   _ _ _ _____ _____ _____         
|     |_ _|_|___| |_| | | |   __| __  |  _  |___ ___ 
|  |  | | | |  _| '_| | | |   __| __ -|   __| -_|  _|
|__  _|___|_|___|_,_|_____|_____|_____|__|  |___|_|  
   |__|                                             \n'''
    cli_logs = False
    files = get_files(sys.argv[1:])

    if len(files):
        cli_logs = True

        log(art, "\nWelcome to QuickWEBPer CLI!\n")
        set_overwrite()
        log("\n")

        for file in files:
            process_file(file)

        if total_diff:
            log(f"\nTotal storage saved: {int(total_diff)}KB\n")
        else:
            log("\nDone!\n")
    else:
        run_gui()