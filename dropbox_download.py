# A very simple Dropbox downloader
import os
import StringIO
import dropbox

_DROPBOX_API_KEY = 'Q-y6h-JIuCAAAAAAAAAATb4TMN4JT15PZrsXvFcuBwyb5MxM54OgAmErQu5K4nYr'

# init dropbox
dbx = dropbox.Dropbox(_DROPBOX_API_KEY)

def list_folder(folder):
    """List a folder.
    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    folder = folder.rstrip('/')
    try:
        res = dbx.files_list_folder(folder)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', folder, '-- assumped empty:', err)
        return {}
    else:
        # sort by modified date
        return sorted(res.entries, key=lambda entry: entry.server_modified)

        """rv = {}
        for entry in entries:
            rv[entry.name] = entry
        return rv"""

def download(folder, name):
    """Download a file.
    Return the bytes of the file, or None if it doesn't exist.
    """
    try:
        md, res = dbx.files_download(folder.rstrip('/') + '/' + name)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None
    data = StringIO.StringIO()
    data.write(res.content)
    #print(len(data), 'bytes; md:', md)
    return data
