window.addEventListener('DOMContentLoaded', () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');
});

up.compiler('#tokenTitle', function(element, data) {
  updateTokenInfo(data.contractAddress, data.tokenId)
})

up.compiler('#ownerTokens', function(element, data) {
  fetchOwnerTokens(data.contractAddress, data.walletAddress, data.urlSlug)
})

up.compiler('#connectWallet', function(element) {
  armConnectButton();
})

up.compiler('#tokenImage', function(element) {
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
  console.log(data);
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
