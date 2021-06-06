import sys

from core.base.Model import Model, singularizable, singularize

from app.workers.DWApiWorker import api_worker_wrapper, DWApiMethod
from app.workers.DownloadWorker import download_worker_wrapper
from app.workers.ArchiveExtractorWorker import archive_extractor_worker_wrapper
from app.workers.WadLoaderWorker import wad_loader_worker_wrapper
from app.workers.WadImporterWorker import wad_importer_worker_wrapper
from app.workers.WadRemoverWorker import wad_remover_worker_wrapper
from app.workers.WadSaverWorker import wad_saver_worker_wrapper
from app.schemas.Wad import Wad

@singularizable
class Wads(Model):
    LOADED = 'WADS_LOADED'
    LOADED_ALL = 'WADS_LOADED_ALL'
    SELECTED = 'WADS_SELECT'
    CREATE = 'WADS_CREATE'
    IMPORT = 'WADS_IMPORT'
    REMOVE = 'WADS_REMOVE'
    DOWNLOAD_PROGRESS = 'WADS_DOWNLOAD_PROGRESS'
    DOWNLOAD_FINISHED = 'WADS_DOWNLOAD_FINISHED'
    RANDOM = 'WADS_RANDOM'
    DETAIL = 'WADS_DETAIL'
    SEARCH = 'WADS_SEARCH'

    def __init__(self):
        Model.__init__(self, schema=Wad, saver=wad_saver_worker_wrapper)
        self.wad_dir_files = []
        self.current_idgames_wad_id = None
        self.load_ordered_files = []
        wad_loader_worker_wrapper([self.loaded], [self.loaded_all])

    def loaded(self, obj):
        id = self.create(**obj)
        self.broadcast((self.LOADED, self.find(id)))

    def loaded_all(self):
        self.broadcast((self.LOADED_ALL, None))

    def select_wad(self, id):
        selected_wad = self.find(id)
        self.load_ordered_files = selected_wad.file_paths

        self.broadcast((self.SELECTED, selected_wad))

    def extract_archive(self, file_path, should_remove_archive=False, item={}, detail_type=None):
        def handle_import_wad(wad_dir):
            self.import_wad(wad_dir, item, detail_type)

        archive_extractor_worker_wrapper(
            file_path,
            should_remove_archive,
            [handle_import_wad]
        )

    def import_wad(self, wad_dir, item={}, detail_type=None):
        def on_import(wad):
            id = self.create(**dict(list(wad.items()) + list(item.items())))
            self.save(id)
            self.broadcast((self.CREATE, id))
            category_name = 'idgames/download'
            if detail_type == self.RANDOM:
                category_name = 'idgames/random'
            elif detail_type != None:
                category_name = detail_type
            self.broadcast((self.IMPORT, (id, category_name)))

        wad_importer_worker_wrapper(wad_dir, [], [on_import])

    def idgames_download(self, item, mirror=None, detail_type=None):
        id = item['id']
        def handle_download_progress(*args):
            self.broadcast((self.DOWNLOAD_PROGRESS, (id, args)))
        def handle_download_finished():
            self.broadcast((self.DOWNLOAD_FINISHED, id))
        def handle_extract_archive(file_path):
            self.extract_archive(file_path, True, item, detail_type)

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
            self.broadcast((self.RANDOM, result))

        api_worker_wrapper(
            DWApiMethod.RANDOM,
            [handle_get_random]
        )

    def idgames_get(self, wad_id):
        def handle_idgames_get_detail(result):
            self.broadcast((self.DETAIL, result))

        api_worker_wrapper(
            DWApiMethod.GET,
            [handle_idgames_get_detail],
            wad_id,
            'id'
        )    

    def idgames_search(self, text, search_by):
        def handle_idgames_search(result):
            self.broadcast((self.SEARCH, result))

        api_worker_wrapper(
            DWApiMethod.SEARCH,
            [handle_idgames_search],
            text,
            search_by
        )

    @singularize
    def remove(self, id):
        wad = self.delete(id)
        def on_remove():
            self.broadcast((self.REMOVE, wad))
        wad_remover_worker_wrapper(wad.path, [], [on_remove])

    def set_load_order(self, files):
        self.load_ordered_files = files

    @singularize
    def add_file_path_to_paths(self, id, file_path):
        wad = self.find(id)
        paths = [*wad.file_paths, file_path]
        self.update(id, file_paths=paths)
        self.save(id)

    @singularize
    def remove_file_path_from_paths(self, id, file_path):
        wad = self.find(id)
        paths = [fp for fp in wad.file_paths if fp != file_path]
        self.update(id, file_paths=paths)
        self.save(id)

