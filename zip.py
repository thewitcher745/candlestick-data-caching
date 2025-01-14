import zipfile
import constants
import os


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.basename(file))


if __name__ == '__main__':
    zipf = zipfile.ZipFile(f"./cached-data/{constants.timeframe}-{constants.end_date}.zip", 'w', zipfile.ZIP_DEFLATED)
    zipdir(f'./cached-data/{constants.timeframe}-{constants.end_date}/', zipf)
    zipf.close()
