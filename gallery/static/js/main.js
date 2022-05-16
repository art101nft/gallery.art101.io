window.addEventListener('DOMContentLoaded', () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');

  // Reload page if Metamask account changes
  if (ethereum) {
    ethereum.on('accountsChanged', function (accounts) {
      window.location.href = '';
    });
  }
});

up.compiler('#withdrawFunds', function(element) {
  withdrawFunds();
})

up.compiler('#tokenTitle', function(element, data) {
  updateTokenInfo(data.contractAddress, data.tokenId);
  updateTokenSales(data.contractAddress, data.tokenId, data.erc1155);
})

up.compiler('#ownerTokens', function(element, data) {
  fetchOwnerTokens(data.contractAddress, data.walletAddress, data.urlSlug);
})

up.compiler('#connectWallet', function(element) {
  armConnectButton();
})

up.compiler('.tokenZoom', function(element) {
  new Viewer(document.getElementById('tokenImage'), {
    inline: false,
    navbar: 0,
    toolbar: 0,
    transition: 0,
  });
})

up.compiler('.tokenPreview', function(element, data) {
  updateTokenPreview(data.contractAddress, data.tokenId)
})

up.compiler('.notyBox', function(element, data) {
  notif(data)
})

async function getMetamaskAccount() {
  const accounts = await window.ethereum.request({
    method: 'eth_requestAccounts',
  });
  const account = accounts[0];
  return account
}

async function armConnectButton(){
  const onboarding = new MetaMaskOnboarding();
  const onboardButton = document.getElementById('connectWallet');
  let accounts;

  if (!onboardButton) {
    return false;
  }

  onboardButton.onclick = async () => {
    await switchNetwork();
    if (!MetaMaskOnboarding.isMetaMaskInstalled()) {
      onboardButton.onclick = () => {
        onboardButton.classList.add('is-loading');
        onboardButton.disabled = true;
        onboarding.startOnboarding();
      };
    } else if (accounts && accounts.length > 0) {
      onboardButton.classList.remove('is-loading');
      onboardButton.disabled = false;
      onboarding.stopOnboarding();
    } else {
      try {
        onboardButton.classList.add('is-loading');
        onboardButton.disabled = true;
        let acc = await getMetamaskAccount();
        window.location.href = ('?wallet=' + acc);
      } catch(e) {
        console.log(e);
        onboardButton.classList.remove('is-loading');
      }
    }
  };

};

async function getMetamaskAccount() {
  const accounts = await window.ethereum.request({
    method: 'eth_requestAccounts',
  });
  const account = accounts[0];
  return account
}

async function getSignedData(publicAddress, jsonData) {
  const signedData = await window.ethereum.request({
    method: 'eth_signTypedData_v3',
    params: [publicAddress, JSON.stringify(jsonData)]
  });
  console.log(signedData);
  return signedData
}

async function switchNetwork(){
  // don't do this if no metamask (errors on coinbase wallet)
  if (!MetaMaskOnboarding.isMetaMaskInstalled()) {
    return false;
  }
  await ethereum.request({
    method: 'wallet_switchEthereumChain',
    params: [{ chainId: '0x1' }],
  });
}

function shortenAddress(a) {
  return a.slice(0, 6) + '...' + a.slice(-4)
}

async function _withdrawFunds() {
  let gasLimit;
  await switchNetwork();
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  const marketplace = new w3.eth.Contract(marketplaceAbi, marketplaceContract);
  const mm = await getMetamaskAccount();
  const gasPrice = await w3.eth.getGasPrice();
  const balance = await marketplace.methods.pendingBalance(mm).call();
  const withdrawButton = document.getElementById('withdrawFunds');
  if (balance > 0) {
    withdrawButton.classList.remove('hidden');
    withdrawButton.innerHTML = `Withdraw  (<strong>+${await w3.utils.fromWei(balance, 'ether')} Ξ</strong>)`;
    withdrawButton.onclick = async function () {
      withdrawButton.classList.add('is-loading');
      try {
        await marketplace.methods.withdraw().estimateGas({from: mm}, function(err, gas){
          gasLimit = gas;
        });
        await marketplace.methods.withdraw().send({
          from: mm,
          gasPrice: gasPrice,
          gas: gasLimit
        });
        withdrawButton.classList.remove('is-loading');
        withdrawButton.classList.add('hidden');
      } catch(e) {
        withdrawButton.classList.remove('is-loading');
      }
    }
  } else {
    withdrawButton.classList.add('hidden');
  }
}

