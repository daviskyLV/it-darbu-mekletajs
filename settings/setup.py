import os.path as osp
import shutil

if __name__ == "__main__":
    # paths
    script_dir = osp.dirname(__file__) # absolute dir
    keywords_rel = "keywords.json"
    dotenv_rel = ".env"
    sites_rel = "../scrapers"
    site_folders = ["cv-lv"]

    # getting absolute paths
    dotenv_abs = osp.abspath(osp.join(script_dir, dotenv_rel))
    keywords_abs = osp.abspath(osp.join(script_dir, keywords_rel))
    site_folders_abs = []
    for sf in site_folders:
        site_folders_abs.append(osp.abspath(osp.join(script_dir, f"{sites_rel}/{sf}")))
    
    # copying over settings to each site folder
    for sf in site_folders_abs:
        shutil.copyfile(dotenv_abs, f"{sf}/.env") # have to copy in case scrapers are run separately
        shutil.copyfile(keywords_abs, f"{sf}/keywords.json")
    
    print("Done setting up sites!")