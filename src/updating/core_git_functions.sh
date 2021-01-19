#!/bin/bash

# series of functions for executing git commands and determining success
# all functions check success of command, and return true or false depending on success of execution. 
# they also return the output from git, which can be saved as an advanced log/feedback for user

### SYNTAX GUIDE

## Use variables: platform, easycut, version_manager to specify which repo the function should action in


### REPO PATHS

home_dir="/home/pi/"
easycut_path="${home_dir}easycut-smartbench/"
platform_path="${home_dir}console-raspi3b-plus-platform/"
version_manager_path="${home_dir}smartbench-version-manager/"

go_to_dir(){

	if [[ $1 = "platform" ]]; then
		cd $platform_path
	elif [[ $1 = "easycut" ]]; then
		cd $easycut_path
	# elif [[ $1 = "version_manager" ]]; then
	elif [[ $1 = "version_manager" ]]; then
		cd $version_manager_path
	fi
}

### FETCH

fetch_tags(){

	go_to_dir $1

	# fetch tags from all repos (including any temporary USB repos)
	if local var=$(git fetch --all -t 2>&1)
	then 
		echo $var
		return true
	else 
		echo $var
		return false
	fi
}

### FETCH ALL REPO TAGS (incl. version manager)

fetch_tags_for_all_repos(){

	local platform_success=$(fetch_tags platform)
	local easycut_success=$(fetch_tags easycut)
	local version_manager_success=$(fetch_tags version_manager)

	echo $platform_success
	echo $easycut_success
	echo $version_manager_success

}

### DEBUGGING

fsck_repo(){

	go_to_dir $1

	if local var=$(git fsck --lost-found 2>&1)
	then 
		echo $var
		return true
	else 
		echo $var
		return false
	fi
}

### PREPATORY COMMANDS

# set up temporary repository from USB
# arguments: argument 1 is the repo we're setting up for, argument 2 is the usb filepath

set_up_usb_repo(){

	go_to_dir $1

	if local var=$(git remote add temp_repository $2)
	then 
		echo $var
		return True

	else
		echo $var
		return False
	fi
}

# describe current tag & return
current_version(){

	go_to_dir $1

	if local var=$(git describe --tags 2>&1)
	then
		echo $var
		return True

	else
		echo $var
		return False

	fi
}


### CHECKOUT NEW VERSIONS

# arg 1 is the repo, arg 2 is the version
checkout_new_version(){

	go_to_dir $1

	if local var=$(git checkout $2 -f 2>&1)
	then
		echo $var
		return True

	else
		echo $var
		return False

	fi
}


### REPAIR AND BACKUPS

# arguments are 1 = git URL (or bundle to clone), 2 = target directory
clone_backup_repo(){

	if [ -d $2]
	then
		echo "backup directory already exists!"
		return False
	else
		if local var=$(git clone --bare $1 $2 2>&1)
		then 
			echo $var
			return True
		else
			echo $var
			return False

		fi
	fi
}

# set up backups with git clone
clone_backup_repos(){

	cd $home_dir

	local platform_success=$(clone_backup_repo "https://github.com/YetiTool/console-raspi3b-plus-platform.git" console-raspi3b-plus-platform-backup)
	local easycut_success=$(clone_backup_repo "https://github.com/YetiTool/easycut-smartbench.git" easycut-smartbench-backup)
	local version_manager_success=$(clone_backup_repo "https://github.com/YetiTool/smartbench-version-manager.git" smartbench-version-manager-backup)

	echo $platform_success
	echo $easycut_success
	echo $version_manager_success

}

# git-repair
repair_repo(){

	go_to_dir $1

	if local var=$(git-repair --force 2>&1)
	then 
		echo $var
		return True
	else
		echo $var
		
		if local var1=$(sudo aptitude install git-repair)
		then
			if local var2=$(git-repair --force 2>&1)
			then 
				echo $var1
				echo $var2
				return True
		
			else
				echo $var1
				echo $var2
				return False
		
			fi
		else
			echo $var1
			return False

		fi
	fi

}

# git prune
prune_repo(){

	go_to_dir $1

	if local var=$(git prune 2>&1)
	then
		echo $var
		return True

	else
		echo $var
		return False

	fi
}

# git gc --aggressive
gc_repo(){

	go_to_dir $1

	if local var=$(git gc --aggressive 2>&1)
	then
		echo $var
		return True

	else
		echo $var
		return False

	fi
}
d