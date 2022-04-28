#!/bin/bash

# sync metadata
aws s3 sync data/0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108/ s3://art101-assets/0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108/ --content-type "application/json" --exclude "*" --include "*.json" --dryrun

# sync images
aws s3 sync data/0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108/ s3://art101-assets/0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108/ --content-type "image/svg+xml" --exclude "*.json" --include "*" --dryrun

# Recurse into each data directory containing metadata and fetch images from IPFS
for i in 0x*; do
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

# Recurse saved image files and update their metadata on S3 to be an image
for i in Qm*; do
aws s3api copy-object \
  --bucket art101-assets \
  --content-type "image/svg+xml" \
  --copy-source "art101-assets/0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB/${i}" \
  --metadata-directive "REPLACE" \
  --key "0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB/${i}"
done
