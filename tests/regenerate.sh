#!/bin/bash
# Note that this scripts expects a directory with WR switches dotconfigs, e.g:
#   https://gitlab.cern.ch/white-rabbit/wrs-configs-cs-ccr-feop.git
#   https://gitlab.cern.ch/white-rabbit/wrs-configs-cs-ccr-felab.git

if [[ $# -ne 2 ]]; then
    echo "Script to regenerate all White Rabbit switch dot-configs for a specific environment"
    echo "Usage: $0 <felab/feop> <fw_version>"
    exit 1
fi

ENV=$1
FW_VERSION=$2
CONFIG_DIR="../../wrs-configs-cs-ccr-$ENV"

if [[ ! -d "$CONFIG_DIR" ]]; then
    echo "$CONFIG_DIR does not exist, it should contain WR switch dot-configs"
    exit 1
fi

read -s -p "CCDE password for $USER: " ccde_pass
echo    # output a newline
mkdir -p "$ENV"

for file in "$CONFIG_DIR"/config-*; do
    base_file=$(basename "$file")
    switch_name=${base_file#config-}
    output_file="$ENV/config-$switch_name"
    echo "*** $switch_name"

    # Generate new dot-config...
    ../generate_config.py --ccde --user "$USER" --password "$ccde_pass" --dev \
        $switch_name --fw-version "$FW_VERSION" --config "$output_file"

    if [[ $? != 0 ]]; then
        rm "$output_file" 2> /dev/null
        continue
    fi

    # ...and compare it with the old one
    diff -u "$CONFIG_DIR/config-$switch_name" "$ENV/config-$switch_name" > "$ENV/diff-$switch_name"
    echo "=============="
done
