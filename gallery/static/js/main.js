window.addEventListener('DOMContentLoaded', () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');
});

up.compiler('#tokenTitle', function(element, data) {
  updateTokenInfo(data.contractAddress, data.tokenId)
})

up.compiler('.tokenPreview', function(element, data) {
  updateTokenPreview(data.contractAddress, data.tokenId)
})

up.compiler('.notyBox', function(element, data) {
  notif(data)
})

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
