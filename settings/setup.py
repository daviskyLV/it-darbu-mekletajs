import os.path as osp
import os
import shutil

if __name__ == "__main__":
    # paths
    script_dir = osp.dirname(__file__) # absolute dir
    keywords_rel = "keywords.json"
    dotenv_rel = ".env"
    utils_rel = "../scrapers/utils"
    sites_rel = "../scrapers"
    site_folders = ["cv-lv"]

    # getting absolute paths
    dotenv_abs = osp.abspath(osp.join(script_dir, dotenv_rel))
    keywords_abs = osp.abspath(osp.join(script_dir, keywords_rel))
    site_folders_abs = []
    for sf in site_folders:
        site_folders_abs.append(osp.abspath(osp.join(script_dir, f"{sites_rel}/{sf}")))
    utils_abs = osp.abspath(osp.join(script_dir, utils_rel))
    
    # getting utils requirements
    utils_requirements = ""
    with open(osp.abspath(f"{utils_abs}/requirements.txt"), "r") as file:
        utils_requirements = file.read()
    
    # copying over settings to each site folder
    for sf in site_folders_abs:
        shutil.copyfile(dotenv_abs, f"{sf}/.env")
        shutil.copyfile(keywords_abs, f"{sf}/keywords.json")
        shutil.copytree(utils_abs, f"{sf}/utils")
        # concatenating requirements.txt
        os.remove(f"{sf}/utils/requirements.txt")
        with open(f"{sf}/requirements.txt", "a") as file:
            file.write(f"\n{utils_requirements}")
    
    print("Done setting up sites!")