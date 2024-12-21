#!/bin/bash

set -e

# Define each contract since content types may vary
export SXM=0x0dD0CFeAE058610C88a87Da2D9fDa496cFadE108
export MND=0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919
export NFS=0xdc8bEd466ee117Ebff8Ee84896d6aCd42170d4bB
export BB=0x62C1e9f6830098DFF647Ef78E1F39244258F7bF5
export NFZ=0xc918F953E1ef2F1eD6ac6A0d2Bf711A93D20Aa2b
export BV=0xea2dc6f116a4c3d6a15f06b4e8ad582a07c3dd9c
export RMUTT=0x6c61fB2400Bf55624ce15104e00F269102dC2Af4
export NFTISSE=0x343b68141129ec115c1fc523c5ae90586fe95b77
export RENASCENCE=0x501a31185927136E87cDfC97dDd4553D8eC1bb4A
export GUZZLERS=0x87739a10f06c08468206008f6cf1abab8e6e9a0d
export ENZOS=0x621b92370fe1a27f95e7109daf0423714b73e9b5

export IPFS_URL=http://127.0.0.1:8081

# Ensure we have all metadata
.venv/bin/python3 download_metadata.py

# Recurse into each data directory containing metadata and fetch images from IPFS
for contract_dir in data/0x*; do
  pushd "${contract_dir}";
  CONTRACT_ADDRESS="$(basename $contract_dir)";

  # Parse each metadata JSON and get images/animations
  for i in *.json; do
    IMG_HASH="$(cat $i | jq -r .image | sed s_ipfs://__)";
    IMG_NAME="$(cat $i | jq -r .name)";
    IMG_IPFS_URL="${IPFS_URL}/ipfs/${IMG_HASH}";

    # Non-Fungible Zine has animations and HTML files
    if [[ $CONTRACT_ADDRESS -eq $NFZ ]]; then
      ANIMATION="$(cat $i | jq -r .animation_url)";
      ANIMATIONINDEX="${ANIMATION}/index.html";
      ANIMATIONPATH="${IPFS_URL}/ipfs/${ANIMATION}";
      if [[ -f "${ANIMATION}" ]]; then
        rm "${ANIMATION}";
      fi
      mkdir -p "${ANIMATION}";
      if [[ ! -f "${ANIMATIONINDEX}" ]]; then
        wget -q -c -t 3 "${ANIMATIONPATH}" -O "${ANIMATIONINDEX}";
      fi
      egrep -o "\w*.png" "${ANIMATIONINDEX}" | xargs -I % bash -c "if [[ ! -f ${ANIMATION}/% ]]; then wget -q -c -t 3 ${ANIMATIONPATH}/% -O ${ANIMATION}/%; fi"
    fi

    # Rmutt has animation files
    if [[ $CONTRACT_ADDRESS -eq $RMUTT ]]; then
      ANIMATION="$(cat $i | jq -r .animation_url | sed s_ipfs://__)";
      ANIMATIONPATH="${IPFS_URL}/ipfs/${ANIMATION}";
      mkdir -p $(dirname $ANIMATION)
      if [[ ! -f "${ANIMATION}" ]]; then
        wget -q -c -t 3 "${ANIMATIONPATH}" -O "${ANIMATION}";
      fi
    fi

    # Download the image
    if [[ ! -f $IMG_HASH ]]; then
      echo "${IMG_NAME} - ${IMG_HASH} does not exist, fetching from ${IMG_IPFS_URL}";
      mkdir -p $(dirname $IMG_HASH)
      wget -q "${IMG_IPFS_URL}" -O "${IMG_HASH}" &
    fi

    # Create fullsize image for discord messages
    if [[ ! -f "${IMG_HASH}.fullsize.png" ]]; then
      echo "[!] Full-sized PNG of ${IMG_NAME} does not exist, converting"
      if [[ "${CONTRACT_ADDRESS}" -eq "${NFS}" ]] || [[ "${CONTRACT_ADDRESS}" -eq "${MND}" ]] || [[ "${CONTRACT_ADDRESS}" -eq "${SXM}" ]]; then
        cat ${IMG_HASH} | inkscape -p -C --export-dpi=30 --export-type=png | convert - ${IMG_HASH}.fullsize.png;
      else
        convert ${IMG_HASH} ${IMG_HASH}.fullsize.png;
      fi
    fi

    # Create thumbnail images
    if [[ ! -f "${IMG_HASH}.thumbnail.png" ]]; then
      echo "[!] Thumbnail PNG of ${IMG_NAME} does not exist, converting"
      if [[ "${CONTRACT_ADDRESS}" -eq "${NFS}" ]] || [[ "${CONTRACT_ADDRESS}" -eq "${MND}" ]] || [[ "${CONTRACT_ADDRESS}" -eq "${SXM}" ]]; then
        cat ${IMG_HASH} | inkscape -p -C --export-dpi=30 --export-type=png | convert - -resize 50% ${IMG_HASH}.thumbnail.png;
      else
        convert -resize 25% ${IMG_HASH} ${IMG_HASH}.thumbnail.png;
      fi
    fi

  done
  popd
