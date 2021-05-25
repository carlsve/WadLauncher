import os, sys, json, shutil

from core.base.Model import Model

from app.config import Config
from app.workers.DWApiWorker import api_worker_wrapper, DWApiMethod
from app.workers.DownloadWorker import download_worker_wrapper
from app.workers.ArchiveExtractorWorker import archive_extractor_worker_wrapper
from app.workers.WadLoaderWorker import wad_loader_worker_wrapper

def save_wad(item):
    metadata_file_path = os.path.join(item['path'], 'metadata.json')
    with open(metadata_file_path, 'w+', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=4)

def search_wad_dir(dir):
    file_paths = []
    for (root, _, files) in os.walk(dir):
        file_paths.extend(
            [os.path.join(root, file) for file in files if is_mod(file)]
        )
    return file_paths

def load_wad(dir):
    loaded_wad = {
        'name': os.path.basename(dir),
        'path': dir,
        'file_paths': search_wad_dir(dir)
    }
    if 'metadata.json' in os.listdir(dir):
        with open(os.path.join(dir, 'metadata.json'), 'r') as json_file:
            loaded_wad.update(json.load(json_file))
    try:
        loaded_wad.update(file_path=loaded_wad['file_paths'][0])
    except IndexError:
        loaded_wad.update(file_path=None, error='No mod file found (.wad or .pk3)')
    return loaded_wad

class Wads(Model):
    WADS_LOADED = 'WADS_LOADED'
    WADS_LOADED_ALL = 'WADS_LOADED_ALL'
    WADS_SELECTED = 'SELECT_WAD'
    WADS_CREATED = 'CREATE_WAD'
    WADS_DOWNLOAD_PROGRESS = 'DOWNLOAD_PROGRESS'
    WADS_DOWNLOAD_FINISHED = 'DOWNLOAD_FINISHED'
    WADS_REMOVE = 'REMOVE_WAD'

    def __init__(self):
        Model.__init__(self, saver=save_wad)
        self.wad_dir_files = []
        self.current_idgames_wad_id = None
        self.load_ordered_files = []
        wad_loader_worker_wrapper([self.wad_loaded], [self.wad_loaded_all])

    def wad_loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.WADS_LOADED, self.find(id)))

    def wad_loaded_all(self):
        self.broadcast((self.WADS_LOADED_ALL, None))

    def select_wad(self, id):
        selected_wad = self.find(id)
        self.load_ordered_files = selected_wad['file_paths']

        self.broadcast((self.WADS_SELECTED, selected_wad))

    def extract_archive(self, file_path, should_remove_archive=False, item={}):
        def handle_import_wad(wad_dir):
            self.import_wad(wad_dir, item)

        archive_extractor_worker_wrapper(
            file_path,
            should_remove_archive,
            [handle_import_wad]
        )

    def import_wad(self, wad_dir, item={}):
        id = self.create(**load_wad(wad_dir), **item)
        self.save(id)
        self.broadcast((WADS_CREATED, id))

    def idgames_download(self, item, mirror=None):
        id = item['id']
        def handle_download_progress(*args):
            self.broadcast(('DOWNLOAD_PROGRESS', (id, args)))
        def handle_download_finished():
            self.broadcast(('DOWNLOAD_FINISHED', id))
        def handle_extract_archive(file_path):
            self.extract_archive(file_path, True, item)

        download_worker_wrapper(
            item,
            [handle_download_progress],
            [
                handle_download_finished,
                handle_extract_archive
            ],
            mirror
        )

    def idgames_random(self):
        def handle_get_random(result):
            self.broadcast(('RANDOM_WAD', result))

        api_worker_wrapper(
            DWApiMethod.RANDOM,
            [handle_get_random]
        )

    def idgames_get(self, wad_id):
        def handle_idgames_get_detail(result):
            self.broadcast(('DETAIL_WAD', result))

        api_worker_wrapper(
            DWApiMethod.GET,
            [handle_idgames_get_detail],
            wad_id,
            'id'
        )    

    def idgames_search(self, text, search_by):
        def handle_idgames_search(result):
            self.broadcast(('SEARCH_WADS', result))

        api_worker_wrapper(
            DWApiMethod.SEARCH,
            [handle_idgames_search],
            text,
            search_by
        )

    def remove(self, id):
        wad = self.delete(id)
        self.broadcast((self.WADS_REMOVE, wad))
        # shutil.rmtree(wad['path'])

    def set_load_order(self, files):
        self.load_ordered_files = files
    
    def add_file_path_to_paths(self, id, file_path):
        wad = self.find(id)
        paths = [*wad['file_paths'], file_path]
        self.update(id, file_paths=paths)
        self.save(id)
    
    def remove_file_path_from_paths(self, id, file_path):
        wad = self.find(id)
        paths = [fp for fp in wad['file_paths'] if fp != file_path]
        self.update(id, file_paths=paths)
        self.save(id)

sys.modules[__name__] = Wads()