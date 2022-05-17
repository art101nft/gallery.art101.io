# gallery.art101.io

Gallery and marketplace site for Art101 NFT projects.

Written with [Quart](https://pgjones.gitlab.io/quart/index.html) (async Flask).

It currently provides current market status and ownership info. In the future we will implement background chain scanning for the purposes of showing historical activity of each token for each collection, regardless of which method of purchase/sale (Opensea, LooksRare, Gem.xyz, etc).

Additionally, rarity will be implemented within the gallery to provide users with the ability to filter and sort based upon trait rarity and groupings.

## Development

Required software:
* docker.io (`sudo apt-get install docker.io`)
* docker-compose (`sudo apt-get install docker-compose`)
* make (`sudo apt-get install make`)
* python3-venv (`sudo apt-get install python3-venv`)

Required tokens:
* Etherscan (look up contract details)
* Eth node (Infura, geth, etc)

Install Python dependencies

`make setup`

Stand up containers (just Redis cache)

`make up`

Setup secrets/tokens

`cp env-example .env && vim .env`

Run development server

`make dev`

## Assets

There are some helper scripts I wrote to download all of the artwork and metadata assets from Pinata's public IPFS gateway. It's a pretty slow process, but once everything is downloaded, I pushed it to Amazon S3 and am hosting directly from the S3 bucket.

`download_metadata.py` fetches all of the metadata and stores JSON objects locally.
`migrate_data_s3.sh` uses the downloaded JSON objects to scrape the image IPFS hashes and fetches each image, then uses `awscli` to sync to S3.
