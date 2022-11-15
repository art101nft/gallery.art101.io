#!/bin/bash

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

# Ensure we have all metadata
.venv/bin/python3 download_metadata.py

# Recurse into each data directory containing metadata and fetch images from IPFS
for contract_dir in data/0x*; do
  echo "moving into ${contract_dir}";
  pushd "${contract_dir}";
  CONTRACT="$(echo $contract_dir | sed s_data/__)";
  for i in *.json; do
    IMG="$(cat $i | jq -r .image | sed s_ipfs://__)";
    NAME="$(cat $i | jq -r .name)";
    FULLPATH="http://127.0.0.1:8080/ipfs/${IMG}";
    echo -e "[+] Fetching assets for ${CONTRACT} token metadata ${i}"
    if [[ $CONTRACT -eq $NFZ ]]; then
      ANIMATION="$(cat $i | jq -r .animation_url)";
      ANIMATIONINDEX="${ANIMATION}/index.html";
      ANIMATIONPATH="http://127.0.0.1:8080/ipfs/${ANIMATION}";
      if [[ -f "${ANIMATION}" ]]; then
        rm "${ANIMATION}";
      fi
      mkdir -p "${ANIMATION}";
      if [[ ! -f "${ANIMATIONINDEX}" ]]; then
        wget -c -t 3 "${ANIMATIONPATH}" -O "${ANIMATIONINDEX}";
      fi
      egrep -o "\w*.png" "${ANIMATIONINDEX}" | xargs -I % bash -c "if [[ ! -f ${ANIMATION}/% ]]; then wget -c -t 3 ${ANIMATIONPATH}/% -O ${ANIMATION}/%; else echo ${ANIMATION}/% does exist. Skipping.; fi"
    fi
    if [[ $CONTRACT -eq $RMUTT ]]; then
      ANIMATION="$(cat $i | jq -r .animation_url | sed s_ipfs://__)";
      ANIMATIONPATH="http://127.0.0.1:8080/ipfs/${ANIMATION}";
      mkdir -p $(dirname $ANIMATION)
      if [[ ! -f "${ANIMATION}" ]]; then
        wget -c -t 3 "${ANIMATIONPATH}" -O "${ANIMATION}";
      fi
    fi
    if [[ ! -f $IMG ]]; then
      echo "${NAME} - ${IMG} does not exist, fetching from ${FULLPATH}";
      mkdir -p $(dirname $IMG)
      wget "${FULLPATH}" -O "${IMG}";
    else
      echo "${NAME} - ${IMG} does exist, skipping";
    fi
    if [[ ! -f "${IMG}.fullsize.png" ]]; then
      echo "[!] Full-sized PNG of ${NAME} does not exist, converting"
      if [[ "${CONTRACT}" -eq "${NFS}" ]] || [[ "${CONTRACT}" -eq "${MND}" ]] || [[ "${CONTRACT}" -eq "${SXM}" ]]; then
        cat ${IMG} | inkscape -p -C --export-dpi=30 --export-type=png | convert - ${IMG}.fullsize.png;
      else
        convert ${IMG} ${IMG}.fullsize.png;
      fi
    fi
    if [[ ! -f "${IMG}.thumbnail.png" ]]; then
      echo "[!] Thumbnail PNG of ${NAME} does not exist, converting"
      if [[ "${CONTRACT}" -eq "${NFS}" ]] || [[ "${CONTRACT}" -eq "${MND}" ]] || [[ "${CONTRACT}" -eq "${SXM}" ]]; then
        cat ${IMG} | inkscape -p -C --export-dpi=30 --export-type=png | convert - -resize 50% ${IMG}.thumbnail.png;
      else
        convert -resize 25% ${IMG} ${IMG}.thumbnail.png;
      fi
    fi
  done
  popd
done

sleep 10

# sync metadata and images
echo "[+] Syncing NFS assets to S3"; sleep 3;
aws s3 sync data/${NFS}/ s3://art101-assets/${NFS}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${NFS}/ s3://art101-assets/${NFS}/ --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync data/${NFS}/ s3://art101-assets/${NFS}/ --content-type "image/svg+xml" --exclude "*.json" --exclude "*.png" --include "*"
echo "[+] Syncing MND assets to S3"; sleep 3;
aws s3 sync data/${MND}/ s3://art101-assets/${MND}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${MND}/ s3://art101-assets/${MND}/ --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync data/${MND}/ s3://art101-assets/${MND}/ --content-type "image/svg+xml" --exclude "*.json" --exclude "*.png" --include "*"
echo "[+] Syncing SXM assets to S3"; sleep 3;
aws s3 sync data/${SXM}/ s3://art101-assets/${SXM}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${SXM}/ s3://art101-assets/${SXM}/ --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync data/${SXM}/ s3://art101-assets/${SXM}/ --content-type "image/svg+xml" --exclude "*.json" --exclude "*.png" --include "*"
echo "[+] Syncing BB assets to S3"; sleep 3;
aws s3 sync data/${BB}/ s3://art101-assets/${BB}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${BB}/ s3://art101-assets/${BB}/ --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing NFZ assets to S3"; sleep 3;
aws s3 sync data/${NFZ}/ s3://art101-assets/${NFZ}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${NFZ}/ s3://art101-assets/${NFZ}/ --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync data/${NFZ}/ s3://art101-assets/${NFZ}/ --content-type "text/html" --exclude "*" --include "*.html"
echo "[+] Syncing BV assets to S3"; sleep 3;
aws s3 sync data/${BV}/ s3://art101-assets/${BV}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${BV}/ s3://art101-assets/${BV}/ --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing RMUTT assets to S3"; sleep 3;
aws s3 sync data/${RMUTT}/ s3://art101-assets/${RMUTT}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${RMUTT}/ s3://art101-assets/${RMUTT}/ --content-type "image/png" --exclude "*" --include "*.png"
aws s3 sync data/${RMUTT}/ s3://art101-assets/${RMUTT}/ --content-type "model/gltf-binary" --exclude "*" --include "*.glb"
echo "[+] Syncing NFTISSE assets to S3"; sleep 3;
aws s3 sync data/${NFTISSE}/ s3://art101-assets/${NFTISSE}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${NFTISSE}/ s3://art101-assets/${NFTISSE}/ --content-type "image/png" --exclude "*.json" --include "*"
echo "[+] Syncing RENASCENCE assets to S3"; sleep 3;
aws s3 sync data/${RENASCENCE}/ s3://art101-assets/${RENASCENCE}/ --content-type "application/json" --exclude "*" --include "*.json"
aws s3 sync data/${RENASCENCE}/ s3://art101-assets/${RENASCENCE}/ --content-type "image/png" --exclude "*.json" --include "*"


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
