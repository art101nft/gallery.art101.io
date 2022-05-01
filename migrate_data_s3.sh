#!/bin/bash

# Define each contract since content types may vary
export SXM=0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108
export MND=0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919
export NFS=0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB
export BB=0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5
export NFZ=0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b
export BV=0xea2dc6f116a4c3d6a15f06b4e8ad582a07c3dd9c

# Ensure we have all metadata
.venv/bin/python3 download_metadata.py

# Recurse into each data directory containing metadata and fetch images from IPFS
for i in data/0x*; do
  echo "moving into ${i}";
  pushd "${i}";
  sleep 5;
  for i in *.json; do
    IMG="$(cat $i | jq -r .image | sed s_ipfs://__)";
    NAME="$(cat $i | jq -r .name)";
    FULLPATHZ="http://127.0.0.1:8080/ipfs/${IMG}";
    FULLPATH="https://gateway.pinata.cloud/ipfs/${IMG}";
    if [[ ! -f $IMG ]]; then
      echo "${NAME} - ${IMG} does not exist, fetching from ${FULLPATH}";
      wget "${FULLPATH}";
      sleep 1;
    else
      echo "${NAME} - ${IMG} does exist, skipping";
    fi
  done
  popd
done

# sync metadata and images
echo "[+] Syncing NFS assets to S3"; sleep 3;
aws s3 sync data/${NFS}/ s3://art101-assets/${NFS}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${NFS}/ s3://art101-assets/${NFS}/ --content-type "image/svg+xml" --exclude "*.json" --include "*"
echo "[+] Syncing MND assets to S3"; sleep 3;
aws s3 sync data/${MND}/ s3://art101-assets/${MND}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${MND}/ s3://art101-assets/${MND}/ --content-type "image/svg+xml" --exclude "*.json" --include "*"
echo "[+] Syncing SXM assets to S3"; sleep 3;
aws s3 sync data/${SXM}/ s3://art101-assets/${SXM}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${SXM}/ s3://art101-assets/${SXM}/ --content-type "image/svg+xml" --exclude "*.json" --include "*"
echo "[+] Syncing BB assets to S3"; sleep 3;
aws s3 sync data/${BB}/ s3://art101-assets/${BB}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${BB}/ s3://art101-assets/${BB}/ --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing NFZ assets to S3"; sleep 3;
aws s3 sync data/${NFZ}/ s3://art101-assets/${NFZ}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${NFZ}/ s3://art101-assets/${NFZ}/ --content-type "image/png" --exclude "*.json" --include "*"
# echo "[+] Syncing BV assets to S3"; sleep 3;
aws s3 sync data/${BV}/ s3://art101-assets/${BV}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${BV}/ s3://art101-assets/${BV}/ --content-type "image/png" --exclude "*.json" --include "*"



# Recurse saved image files and update their metadata on S3 to be an image
# use this if you already synced and need to update metadata/content-type
# for i in Qm*; do
# aws s3api copy-object \
#   --bucket art101-assets \
#   --content-type "image/svg+xml" \
#   --copy-source "art101-assets/0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB/${i}" \
#   --metadata-directive "REPLACE" \
#   --key "0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB/${i}"
# done
