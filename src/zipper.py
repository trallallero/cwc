"""Module to un/zip the project in a temporary folder.
Needed to save/open a crossword project.
"""

import tempfile
import zipfile
import os

class Zip:
    """Class to un/zip the project in a temporary folder"""

    __tdir  = tempfile.TemporaryDirectory()
    tempdir = __tdir.name

    @staticmethod
    def get_temp_dir():
        return Zip.tempdir

    @staticmethod
    def zip_project(directory, zipname):
        with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as out_zip_file:
            rootdir = os.path.basename(directory)
            for dirpath, _, filenames in os.walk(directory):
                for fname in filenames:
                    filepath   = os.path.join(dirpath, fname)
                    parentpath = os.path.relpath(filepath, directory)
                    arcname    = os.path.join(rootdir, parentpath)
                    out_zip_file.write(filepath, arcname)

    @staticmethod
    def unzip_project(zipname):
        with zipfile.ZipFile(zipname, 'r') as zipobj:
            zipobj.extractall(Zip.tempdir)
        return os.path.join(Zip.tempdir, os.path.splitext(os.path.basename(zipname))[0])


############# TESTS #############

if __name__ == "__main__":
    try:
        from cwc_globals import GlobalData
        filename = os.path.join(GlobalData.ROOT_DIR, 'test.cwc')
        dirname  = os.path.splitext(filename)[0]

        Zip.zip_project(directory=dirname, zipname=filename)
        Zip.unzip_project(zipname=filename)
    except Exception as e:
        print(e)
