import PySimpleGUI as sg
from os import path, makedirs

sg.theme("LightBlue3")

filename = False

layout = [  [sg.Text('Click Browse to select ESO Log file to split and press Split button.')],
            [sg.Text('Log file'), sg.Input(size=(56,1), enable_events=True,key="-LOGFILE-"), sg.FileBrowse(file_types=(("Log Files", "*.log"),))],
            [sg.Text('',size=(46,1),key = "-OUTPUT-")],
            [sg.ProgressBar(100, orientation='h', size=(46, 20), key='-PROGBAR-')],
            [sg.Output(size=(70,20))],
            [sg.Button('Split',size=(10,1))]
         ]

window = sg.Window('Seaunicorns ESO Log Splitter', layout,finalize=True)

try:
    if path.getsize("Splitlog.config") > 0:
        with open("Splitlog.config", 'r') as pathfile:
            for line in pathfile:
                filename = line
        window['-LOGFILE-'].update(filename)
        
except OSError as e:
    filename = False

while True:             
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
        
    if event == "-LOGFILE-":
        filename = values["-LOGFILE-"]
        with open("Splitlog.config", 'w') as pathfile:
            pathfile.write(filename)
        
    if event == "Split" and not filename:
        window['-OUTPUT-'].update("Please select ESO Log file to split first (>**)>")
        
    if event == "Split" and filename:
        if not path.exists('To upload'):
            makedirs('To upload')
        try:
            filesize = path.getsize(filename)
            window['-OUTPUT-'].update("I am working...")

            # First pass: collect BEGIN_LOG and all ABILITY_INFO/EFFECT_INFO lines
            print("First pass: collecting ability definitions...")
            begin_log_line = ''
            ability_lines = []
            with open(filename, encoding='UTF-8') as fin:
                for line in fin:
                    if 'BEGIN_LOG' in line:
                        begin_log_line = line
                    elif 'ABILITY_INFO' in line or 'EFFECT_INFO' in line:
                        ability_lines.append(line)
            print("  Found %d ability/effect definitions." % len(ability_lines))

            # Second pass: split into zone files
            print("Second pass: splitting log...")
            with open(filename, encoding='UTF-8') as fin:
                n = 0
                fout = open("To upload\\initial.log", "wb")
                ln = 0
                in_run = False
                for line in fin:
                    ln += 1

                    if 'ZONE_CHANGED' in line:
                        zone = line.split(",")[3].strip('"')
                        difficulty = line.split(",")[4].strip().strip('"').strip()
                        if in_run:
                            fout.close()
                        n += 1
                        safe_zone = zone.replace(' ', '_').replace('/', '-')
                        fname = "To upload\\%d %s %s.log" % (n, safe_zone, difficulty)
                        fout = open(fname, "wb")
                        in_run = True
                        print("\n  %d - %s (%s)" % (n, zone, difficulty))
                        progress = round(ln * 17000 / filesize)
                        window['-PROGBAR-'].update_bar(progress)
                        # Write BEGIN_LOG + all ability definitions + this zone line
                        fout.write(begin_log_line.encode("utf-8"))
                        for al in ability_lines:
                            fout.write(al.encode("utf-8"))
                        fout.write(line.encode("utf-8"))

                    elif in_run:
                        # Skip duplicate ABILITY_INFO/EFFECT_INFO in body (already in header)
                        if 'ABILITY_INFO' not in line and 'EFFECT_INFO' not in line:
                            fout.write(line.encode("utf-8"))

                fout.close()
            window['-OUTPUT-'].update("Yey, I have finished :3")
            window['-PROGBAR-'].update_bar(100)
            print("\n    You can find listed log files in the \"To upload\" directory.\n    Please do not forget to delete the original log file (**,)")
            
        except Exception as e:
            window['-OUTPUT-'].update("Log file does not exist or something else went wrong :(")
            print("Error:", e)

window.close()
