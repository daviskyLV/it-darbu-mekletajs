import os.path as osp
import shutil

if __name__ == "__main__":
    # paths
    script_dir = osp.dirname(__file__) # absolute dir
    keywords_rel = "keywords.json"
    database_env_rel = "database.env"
    scrapers_env_rel = "scrapers.env"
    sites_rel = "../scrapers"
    database_rel = "../database"
    site_folders = ["cv-lv"]

    # getting absolute paths
    database_env_abs = osp.abspath(osp.join(script_dir, database_env_rel))
    database_abs = osp.abspath(osp.join(script_dir, database_rel))
    scrapers_env_abs = osp.abspath(osp.join(script_dir, scrapers_env_rel))
    keywords_abs = osp.abspath(osp.join(script_dir, keywords_rel))
    site_folders_abs = []
    for sf in site_folders:
        site_folders_abs.append(osp.abspath(osp.join(script_dir, f"{sites_rel}/{sf}")))
    
    # copying over settings to each site folder
    shutil.copyfile(database_env_abs, f"{database_abs}/.env") # copying configuration for database
    for sf in site_folders_abs:
        shutil.copyfile(scrapers_env_abs, f"{sf}/.env") # have to copy in case scrapers are run separately
        shutil.copyfile(keywords_abs, f"{sf}/keywords.json")
    
    print("Done setting up sites!")