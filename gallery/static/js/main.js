window.addEventListener('DOMContentLoaded', async () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');

  // Reload page if Metamask account changes
  if (ethereum) {
    ethereum.on('accountsChanged', function () {
      window.location.reload();
    });
  }

  // Menu clickable on small screens
  const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
  if ($navbarBurgers.length > 0) {
    $navbarBurgers.forEach( el => {
      el.addEventListener('click', () => {
        const target = el.dataset.target;
        const $target = document.getElementById(target);
        el.classList.toggle('is-active');
        $target.classList.toggle('is-active');
      });
    });
  };

  // Click triggers to save the profile/socials in database
  const saveProfile = document.getElementById('saveProfile');
  saveProfile.onclick = async () => {
    saveProfile.classList.add('is-loading')
    let res = await updateProfile();
    if (res == true) {
      saveProfile.classList.add('is-info');
      await notif({'message': 'Your social media info has been saved.', 'category': 'success'});
      closeModal(document.getElementById('profileModal'));
    } else {
      saveProfile.classList.add('is-error')
      await notif({'message': 'Unable to save; something went wrong.', 'category': 'danger'});
    }
    saveProfile.classList.remove('is-loading');
  }

  // Add a click event on buttons to open a specific modal
  (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
    const modal = $trigger.dataset.target;
    const $target = document.getElementById(modal);

    $trigger.addEventListener('click', () => {
      openModal($target);
    });
  });

  // Add a click event on various child elements to close the parent modal
  (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .closeModal') || []).forEach(($close) => {
    const $target = $close.closest('.modal');

    $close.addEventListener('click', () => {
      closeModal($target);
    });
  });

  // Add a keyboard event to close all modals
  document.addEventListener('keydown', (event) => {
    const e = event || window.event;

    if (e.keyCode === 27) { // Escape key
      closeAllModals();
    }
  });

  // Poll for available funds if connected
  if (await isConnected()) {
    await getProfile();
    const btn = document.getElementById('yourProfile');
    btn.classList.remove('hidden');
    // If MetaMask is connected, check for withdrawals
    let withdrawFunds = async () => await _withdrawFunds();
    await withdrawFunds();
    let withdraw = setInterval(withdrawFunds, 15000);
  } else {
    // Otherwise, present connect button before prompting
    const btn = document.getElementById('connectButton');
    btn.classList.remove('hidden');
    btn.onclick = connect;
  }

});

up.compiler('#fullscreen_btn', async function(element) {
  fullscreenZine();
})

up.compiler('.activeBidsOffers', async function(element, data) {
  let events;
  let lowestOffer;
  let msg;
  let bidAmounts = 0;
  let bidCount = 0;
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  if (data.type == 'offers') {
    events = await getCollectionActiveOffers(data.contractAddress, data.urlSlug);
  } else {
    events = await getCollectionActiveBids(data.contractAddress, data.urlSlug);
  }
  lowestOffer = events[0].amount;
  for (i = 0; i < events.length; i++) {
    bidAmounts += events[i].amount;
    bidCount += 1;
    if (events[i].amount < lowestOffer) {
      lowestOffer = events[i].amount;
    }
    if (i % 4 == 0) {
      newColumn = document.createElement('div');
      newColumn.classList.add('columns');
      element.appendChild(newColumn);
      console.log(`Creating new child for index ${i}`)
    }
    let tokenIndex = events[i].token_id;
    console.log(`Found token #${tokenIndex} for sale in contract ${data.contractAddress}`);
    let newItem = document.createElement('div');
    newItem.classList.add('column');
    newColumn.appendChild(newItem);
    newItem.innerHTML = `<div class="card-image" style="max-width: 180px; margin: left;">
              <figure class="image">
                <a href="/collection/${data.urlSlug}/${tokenIndex}" up-target=".container" up-transition="cross-fade" up-preload>
                  <img src="/static/img/loading2.gif" width=40 class="tokenPreview previewPreload" id="tokenPreview-${tokenIndex}" up-data='{ "contractAddress": "${data.contractAddress}", "tokenId": "${tokenIndex}" }'>
                </a>
                <p class="subtext">${w3.utils.fromWei((events[i].amount).toString())} Ξ</p>
              </figure>
            </div>`;

    updateTokenPreview(data.contractAddress, tokenIndex);
  }
  if (data.type == 'offers') {
    msg = `The lowest price currently for sale is ${w3.utils.fromWei(lowestOffer.toString())} Ξ.
    `;
  } else {
    msg = `The average currently open bid is ${w3.utils.fromWei(bidAmounts.toString()) / bidCount} Ξ.<br/>
    Total value of all current bids is ${w3.utils.fromWei(bidAmounts.toString())} Ξ.
    `;
  }
  let sd = document.createElement('p');
  sd.innerHTML = msg;
  sd.classList.add('pb-4');
  element.insertBefore(sd, element.firstChild);
})