async function withdrawFunds() {
  await _withdrawFunds();
  setInterval(async function () {
    await _withdrawFunds();
  }, 8000);
}

async function updateTokenSales(contractAddress, tokenId, erc1155) {
  await _updateTokenSales(contractAddress, tokenId, erc1155);
  setInterval(async function () {
    await _updateTokenSales(contractAddress, tokenId, erc1155);
  }, 6000);
}

async function _updateTokenSales(contractAddress, tokenId, erc1155) {
  let gasLimit;
  let contract;
  let userIsOwner;
  let approved;
  let setApproval;
  await switchNetwork();
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  const gasPrice = await w3.eth.getGasPrice();
  const mm = await getMetamaskAccount();
  const marketplace = new w3.eth.Contract(marketplaceAbi, marketplaceContract);
  const offer = await marketplace.methods.tokenOffers(contractAddress, tokenId).call();
  const bid = await marketplace.methods.tokenBids(contractAddress, tokenId).call();
  const collection = await marketplace.methods.collectionState(contractAddress).call();
  if (!collection.status) {
    console.log('This collection is not yet active on the marketplace.');
    return
  }
  const tokenSaleStatus = document.getElementById('tokenSaleStatus');
  const tokenBidStatus = document.getElementById('tokenBidStatus');
  const bidAmountEther = document.getElementById('bidAmountEther');
  const sellAmountEther = document.getElementById('sellAmountEther');
  const tokenPlaceBid = document.getElementById('tokenPlaceBid');
  const tokenAcceptBid = document.getElementById('tokenAcceptBid');
  const tokenWithdrawSale = document.getElementById('tokenWithdrawSale');
  const tokenWithdrawBid = document.getElementById('tokenWithdrawBid');
  const tokenPurchase = document.getElementById('tokenPurchase');
  const tokenSell = document.getElementById('tokenSell');
  const collectionRoyalty = document.getElementById('collectionRoyalty');
  collectionRoyalty.innerHTML = `This collection has a royalty of ${collection.royaltyPercent}%`;
  if (erc1155 == "true") {
    contract = new w3.eth.Contract(erc1155Abi, contractAddress);
    userIsOwner = (await contract.methods.balanceOf(mm, tokenId).call()) > 0;
    approved = await contract.methods.isApprovedForAll(mm, marketplaceContract).call();
    setApproval = contract.methods.setApprovalForAll(marketplaceContract, true);
  } else {
    contract = new w3.eth.Contract(erc721Abi, contractAddress);
    const owner = await contract.methods.ownerOf(tokenId).call();
    userIsOwner = w3.utils.toChecksumAddress(owner) == w3.utils.toChecksumAddress(mm);
    approved = (await contract.methods.getApproved(tokenId).call()) == marketplaceContract;
    setApproval = contract.methods.approve(marketplaceContract, tokenId);
  }

  // Check if current user owns the token
  if (userIsOwner) {
    // if current user owns the token...
    sellAmountEther.classList.remove('hidden');
    tokenSell.classList.remove('hidden');
    // Wire up sell button
    tokenSell.onclick = async function () {
      if (sellAmountEther.value <= 0 || isNaN(sellAmountEther.value)) {
        notif({'message': 'Must provide a number greater than 0.', 'category': 'warning'});
        return
      }
      let amt = await w3.utils.toWei(sellAmountEther.value);
      tokenSell.classList.add('is-loading');
      try {
        if (!approved) {
          await setApproval.estimateGas({from: mm}, function(err, gas){
            gasLimit = gas;
          });
          await setApproval.send({
            from: mm,
            gasLimit: gasLimit,
            gasPrice: gasPrice
          });
        }
        await marketplace.methods.offerTokenForSale(contractAddress, tokenId, amt).estimateGas({from: mm}, function(err, gas){
          gasLimit = gas;
        });
        await marketplace.methods.offerTokenForSale(contractAddress, tokenId, amt).send({
          from: mm,
          gasPrice: gasPrice,
          gas: gasLimit
        });
      } catch(e) {
        console.log(e);
      }
      tokenSell.classList.remove('is-loading');
      sellAmountEther.value = "";
    }
  } else {
    // otherwise, show bid form
    bidAmountEther.classList.remove('hidden');
    tokenPlaceBid.classList.remove('hidden');
    // Setup click event for bid button
    tokenPlaceBid.onclick = async function () {
      if (bidAmountEther.value <= 0 || isNaN(bidAmountEther.value)) {
        notif({'message': 'Must provide a number greater than 0.', 'category': 'warning'});
        return
      }
      let amt = await w3.utils.toWei(bidAmountEther.value);
      if((amt - bid.value) > 0) {
        tokenPlaceBid.classList.add('is-loading');
        try {
          await marketplace.methods.enterBidForToken(contractAddress, tokenId).estimateGas({from: mm, value: amt}, function(err, gas){
            gasLimit = gas;
          });
          await marketplace.methods.enterBidForToken(contractAddress, tokenId).send({
            from: mm,
            gasPrice: gasPrice,
            gas: gasLimit,
            value: amt
          });
        } catch(e) {
          console.log(e);
        }
        tokenPlaceBid.classList.remove('is-loading');
        bidAmountEther.value = "";
      } else {
        notif({'message': 'Bid must be larger than the previous.', 'category': 'warning'});
      }
    };
  }

  if (offer.isForSale) {
    let saleAmountEther = await w3.utils.fromWei(offer.minValue);
    tokenSaleStatus.innerHTML = `Token is currently for sale for <strong>${saleAmountEther} Ξ</strong> by <a href="https://etherscan.io/address/${offer.seller}" target=_blank>${shortenAddress(offer.seller)}</a>.`;
    if (!userIsOwner) {
      tokenPurchase.classList.remove('hidden');
      tokenPurchase.innerHTML = `Purchase (<strong>-${saleAmountEther} Ξ</strong>)`;
      // Setup click event for purchase button
      tokenPurchase.onclick = async function () {
        tokenPurchase.classList.add('is-loading');
        try {
          await marketplace.methods.acceptOfferForToken(contractAddress, tokenId).estimateGas({from: mm, value: offer.minValue}, function(err, gas){
            gasLimit = gas;
          });
          await marketplace.methods.acceptOfferForToken(contractAddress, tokenId).send({
            from: mm,
            gasPrice: gasPrice,
            gas: gasLimit,
            value: offer.minValue
          });
          tokenPurchase.classList.add('hidden');
          bidAmountEther.classList.add('hidden');
          tokenPlaceBid.classList.add('hidden');
          tokenWithdrawBid.classList.add('hidden');
        } catch(e) {
          console.log(e);
        }
        tokenPurchase.classList.remove('is-loading');
      };
    } else {
      tokenWithdrawSale.classList.remove('hidden');
      tokenWithdrawSale.onclick = async function () {
        tokenWithdrawSale.classList.add('is-loading');
        try {
          await marketplace.methods.tokenNoLongerForSale(contractAddress, tokenId).estimateGas({from: mm}, function(err, gas){
            gasLimit = gas;
          });
          await marketplace.methods.tokenNoLongerForSale(contractAddress, tokenId).send({
            from: mm,
            gasPrice: gasPrice,
            gas: gasLimit
          });
          tokenWithdrawSale.classList.add('hidden');
        } catch(e) {
          console.log(e);
        }
        tokenWithdrawSale.classList.remove('is-loading');
      }
    }
    // if (offer.onlySellTo == '0x0000000000000000000000000000000000000000') {}
  } else {
    tokenSaleStatus.innerHTML = 'Token is not currently for sale.';
  }

  if (bid.hasBid) {
    let bidAmount = await w3.utils.fromWei(bid.value, 'ether');
    tokenBidStatus.innerHTML = `Token currently has a bid of <strong>${bidAmount} Ξ</strong> from <a href="https://etherscan.io/address/${bid.bidder}" target=_blank>${shortenAddress(bid.bidder)}</a>`;
    if (userIsOwner) {
      tokenAcceptBid.classList.remove('hidden');
      tokenAcceptBid.innerHTML = `Accept Bid (<strong>+${bidAmount} Ξ</strong>)`
      tokenAcceptBid.onclick = async function () {
        tokenAcceptBid.classList.add('is-loading');
        if (!approved) {
          try {
            await setApproval.estimateGas({from: mm}, function(err, gas){
              gasLimit = gas;
            });
            await setApproval.send({
              from: mm,
              gasLimit: gasLimit,
              gasPrice: gasPrice
            });
          } catch(e) {
            console.log(e);
            tokenAcceptBid.classList.remove('is-loading');
            return
          }
        }
        try {
          await marketplace.methods.acceptBidForToken(contractAddress, tokenId, bid.value).estimateGas({from: mm}, function(err, gas){
            gasLimit = gas;
          });
          await marketplace.methods.acceptBidForToken(contractAddress, tokenId, bid.value).send({
            from: mm,
            gasPrice: gasPrice,
            gas: gasLimit
          });
          tokenAcceptBid.classList.add('hidden');
          tokenWithdrawSale.classList.add('hidden');
          sellAmountEther.classList.add('hidden');
          tokenSell.classList.add('hidden');
        } catch(e) {
          console.log(e);
        }
        tokenAcceptBid.classList.remove('is-loading');
      }
    }

    if (w3.utils.toChecksumAddress(bid.bidder) == w3.utils.toChecksumAddress(mm)) {
      tokenWithdrawBid.classList.remove('hidden');
      tokenWithdrawBid.innerHTML = `Withdraw Bid (<strong>+${bidAmount} Ξ</strong>)`
      tokenWithdrawBid.onclick = async function () {
        tokenWithdrawBid.classList.add('is-loading');
        try {
          await marketplace.methods.withdrawBidForToken(contractAddress, tokenId).estimateGas({from: mm}, function(err, gas){
            gasLimit = gas;
          });
          await marketplace.methods.withdrawBidForToken(contractAddress, tokenId).send({
            from: mm,
            gasPrice: gasPrice,
            gas: gasLimit
          });
          tokenWithdrawBid.classList.add('hidden');
        } catch(e) {
          console.log(e);
        }
        tokenWithdrawBid.classList.remove('is-loading');
      }
    }
  } else {
    tokenBidStatus.innerHTML = 'Token currently has no bids.';
  }
}

