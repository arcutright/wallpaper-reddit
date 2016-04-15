import os
import sys

from wpreddit import config, connection, download, reddit, wallpaper

runcount = 0

def run():
    try:
        config.init_config()
        # blacklist the current wallpaper if requested
        if config.blacklistcurrent:
            reddit.blacklist_current()
        # check if the program is run in a special case (save or startup)
        if config.save:
            wallpaper.save_wallpaper()
            sys.exit(0)
        if config.startup:
            connection.wait_for_connection(config.startupattempts, config.startupinterval)
        # make sure you're actually connected to reddit
        if not connection.connected("http://www.reddit.com"):
            print("ERROR: You do not appear to be connected to Reddit. Exiting")
            sys.exit(1)
        links = reddit.get_links()
        titles = links[1]
        # mass download mode
        if config.massdownload is not None and config.massdownload > 0:
            # pls fix me to grab by sub, not first n valid links across all subs
            valid_links = reddit.choose_valid(links[0], config.massdownload * len(config.subs))
            for link in valid_links:
                url = link[0]
                title = titles[link[1]]
                download.download_image_and_save(url, title)
            external_script()
        # normal operation (meant for cron jobs and such)
        else:
            valid = reddit.choose_first_valid(links[0])
            valid_url = valid[0]
            title = titles[valid[1]]
            download.download_image(valid_url, title)
            download.save_info(valid_url, title)
            wallpaper.set_wallpaper()
            if config.autosave:
                wallpaper.save_wallpaper()
            external_script()
            # repeats
            if config.repeat is not None:
                global runcount
                if runcount < config.repeat:
                    run()
                    runcount += 1
                else:
                    runcount = 0
    except KeyboardInterrupt:
        sys.exit(1)


# creates and runs the ~/.wallpaper/external.sh script
def external_script():
    if config.opsys == 'Linux':
        if not os.path.isfile(config.walldir + '/external.sh'):
            with open(config.walldir + '/external.sh', 'w') as external:
                external.write('# ! /bin/bash\n\n# You can enter custom '+
                    'commands here that will execute after the main program is finished')
            os.system('chmod +x ' + config.walldir + '/external.sh')
        os.system('bash ' + config.walldir + '/external.sh')
