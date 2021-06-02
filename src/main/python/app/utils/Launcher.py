import os, subprocess
from pathlib import Path

from app.config import Config

def launch(files, iwad, source_port):
    config = Config.Instance()

    wads_path = os.path.expanduser(config['PATHS']['WADS_PATH'])
    executable_path = os.path.join(source_port.dir, source_port.executable)

    files_arg_with_params = []
    savedir_arg_with_params = []
    if len(files) > 0:
        files_arg_with_params = [source_port.wad_arg, *files]

        wad_dir = os.path.dirname(os.path.abspath(files[0]))
        wad_save_dir = os.path.join(wad_dir, 'saves')
        Path(wad_save_dir).mkdir(parents=True, exist_ok=True)
        savedir_arg_with_params = [
            source_port.save_arg,
            wad_save_dir
        ]

    iwad_arg_with_params = []
    if iwad:
        iwad_arg_with_params = [source_port.iwad_arg, iwad.path]


    process_call = [
        executable_path,
        *files_arg_with_params,
        *iwad_arg_with_params,
        *savedir_arg_with_params,
    ]

    subprocess.Popen(process_call, cwd=source_port.dir)