async function fetchOwnerTokens(contractAddress, walletAddress, urlSlug) {
  let newColumn;
  let parent = document.getElementById('ownerTokens');
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  // const walletAddress = await getMMAccount();
  const walletShort = walletAddress.slice(0, 6) + '...' + walletAddress.slice(-4)
  const contract = new w3.eth.Contract(erc721Abi, contractAddress);
  const balance = await contract.methods.balanceOf(walletAddress).call();
  if (balance == 0) {
    parent.innerHTML = 'No tokens found for this address.';
    return
  }
  for (i=0; i<balance; i++) {
    if (i % 4 == 0) {
      newColumn = document.createElement('div');
      newColumn.classList.add('columns');
      parent.appendChild(newColumn);
      console.log(`Creating new child for index ${i}`)
    }
    let tokenIndex = await contract.methods.tokenOfOwnerByIndex(walletAddress, i).call();
    console.log(`Found token #${tokenIndex} for wallet ${walletAddress} in contract ${contractAddress}`)
    let newItem = document.createElement('div');
    newItem.classList.add('column');
    newColumn.appendChild(newItem);
    newItem.innerHTML = `<div class="card-image">
              <figure class="image">
                <a href="/collection/${urlSlug}/${tokenIndex}" up-target=".container" up-transition="cross-fade" up-preload>
                  <img src="/static/img/loading2.gif" width=40 class="tokenPreview previewPreload" id="tokenPreview-${tokenIndex}" up-data='{ "contractAddress": "${contractAddress}", "tokenId": "${tokenIndex}" }'>
                </a>
              </figure>
            </div>`;
    await updateTokenPreview(contractAddress, tokenIndex);
  };

}

