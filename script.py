import os
import zipfile
import tarfile
import time
import httplib2

from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaFileUpload
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
SCOPES = "https://www.googleapis.com/auth/drive"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Quickstart'

#Define Time
T = time.time()

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    print(credential_dir)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print ('Storing credentials to ' + credential_path)
    return credentials

# define the function to split the file into smaller chunks
def splitFile(inputFile,chunkSize):
    """ Split File """
    fname = inputFile.replace('\\', '/')
    fname = fname.split('/')[-1]
    chunkNames = []
    f1 = open(inputFile, 'rb')
    i = 0
    
    # Optimizing memory use
    for ch in readInChunks(f1, chunkSize):
        fn1 = "%s%s" % (fname,i)
        chunkNames.append(fn1)
        f = open(fn1, 'wb')
        f.write(ch)
        f.close()
        i += 1
    f1.close()
    return i

#define the function to join the chunks of files into a single file

def joinFiles(fileName,noOfChunks,chunkSize):

    dataList = []
    for i in range(0,noOfChunks,1):
        chunkNum=i * chunkSize
        chunkName = fileName+'%s'%chunkNum
        f = open(chunkName, 'rb')
        dataList.append(f.read())
        f.close()
    for data in dataList:
        f2 = open(fileName, 'wb')
        f2.write(data)
        f2.close()

def zipdir(path, ziph):
    #Black list file and folder
    blacklist_folder = ['/plugins/dynmap/web', '/BuildData', '/src', '/CraftBukkit', '/apache-maven-3.2.5'\
                ,'/Spigot', '/Bukkit', '/work']
    blacklist_file = ['craftbukkit-1.8.7.jar']
    for root, dirs, files in os.walk(path):
        c = False
        for bl in blacklist_folder:
            if path + bl in root:
                c = True
                break
        if c:
            continue
        print root, "Files list ..."
        
        for file in files:
            if file in blacklist_file:
                break
            print root,file
            #print file
            ziph.write(os.path.join(root, file))
        print "-----------------------------------"

def readInChunks(fileObj, chunkSize=2048):
    """
    Lazy function to read a file piece by piece.
    Default chunk size: 2kB.
    """
    while True:
        data = fileObj.read(chunkSize)
        if not data:
            break
        yield data


def tardir(path, ziph):
    #Black list file and folder
    blacklist_folder = ['/plugins/dynmap/web', '/BuildData', '/src', '/CraftBukkit', '/apache-maven-3.2.5'\
                ,'/Spigot', '/Bukkit', '/work']
    blacklist_file = ['craftbukkit-1.8.7.jar']
    for root, dirs, files in os.walk(path):
        c = False
        for bl in blacklist_folder:
            if path + bl in root:
                c = True
                break
        if c:
            continue
        print root, "Files list ..."
        
        for file in files:
            if file in blacklist_file:
                break
            print root,file
            #print file
            ziph.add(os.path.join(root, file))
        print "-----------------------------------"
        
def upload_gdrive(numchunk):
    """ Upload Files to Google drive
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    for i in range(numchunk):
        media_body = MediaFileUpload("backup%d.tar.gz%d" % (T, i), mimetype = "application/rar")
        body = {
        'title': "backup%d.tar.gz%d" % (T, i),
        'description': "Backup world",
        'mimeType': "application/rar",
          }
        # Upload to folder...
        # body['parents'] = [{'id': ''}]
        file_ = service.files().insert(
            body=body,
            media_body=media_body).execute()

    results = service.files().list(maxResults=numchunk).execute()
    items = results.get('items', [])
    if not items:
        print( 'No files found.')
    else:
        print ('Files:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))

if __name__ == '__main__':

    # If you want .zip file uncomment this
    #zipf = zipfile.ZipFile('backup%d.zip' % t, 'w',allowZip64=True)
    #zipdir('/home/mc/mainsv', zipf)
    #zipf.close()
    
    tar = tarfile.open('backup%d.tar.gz' % T, 'w:gz')
    
    tardir('/path/to/minecraft/folder', tar)
    tar.close()

    # Split files for upload to gdrive
    #numchunk = splitFile('backup%d.tar.gz' % T, 100000000)
    
    # Upload to gdrive
    #upload_gdrive(numchunk)

