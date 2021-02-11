import os
from unittest.mock import MagicMock

import subprocess
from pathlib import Path
from app.config import Config

from app.utils.Launcher import launch

mock_Instance = MagicMock(return_value={
    'PATHS': {
        'WADS_PATH': '~/.wadlauncher/wads'
    }
})
mock_Popen = MagicMock()
mock_mkdir = MagicMock()

mock_files = [
    '~/.wadlauncher/wads/sunder/sunder.wad',
    '~/.wadlauncher/wads/sunder/Guncaster.pk3'
]
mock_file = mock_files[0]
mock_iwad = { 'path': '~/.iwads/doom2.wad' }
mock_source_port = {
    'dir': '~/.sourceports/gzdoom',
    'executable': 'gzdoom',
    'wad_arg': '-file',
    'iwad_arg': '-iwad',
    'save_arg': '-savedir'
}

def test_happy_path(monkeypatch):
    monkeypatch.setattr(Config, 'Instance', mock_Instance)
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)
    monkeypatch.setattr(Path, 'mkdir', mock_mkdir)

    # Assert multiple files works
    launch(mock_files, mock_iwad, mock_source_port)
    mock_Instance.assert_called()
    mock_mkdir.assert_called()

    process_call = [
        os.path.join(mock_source_port['dir'], mock_source_port['executable']),
        '-file',
        '~/.wadlauncher/wads/sunder/sunder.wad',
        '~/.wadlauncher/wads/sunder/Guncaster.pk3',
        '-iwad',
        '~/.iwads/doom2.wad',
        '-savedir',
        os.path.join(os.path.dirname(os.path.abspath(mock_files[0])), 'saves')
    ]

    mock_Popen.assert_called_with(process_call, cwd='~/.sourceports/gzdoom')

    # Assert single file works
    launch([mock_file], mock_iwad, mock_source_port)
    process_call = [
        os.path.join(mock_source_port['dir'], mock_source_port['executable']),
        '-file',
        '~/.wadlauncher/wads/sunder/sunder.wad',
        '-iwad',
        '~/.iwads/doom2.wad',
        '-savedir',
        os.path.join(os.path.dirname(os.path.abspath(mock_files[0])), 'saves')
    ]
    mock_Popen.assert_called_with(process_call, cwd='~/.sourceports/gzdoom')

def test_no_files(monkeypatch):
    monkeypatch.setattr(Config, 'Instance', mock_Instance)
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)
    monkeypatch.setattr(Path, 'mkdir', mock_mkdir)

    launch([], mock_iwad, mock_source_port)

    process_call = [
        os.path.join(mock_source_port['dir'], mock_source_port['executable']),
        '-iwad',
        '~/.iwads/doom2.wad'
    ]
    mock_Popen.assert_called_with(process_call, cwd='~/.sourceports/gzdoom')

def test_no_iwad(monkeypatch):
    monkeypatch.setattr(Config, 'Instance', mock_Instance)
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)
    monkeypatch.setattr(Path, 'mkdir', mock_mkdir)

    launch(mock_files, None, mock_source_port)

    process_call = [
        os.path.join(mock_source_port['dir'], mock_source_port['executable']),
        '-file',
        '~/.wadlauncher/wads/sunder/sunder.wad',
        '~/.wadlauncher/wads/sunder/Guncaster.pk3',
        '-savedir',
        os.path.join(os.path.dirname(os.path.abspath(mock_files[0])), 'saves')
    ]
    mock_Popen.assert_called_with(process_call, cwd='~/.sourceports/gzdoom')
