window.addEventListener('DOMContentLoaded', async () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');

  // Reload page if Metamask account changes
  if (ethereum) {
    ethereum.on('accountsChanged', function () {
      window.location.reload();
    });
  }

});

up.compiler('#fullscreen_btn', async function(element) {
  fullscreenZine();
})

up.compiler('#tokenTitle', async function(element, data) {
  await updateTokenInfo(data.contractAddress, data.tokenId);
  await updateTokenHistory(data.contractAddress, data.tokenId);
})

up.compiler('#ownerTokens', function(element, data) {
  fetchOwnerTokens(data.contractAddress, data.walletAddress, data.urlSlug);
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

function shortenAddress(a) {
  return a.slice(0, 6) + '...' + a.slice(-4)
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
      } else {
        console.log(`Unreferenced sale:`);
        console.log(sale);
        return
      }
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

async function fetchOwnerTokens(contractAddress, walletAddress, urlSlug) {
  let newColumn;
  let parent = document.getElementById('ownerTokens');
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  const contract = new w3.eth.Contract(erc721Abi, contractAddress);
  const balance = await contract.methods.balanceOf(walletAddress).call();
  if (balance == 0) {
    parent.innerHTML = 'No tokens found for this address.';
    return
  }
  for (i=0; i<balance; i++) {
    if (i % 4 == 0) {
      newColumn = document.createElement('div');
      newColumn.classList.add('row');
      parent.appendChild(newColumn);
    }
    let tokenIndex = await contract.methods.tokenOfOwnerByIndex(walletAddress, i).call();
    let newItem = document.createElement('div');
    newItem.classList.add('three');
    newItem.classList.add('columns');
    newColumn.appendChild(newItem);
    newItem.innerHTML = `<a href="/collection/${urlSlug}/${tokenIndex}" up-target=".container" up-transition="cross-fade" up-preload>
      <img width=40 class="tokenPreview previewPreload" id="tokenPreview-${tokenIndex}" up-data='{ "contractAddress": "${contractAddress}", "tokenId": "${tokenIndex}" }'>
    </a>`;
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
