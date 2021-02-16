#!/bin/bash

dev=0
while getopts d option; do
	case "${option}" in
	d) dev=1; printf "Development flag set.\n"; sleep 2;;
	*) exit 1;;
	esac
done

TOOLS_PATH="/nfs/cs-ccr-nfs3/vol1/u1/white_rabbit/tools"
if [ "$dev" == "1" ] ; then
	TOOLS_PATH="."
fi
DEPLOY_PATH="${TOOLS_PATH}/wrs_config_generator_releases"
GIT_PROJECT="wrs-config-generator"
GIT_URL=https://gitlab.cern.ch/white-rabbit/${GIT_PROJECT}.git

#Get list of tags 
tags=`git ls-remote --tags https://gitlab.cern.ch/white-rabbit/wrs-config-generator.git |  grep -v "\^{}" |grep -o 'refs/tags/w[0-9]*\.[0-9]*\.[0-9]*.*' | sort -r | head | grep -o '[^\/]*$' | tr '\n' ' '`
if [ "$?" != "0" ] ; then
	printf "Cannot get list of tags !!! Exit.\n" 
	exit 1
fi

IFS=' ' read -ra ifaces <<< "$tags"

list_cloned_tags() {
	local list=`ls ${DEPLOY_PATH}| grep -e "^w" | tr "\n" " "`
	echo "$list"
}

active_version() {
	local active=`ls -l ${TOOLS_PATH}/${GIT_PROJECT} | grep -o "w[0-9].*"`
	echo "$active"
}

menu_header() {
	clear
	printf "#################################################\n"
	printf "# wrs-config-generator deployment               #\n"
	printf "#################################################\n"
	printf "# Release dir :\n"
	printf "#     - ${TOOLS_PATH}\n"
	local active=$(active_version)
	if [ -n "$active" ] ; then 	
		printf "#  Current version:\n"
		printf "#     - %s\n#\n" "$active"
	fi
	local lct=$(list_cloned_tags)
	if [ -n "$lct" ] ; then 	
		printf "#  List of cloned tags :\n"
		for x in $lct ; do
			printf "#     - %s\n" "$x" 
		done
		printf "#\n"
	fi
	printf "\n"
}

menu_deploy() {
	while : ; do
		menu_header
	    printf "Set production version menu\n\n"
	    local lct=$(list_cloned_tags)
		IFS=' ' read -ra idep <<< "$lct"
		if [ -n "$lct" ] ; then
			for i in "${!idep[@]}"; do
			    printf "  %s) %s\n" "$i" "${idep[$i]}"
			done
		fi
		printf "  q) quit\n\n"
	    printf "\n  Choice: "
		IFS= read -r opt
		if [ "$opt" == "q" ] ; then 
			break;
		fi
		if [[ $opt =~ ^[0-9]+$ ]] && (( ($opt >= 0) && ($opt <= "${#idep[@]}") ));  then
    		rm -f ${TOOLS_PATH}/${GIT_PROJECT}
    		ln -s ${DEPLOY_PATH}/${idep[$opt]} ${TOOLS_PATH}/${GIT_PROJECT}
    		break
		else
		echo 
    		if [ "$opt" == "q" ] ; then 
    			return 0
    		fi
    	fi
    done
} 

menu_dev() {
	while : ; do
		menu_header
	    printf "Set development version menu\n\n"
	    local lct=$(list_cloned_tags)
		IFS=' ' read -ra idep <<< "$lct"
		if [ -n "$lct" ] ; then
			for i in "${!idep[@]}"; do
			    printf "  %s) %s\n" "$i" "${idep[$i]}"
			done
		fi
		printf "  q) quit\n\n"
	    printf "\n  Choice: "
		IFS= read -r opt
		if [ "$opt" == "q" ] ; then
			break;
		fi
		if [[ $opt =~ ^[0-9]+$ ]] && (( ($opt >= 0) && ($opt <= "${#idep[@]}") ));  then
    		rm -f ${TOOLS_PATH}/${GIT_PROJECT}_dev
    		ln -s ${DEPLOY_PATH}/${idep[$opt]} ${TOOLS_PATH}/${GIT_PROJECT}_dev
    		break
		else
		echo
    		if [ "$opt" == "q" ] ; then
    			return 0
    		fi
    	fi
    done
}

clone() {
	local tagToClone=$1
	local dirLocation=${DEPLOY_PATH}/${tagToClone}
	echo "Clonning $tagToClone to ${dirLocation} ..." 
	if [ -d ${dirLocation} ] ; then
		printf "Error: ${dirLocation} directory already exists."
	else
		git clone -b master ${GIT_URL} ${dirLocation}	
		if [ "$?" != "0" ] ; then
			printf "Error: Cannot clone tag ${tagToClone} !!!\n"
		else 
			printf "Success: Tag ${tagToClone} successfully cloned.\n"		 
		fi
	fi
 	sleep 6
}

menu_clone() {
	while : ; do
		menu_header
	    printf "Clone tag menu\n\n"
		for i in "${!ifaces[@]}"; do
		    printf "  %s) %s\n" "$i" "${ifaces[$i]}"
		done
		printf "  q) quit\n\n"
	    printf "  Choice : "
		IFS= read -r opt
		if [[ $opt =~ ^[0-9]+$ ]] && (( ($opt >= 0) && ($opt <= "${#ifaces[@]}") ));  then
    		clone "${ifaces[$opt]}"
		else
		echo 
    		if [ "$opt" == "q" ] ; then 
    			break;
    		fi
    	fi
    done
}

menu_main() {
	while : ; do
	    menu_header
	    printf "Main menu\n\n"
		printf "  0) Clone new tagged version\n"
		printf "  1) Set production  version (used by CCDE)\n"
		printf "  2) Set development version (used by CCDE_DEV) \n"
		printf "  q) Quit\n\n"
		printf "  Choice :"
		IFS= read -r opt
		case "$opt" in
			"0") menu_clone ;;
			"1") menu_deploy;;
			"2") menu_dev;;
			"q") break ;;
		esac
    done	
}

menu_main