async function getTokenMetadata(contractAddress, tokenId) {
  let res = await fetch(`/api/v1/get_token_metadata/${contractAddress}/${tokenId}`)
    .then((resp) => resp.json())
    .then(function(data) {
      return data
    })
  return res
}

async function updateTokenPreview(contractAddress, tokenId) {
  let data = await getTokenMetadata(contractAddress, tokenId);
  if (data) {
    let i = document.getElementById('tokenPreview-' + tokenId);
    i.src = loadImg(data.image, contractAddress, false);
    i.onload = function(){
      i.width = 200;
      i.classList.remove('previewPreload');
    }
  }
}

async function updateTokenInfo(contractAddress, tokenId) {
  let data = await getTokenMetadata(contractAddress, tokenId);
  if (!data) {
    document.getElementById('tokenTitle').innerHTML = 'Error';
    document.getElementById('tokenDescription').innerHTML = 'Malformed JSON payload';
    document.getElementById('tokenImage').src = '';
    return false
  }
  let offchainImg = loadImg(data.image, contractAddress, false);
  let onchainImg = loadImg(data.image, contractAddress, true);
  let onchainMeta = loadImg(data.tokenURI, contractAddress, true);
  document.getElementById('tokenTitle').innerHTML = data.name;
  if (data.ownerOf) {
    if (data.ownerENS) {
      document.getElementById('tokenOwner').innerHTML = `<strong>Owner: ${data.ownerENS}</strong></br>(<a href="https://etherscan.io/address/${data.ownerOf}" target=_blank>${data.ownerOf}</a>)`;
    } else {
      document.getElementById('tokenOwner').innerHTML = `<strong>Owner:</br><a href="https://etherscan.io/address/${data.ownerOf}" target=_blank>${data.ownerOf}</a></strong>`;
    }
  }
  document.getElementById('tokenDescription').innerHTML = data.description;
  document.getElementById('tokenImage').src = offchainImg;
  // If nftzine, link out to IPFS to view clickable zine
  if (document.getElementById('tokenImage').classList.contains('zineLink')) {
    document.getElementById('tokenImage').onclick = function() {
      window.location.href = `https://gateway.pinata.cloud/ipfs/${data.animation_url}`;
    }
  }
  document.getElementById('tokenOnchainURI').innerHTML = `</br><strong>On-chain Metadata:</strong></br><a href="${onchainMeta}" target=_blank>${data.tokenURI}</a>`;
  document.getElementById('tokenOffchainURI').innerHTML = `</br><strong>Off-chain Metadata:</strong></br><a href="${data.tokenOffchainURI}" target=_blank>${data.tokenOffchainURI}</a>`;
  document.getElementById('tokenOnchainImage').innerHTML = `</br><strong>On-chain Image:</strong></br><a href="${onchainImg}" target=_blank>${data.image}</a>`;
  document.getElementById('tokenOffchainImage').innerHTML = `</br><strong>Off-chain Image:</strong></br><a href="${offchainImg}" target=_blank>${offchainImg}</a>`;
  data.attributes.forEach(function(i){
    let newChild = document.createElement('li');
    newChild.innerHTML = `<span class="tag is-white is-medium"><strong class="pr-1">${i.trait_type}:</strong> ${i.value}</span>`;
    document.getElementById('tokenTraits').appendChild(newChild);
  })
  let buttons = document.getElementById('updateButtons')
  if (buttons) {
    buttons.style.display = 'flex';
  }
}

async function notif(data) {
  new Noty({
    type: data.category,
    theme: 'relax',
    layout: 'topCenter',
    text: data.message,
    timeout: 4500
  }).show();
  return
}