done

# sync metadata and images
echo "[+] Syncing NFS assets to S3"; sleep 1;
aws s3 sync "data/${NFS}/" "s3://art101-assets/${NFS}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${NFS}/" "s3://art101-assets/${NFS}/" --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync "data/${NFS}/" "s3://art101-assets/${NFS}/" --content-type "image/svg+xml" --exclude "*.json" --exclude "*.png" --include "*"
echo "[+] Syncing MND assets to S3"; sleep 1;
aws s3 sync "data/${MND}/" "s3://art101-assets/${MND}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${MND}/" "s3://art101-assets/${MND}/" --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync "data/${MND}/" "s3://art101-assets/${MND}/" --content-type "image/svg+xml" --exclude "*.json" --exclude "*.png" --include "*"
echo "[+] Syncing SXM assets to S3"; sleep 1;
aws s3 sync "data/${SXM}"/ "s3://art101-assets/${SXM}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${SXM}"/ "s3://art101-assets/${SXM}/" --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync "data/${SXM}"/ "s3://art101-assets/${SXM}/" --content-type "image/svg+xml" --exclude "*.json" --exclude "*.png" --include "*"
echo "[+] Syncing BB assets to S3"; sleep 1;
aws s3 sync "data/${BB}/" "s3://art101-assets/${BB}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${BB}/" "s3://art101-assets/${BB}/" --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing NFZ assets to S3"; sleep 1;
aws s3 sync "data/${NFZ}/" "s3://art101-assets/${NFZ}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${NFZ}/" "s3://art101-assets/${NFZ}/" --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync "data/${NFZ}/" "s3://art101-assets/${NFZ}/" --content-type "text/html" --exclude "*" --include "*.html"
echo "[+] Syncing BV assets to S3"; sleep 1;
aws s3 sync "data/${BV}/" "s3://art101-assets/${BV}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${BV}/" "s3://art101-assets/${BV}/" --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing RMUTT assets to S3"; sleep 1;
aws s3 sync "data/${RMUTT}/" "s3://art101-assets/${RMUTT}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${RMUTT}/" "s3://art101-assets/${RMUTT}/" --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync "data/${RMUTT}/" "s3://art101-assets/${RMUTT}/" --content-type "model/gltf-binary" --exclude "*" --include "*.glb"
echo "[+] Syncing NFTISSE assets to S3"; sleep 1;
aws s3 sync "data/${NFTISSE}/" "s3://art101-assets/${NFTISSE}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${NFTISSE}/" "s3://art101-assets/${NFTISSE}/" --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing RENASCENCE assets to S3"; sleep 1;
aws s3 sync "data/${RENASCENCE}/" "s3://art101-assets/${RENASCENCE}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${RENASCENCE}/" "s3://art101-assets/${RENASCENCE}/" --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing GUZZLERS assets to S3"; sleep 1;
aws s3 sync "data/${GUZZLERS}/" "s3://art101-assets/${GUZZLERS}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${GUZZLERS}/" "s3://art101-assets/${GUZZLERS}/" --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing ENZOS assets to S3"; sleep 1;
aws s3 sync "data/${ENZOS}/" "s3://art101-assets/${ENZOS}/" --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync "data/${ENZOS}/" "s3://art101-assets/${ENZOS}/" --content-type "image/png" --exclude "*.json" --include "*"


# Recurse saved image files and update their metadata on S3 to be an image
# use this if you already synced and need to update metadata/content-type
# for i in Qm*.png; do
#   echo -e "[+] Updating metadata for ${i}";
#   aws s3api copy-object \
#     --bucket art101-assets \
#     --content-type "image/png" \
#     --copy-source "art101-assets/0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919/${i}" \
#     --metadata-directive "REPLACE" \
#     --key "0x7f81858ea3b43513adfaf0a20dc7b4c6ebe72919/${i}"
# done