up.compiler('#tokenTitle', async function(element, data) {
  await updateTokenInfo(data.contractAddress, data.tokenId);
  await updateTokenHistory(data.contractAddress, data.tokenId);
  const c = await isConnected();
  if (!c) {
    const tokenHistory = document.getElementById('tokenHistory');
    const article = document.createElement('article');
    const msgBody = document.createElement('div');
    article.classList.add('message', 'is-warning')
    msgBody.classList.add('message-body');
    msgBody.innerHTML = 'Please connect your wallet in order to bid/offer tokens.';
    article.appendChild(msgBody);
    tokenHistory.appendChild(article);
    return false;
  } else {
    let updateTokenSales = async () => _updateTokenSales(data.contractAddress, data.tokenId, data.erc1155);
    updateTokenSales();
    let update = setInterval(updateTokenSales, 8000);
    up.destructor(element, () => clearInterval(update));
  }
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

async function isConnected() {
  const accts = await window.ethereum.request({method: 'eth_accounts'});
  if (accts.length > 0) {
    return true;
  } else {
    return false;
  }
}

function connect() {
  switchNetwork();
  const btn = document.getElementById('connectButton');
  btn.classList.add('is-loading');
  btn.disabled = true;
  window.ethereum
    .request({ method: 'eth_requestAccounts' })
    .then(function() {
      window.location.reload();
    })
    .catch((err) => {
      btn.classList.remove('is-loading');
      btn.disabled = false;
      if (err.code === 4001) {
        console.log('Please connect to MetaMask.');
      } else {
        console.error(err);
      }
    });
}

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

async function updateTokenHistory(contractAddress, tokenId) {
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  const tokenHistory = document.getElementById('tokenHistory');
  const tokenSales = await getTokenSales(contractAddress, tokenId);
  if (tokenSales.length > 0) {
    tokenSales.forEach(function(sale) {
      let msgColor;
      let msgText;
      const msInDay = 24 * 60 * 60 * 1000;
      const now = new Date();
      const txDate = new Date(sale.tx_date);
      let diff = ((now - txDate) / msInDay).toFixed(2);
      if (sale.event_type == 'sale') {
        msgColor = 'is-success';
        msgText = `Sold for <strong>${w3.utils.fromWei(sale.amount.toString())} Ξ</strong> by <a href="https://etherscan.io/address/${sale.from_wallet}" target="_blank">${shortenAddress(sale.from_wallet)}</a> to <a href="https://etherscan.io/address/${sale.to_wallet}" target="_blank">${shortenAddress(sale.to_wallet)}</a> <strong>${diff} days ago</strong> in tx <a href="https://etherscan.io/tx/${sale.tx}" target="_blank">${shortenAddress(sale.tx)}</a> via ${sale.platform.toUpperCase()}`;
      } else if (sale.event_type == 'transfer' && sale.from_wallet == '0x0000000000000000000000000000000000000000') {
        msgColor = 'is-info';
        msgText = `Minted by <a href="https://etherscan.io/address/${sale.to_wallet}" target="_blank">${shortenAddress(sale.to_wallet)}</a> <strong>${diff} days ago</strong> in tx <a href="https://etherscan.io/tx/${sale.tx}" target="_blank">${shortenAddress(sale.tx)}</a>`;
      } else if (sale.event_type == 'transfer') {
        msgColor = 'is-dark';
        msgText = `Transferred from <a href="https://etherscan.io/address/${sale.from_wallet}" target="_blank">${shortenAddress(sale.from_wallet)}</a> to <a href="https://etherscan.io/address/${sale.to_wallet}" target="_blank">${shortenAddress(sale.to_wallet)}</a> <strong>${diff} days ago</strong> in tx <a href="https://etherscan.io/tx/${sale.tx}" target="_blank">${shortenAddress(sale.tx)}</a>`;
      } else if (sale.event_type == 'tokenoffered') {
        msgColor = 'is-warning';
        msgText = `Offered by owner <strong>${diff} days ago</strong> for ${w3.utils.fromWei(sale.amount.toString())} Ξ in tx <a href="https://etherscan.io/tx/${sale.tx}" target="_blank">${shortenAddress(sale.tx)}</a>`;
      } else if (sale.event_type == 'tokennolongerforsale') {
        msgColor = 'is-danger';
        msgText = `Offer revoked <strong>${diff} days ago</strong> in tx <a href="https://etherscan.io/tx/${sale.tx}" target="_blank">${shortenAddress(sale.tx)}</a>`;
      } else if (sale.event_type == 'tokenbidentered') {
        msgColor = 'is-warning';
        msgText = `Bid entered <strong>${diff} days ago</strong> for ${w3.utils.fromWei(sale.amount.toString())} Ξ in tx <a href="https://etherscan.io/tx/${sale.tx}" target="_blank">${shortenAddress(sale.tx)}</a>`;
      } else {
        console.log(`Unreferenced sale:`);
        console.log(sale);
        return
      }
      // TokenTransfer
      // TokenOffered
      // TokenBidEntered
      // TokenBidWithdrawn
      // TokenBought
      // TokenNoLongerForSale
      const article = document.createElement('article');
      const msgBody = document.createElement('div');
      article.classList.add('message', msgColor)
      msgBody.classList.add('message-body');
      msgBody.innerHTML = msgText;
      article.appendChild(msgBody);
      tokenHistory.appendChild(article);
    })
  } else {
    const article = document.createElement('article');
    const msgBody = document.createElement('div');
    article.classList.add('message', 'is-danger')
    msgBody.classList.add('message-body');
    msgBody.innerHTML = 'Unable to load token history at this time. Check again later.';
    article.appendChild(msgBody);
    tokenHistory.appendChild(article);
  }
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
    newItem.innerHTML = `<div class="card-image" style="max-width: 200px; margin: auto;">
              <figure class="image">
                <a href="/collection/${urlSlug}/${tokenIndex}" up-target=".container" up-transition="cross-fade" up-preload>
                  <img src="/static/img/loading2.gif" width=40 class="tokenPreview previewPreload" id="tokenPreview-${tokenIndex}" up-data='{ "contractAddress": "${contractAddress}", "tokenId": "${tokenIndex}" }'>
                </a>
              </figure>
            </div>`;
    updateTokenPreview(contractAddress, tokenIndex);
  };

}

async function getTokenSales(contractAddress, tokenId) {
  let res = await fetch(`/api/v1/get_token_sales/${contractAddress}/${tokenId}`)
    .then((resp) => resp.json())
    .then(function(data) {
      return data
    })
  return res
}

async function getCollectionActiveBids(contractAddress) {
  let res = await fetch(`/api/v1/get_collection_active_bids/${contractAddress}`)
    .then((resp) => resp.json())
    .then(function(data) {
      return data
    })
  return res
}

async function getCollectionActiveOffers(contractAddress) {
  let res = await fetch(`/api/v1/get_collection_active_offers/${contractAddress}`)
    .then((resp) => resp.json())
    .then(function(data) {
      return data
    })
  return res
}

async function getCollectionEvents(contractAddress) {
  let res = await fetch(`/api/v1/get_collection_events/${contractAddress}`)
    .then((resp) => resp.json())
    .then(function(data) {
      return data
    })
  return res
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
  // If nftzine, load iframe for clickable zine
  if (document.getElementById('tokenImage').classList.contains('zineLink')) {
    let animationURL = loadAssets(contractAddress) + `/${data.animation_url}/index.html`;
    let ifrm = document.createElement('iframe');
    ifrm.setAttribute('src', animationURL);
    ifrm.setAttribute('allowfullscreen', true);
    ifrm.style.width = "640px";
    ifrm.style.height = "480px";
    document.getElementById('tokenImage').remove();
    document.getElementById('tokenImageHolder').appendChild(ifrm);
  }
  // If rmutt, load model viewer for 3d interactive
  if (document.getElementById('tokenImage').classList.contains('glbLink')) {
    let animationURL = loadAssets(contractAddress) + '/' + data.animation_url.replace('ipfs://', '');
    // let placeholderImg = data.image.replace('ipfs://', '')
    let modelViewer = `
      <model-viewer style="background: ${data.background_color}" id="glb" bounds="tight" src="${animationURL}" enable-pan ar ar-modes="webxr scene-viewer quick-look" camera-controls environment-image="neutral" poster="${offchainImg}" shadow-intensity="1" exposure="0.9" shadow-softness="0" camera-orbit="-45deg 75deg auto">
      <div class="progress-bar hide" slot="progress-bar">
          <div class="update-bar"></div>
      </div>
      <button slot="ar-button" id="ar-button">
          View in your space
      </button>
      <div id="ar-prompt">
          <img src="/static/img/ar_hand_prompt.png">
      </div>
    </model-viewer>
    <button id="fullscreen_glb" style="width: 40px">
    <svg version="1.1" viewBox="0 0 36 36">
    <path d="m 10,16 2,0 0,-4 4,0 0,-2 L 10,10 l 0,6 0,0 z"></path>
    <path d="m 20,10 0,2 4,0 0,4 2,0 L 26,10 l -6,0 0,0 z"></path>
    <path d="m 24,24 -4,0 0,2 L 26,26 l 0,-6 -2,0 0,4 0,0 z"></path>
    <path d="M 12,20 10,20 10,26 l 6,0 0,-2 -4,0 0,-4 0,0 z"></path>
    </svg>
    </button>`;
    document.getElementById('tokenImage').remove();
    document.getElementById('tokenImageHolder').innerHTML = modelViewer;
    // Handles loading the events for <model-viewer>'s slotted progress bar
    const onProgress = (event) => {
      const progressBar = event.target.querySelector('.progress-bar');
      const updatingBar = event.target.querySelector('.update-bar');
      updatingBar.style.width = `${event.detail.totalProgress * 100}%`;
      if (event.detail.totalProgress === 1) {
        progressBar.classList.add('hide');
      } else {
        progressBar.classList.remove('hide');
        if (event.detail.totalProgress === 0) {
          event.target.querySelector('.center-pre-prompt').classList.add('hide');
        }
      }
    };
    document.querySelector('#fullscreen_glb').addEventListener('click', () => {
      if (document.fullscreen) {
          for (let name of ['exitFullscreen','mozExitFullscreen','webkitExitFullscreen']) {
              let fn = document[name];
              if (fn) return fn.call(document);
          }
      } else {
          let bg = document.querySelector('#glb');
          for (let name of ['requestFullscreen','mozRequestFullscreen','webkitRequestFullscreen']) {
              let fn = bg[name];
              if (typeof fn === 'function') return fn.call(bg);
          }
      }
    });
    document.querySelector('model-viewer').addEventListener('progress', onProgress);
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

function fullscreenZine(divId) {
  document.querySelector('#fullscreen_btn').addEventListener('click', () => {
    if (document.fullscreen) {
        for (let name of ['exitFullscreen','mozExitFullscreen','webkitExitFullscreen']) {
            let fn = document[name];
            if (fn) return fn.call(document);
        }
    } else {
        let bg = document.querySelector('#bg');
        for (let name of ['requestFullscreen','mozRequestFullscreen','webkitRequestFullscreen']) {
            let fn = bg[name];
            if (typeof fn === 'function') return fn.call(bg);
        }
    }
  });
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

function openModal($el) {
  $el.classList.add('is-active');
}

function closeModal($el) {
  $el.classList.remove('is-active');
}

function closeAllModals() {
  (document.querySelectorAll('.modal') || []).forEach(($modal) => {
    closeModal($modal);
  });
}

async function getProfile() {
  let acct = await getMetamaskAccount();
  await fetch(`/api/v1/check_address_exists?address=${acct}`)
    .then((resp) => resp.json())
    .then(async function(data) {
        if (!data['success']) {
          return
        }
        if (data['socials']['discord']) document.getElementById('discordHandle').value = '******';
        if (data['socials']['twitter']) document.getElementById('twitterHandle').value = '******';
        if (data['socials']['email']) document.getElementById('emailAddress').value = '******';
      });
}

async function updateProfile() {
  const acct = await getMetamaskAccount();
  let res1 = await fetch(`/api/v1/check_address_exists?address=${acct}`)
    .then((resp) => resp.json())
    .then(async function(data) {
        if (!data['success']) {
          console.log('error checking if address exists!')
          return
        }
        nonce = data['nonce'];
        const msg = `Authentication request from Art101 Gallery app!
        This will not cost any gas, it is simply a check to confirm you
        own this address so that we can store some social media info to
        notify you of marketplace events. Verifying message with nonce ${nonce}`;
        const signedData = await window.ethereum.request({
          method: 'personal_sign',
          params: [msg, acct]
        });

        let res2 = await fetch('/api/v1/save_profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json;charset=utf-8'
          },
          body: JSON.stringify({
            'signed_data': signedData,
            'address': acct,
            'nonce': nonce,
            'message': msg,
            'twitter': document.getElementById('twitterHandle').value,
            'discord': document.getElementById('discordHandle').value,
            'email': document.getElementById('emailAddress').value
          })
        })
          .then((resp) => resp.json())
          .then(function(data) {
              if (data['success']) {
                return true
              } else {
                return false
              }
          });
        return res2;
    });
    return res1;
}
