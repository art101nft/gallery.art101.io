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

async function getENS(address) {
  const w3 = new Web3(Web3.givenProvider || "http://127.0.0.1:7545");
  const namehash = await w3.eth.call({
    to: '0x084b1c3c81545d370f3634392de611caabff8148', // ENS: Reverse Registrar
    data: w3.eth.abi.encodeFunctionCall({
      name: 'node', type: 'function',
      inputs: [{type: 'address', name: 'addr'}]
    }, [address])
  });
  const res = w3.eth.abi.decodeParameter('string', await w3.eth.call({
    to: '0xa2c122be93b0074270ebee7f6b7292c7deb45047', // ENS: Default Reverse Resolver
    data: w3.eth.abi.encodeFunctionCall({
      name: 'name', type: 'function',
      inputs: [{type: 'bytes32', name: 'hash'}]
    }, [namehash])
  }));
  if (!res) {
    return address;
  } else {
    return res;
  }
}

async function processSale(sale) {
  let from_wallet = await getENS(sale.from_wallet);
  let to_wallet = await getENS(sale.to_wallet);
  if (!from_wallet.endsWith('.eth')) from_wallet = shortenAddress(from_wallet);
  if (!to_wallet.endsWith('.eth')) to_wallet = shortenAddress(to_wallet);
  // let diff = Number((new Date() - new Date(sale.tx_date)) / (24 * 60 * 60 * 1000)).toFixed(2);
  let event, amount;

  if (sale.event_type == 'transfer' && sale.from_wallet == '0x0000000000000000000000000000000000000000') {
    event = 'mint';
  } else {
    event = sale.event_type;
  }

  if (sale.event_type == 'sale') {
    amount = `${new Web3().utils.fromWei(sale.amount.toString())} Ξ`;
  } else {
    amount = '-';
  }

  const tr = document.createElement('tr');
  tr.classList.add(`row-${event}`);
  tr.innerHTML = `
    <td><a href="https://etherscan.io/tx/${sale.tx}" target=_blank>${event}</a></td>
    <td><a href="https://etherscan.io/address/${sale.from_wallet}" target=_blank>${from_wallet}</a></td>
    <td><a href="https://etherscan.io/address/${sale.to_wallet}" target=_blank>${to_wallet}</a></td>
    <td>${sale.platform}</td>
    <td>${amount}</td>
    <td>${new Date(sale.tx_date).toLocaleDateString()}</td>
  `;
  document.getElementById('tokenHistory').appendChild(tr);
}

async function updateTokenHistory(contractAddress, tokenId) {
  const tokenSales = await getTokenSales(contractAddress, tokenId);
  if (tokenSales.length > 0) {
    document.getElementById('tokenHistoryTable').classList.remove('hidden')
    for(i = 0; i < tokenSales.length; i++) {
      await processSale(tokenSales[i]);
    }
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
    newItem.classList.add('previewTokens');
    newColumn.appendChild(newItem);
    newItem.innerHTML = `<a href="/collection/${urlSlug}/${tokenIndex}" up-transition="cross-fade" up-preload>
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
    document.getElementById('tokenImage').src = '';
    return false
  }
  let offchainImg = loadImg(data.image, contractAddress, false);
  let onchainImg = loadImg(data.image, contractAddress, true);
  let onchainMeta = loadImg(data.tokenURI, contractAddress, true);
  document.getElementById('tokenTitle').innerHTML = data.name;
  if (data.ownerOf) {
    if (data.ownerENS) {
      document.getElementById('tokenOwner').innerHTML = `<strong>Owner</strong>: <a href="https://etherscan.io/address/${data.ownerOf}" target=_blank>${data.ownerENS}</a>`;
    } else {
      document.getElementById('tokenOwner').innerHTML = `<strong>Owner</strong>: <a href="https://etherscan.io/address/${data.ownerOf}" target=_blank>${shortenAddress(data.ownerOf)}</a>`;
    }
  }
  document.getElementById('tokenImage').src = offchainImg;
  document.getElementById('tokenImage').classList.remove('previewPreload');
  // If nftzine, load iframe for clickable zine
  if (document.getElementById('tokenImage').classList.contains('zineLink')) {
    let animationURL = loadAssets(contractAddress) + `/${data.animation_url}/index.html`;
    let ifrm = document.createElement('iframe');
    ifrm.setAttribute('src', animationURL);
    ifrm.setAttribute('allowfullscreen', true);
    ifrm.style.width = "100%";
    ifrm.style.height = "50vh";
    document.getElementById('tokenImage').remove();
    document.getElementById('tokenImageHolder').appendChild(ifrm);
  }
  // If rmutt, load model viewer for 3d interactive
  if (
    document.getElementById('tokenImage') 
    && 
    (document.getElementById('tokenImage').classList.contains('glbLink'))
  ) {
    let animationURL = loadAssets(contractAddress) + '/' + data.animation_url.replace('ipfs://', '');
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
    <button id="fullscreen_glb" class="button">
      Fullscreen
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
  document.getElementById('tokenOnchainURI').innerHTML = `<strong>On-chain Metadata</strong>:</br><a href="${onchainMeta}" target=_blank>${data.tokenURI}</a>`;
  document.getElementById('tokenOffchainURI').innerHTML = `<strong>Off-chain Metadata</strong>:</br><a href="${data.tokenOffchainURI}" target=_blank>${data.tokenOffchainURI}</a>`;
  document.getElementById('tokenOnchainImage').innerHTML = `<strong>On-chain Image</strong>:</br><a href="${onchainImg}" target=_blank>${data.image}</a>`;
  document.getElementById('tokenOffchainImage').innerHTML = `<strong>Off-chain Image</strong>:</br><a href="${offchainImg}" target=_blank>${offchainImg}</a>`;
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
