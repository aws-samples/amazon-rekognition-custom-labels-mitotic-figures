import os
import urllib.request
from tqdm.notebook import tqdm

def download_dataset():
    downloadableFiles = {'WSI/deb768e5efb9d1dcbc13.svs' : #18
                             'https://ndownloader.figshare.com/files/22407414?private_link=be072bf30fd3f63b03cc',
                         'WSI/d37ab62158945f22deed.svs' : #19
                             'https://ndownloader.figshare.com/files/22585835?private_link=be072bf30fd3f63b03cc',
                         'WSI/022857018aa597374b6c.svs': #1,
                             'https://ndownloader.figshare.com/files/22407537?private_link=be072bf30fd3f63b03cc',
                         'WSI/69a02453620ade0edefd.svs': #2
                              'https://ndownloader.figshare.com/files/22407411?private_link=be072bf30fd3f63b03cc', 
                         'WSI/a8773be388e12df89edd.svs': #3
                              'https://ndownloader.figshare.com/files/22407540?private_link=be072bf30fd3f63b03cc',
                         'WSI/c4b95da36e32993289cb.svs': #4
                              'https://ndownloader.figshare.com/files/22407552?private_link=be072bf30fd3f63b03cc',
                         'WSI/3d3d04eca056556b0b26.svs': #5
                              'https://ndownloader.figshare.com/files/22407585?private_link=be072bf30fd3f63b03cc',
                         'WSI/d0423ef9a648bb66a763.svs': #6
                              'https://ndownloader.figshare.com/files/22407624?private_link=be072bf30fd3f63b03cc',
                         'WSI/50cf88e9a33df0c0c8f9.svs': #7
                              'https://ndownloader.figshare.com/files/22407531?private_link=be072bf30fd3f63b03cc',
                         'WSI/084383c18b9060880e82.svs': #8
                             'https://ndownloader.figshare.com/files/22407486?private_link=be072bf30fd3f63b03cc',
                         'WSI/4eee7b944ad5e46c60ce.svs': #9
                             'https://ndownloader.figshare.com/files/22407528?private_link=be072bf30fd3f63b03cc',
                         'WSI/2191a7aa287ce1d5dbc0.svs' : #10
                             'https://ndownloader.figshare.com/files/22407525?private_link=be072bf30fd3f63b03cc',
                         'WSI/13528f1921d4f1f15511.svs' : #11
                             'https://ndownloader.figshare.com/files/22407519?private_link=be072bf30fd3f63b03cc',
                         'WSI/2d56d1902ca533a5b509.svs' : #12
                             'https://ndownloader.figshare.com/files/22407522?private_link=be072bf30fd3f63b03cc',
                         'WSI/460906c0b1fe17ea5354.svs' : #13
                             'https://ndownloader.figshare.com/files/22407447?private_link=be072bf30fd3f63b03cc',
                         'WSI/da18e7b9846e9d38034c.svs' : #14
                             'https://ndownloader.figshare.com/files/22407453?private_link=be072bf30fd3f63b03cc',
                         'WSI/72c93e042d0171a61012.svs' : #15
                             'https://ndownloader.figshare.com/files/22407456?private_link=be072bf30fd3f63b03cc',
                         'WSI/b1bdee8e5e3372174619.svs' : #16
                             'https://ndownloader.figshare.com/files/22407423?private_link=be072bf30fd3f63b03cc',
                         'WSI/fa4959e484beec77543b.svs' : #17
                             'https://ndownloader.figshare.com/files/22407459?private_link=be072bf30fd3f63b03cc',
                         'WSI/e09512d530d933e436d5.svs' : #20
                             'https://ndownloader.figshare.com/files/22407465?private_link=be072bf30fd3f63b03cc',
                         'WSI/d7a8af121d7d4f3fbf01.svs' : #21
                             'https://ndownloader.figshare.com/files/22407477?private_link=be072bf30fd3f63b03cc',
                        }
    
    os.makedirs('WSI', exist_ok=True)
    tqdm.write('Downloading all files from figshare (37 GB download)')

    for fname in tqdm(list(downloadableFiles.keys())):
        urllib.request.urlretrieve(downloadableFiles[fname],fname)

                    
