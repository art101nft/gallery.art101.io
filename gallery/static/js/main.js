window.addEventListener('DOMContentLoaded', () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');
});

up.compiler('#tokenTitle', function(element, data) {
  updateTokenInfo(data)
})

up.compiler('.tokenPreview', function(element, data) {
  updateTokenPreview(data)
})

up.compiler('.notyBox', function(element, data) {
  notif(data)
})

async function getTokenMetadata(tokenId) {
  let res = await fetch(`/api/v1/get_token_metadata/${tokenId}`)
    .then((resp) => resp.json())
    .then(function(data) {
      return data
    })
  return res
}

function loadImg(_u) {
  if (_u.startsWith('ipfs://')) {
    let stripped = _u.replace('ipfs://', '');
    return `/ipfs/${stripped}`
  } else {
    return _u
  }
}

async function updateTokenPreview(tokenId) {
  let data = await getTokenMetadata(tokenId);
  if (data) {
    let i = document.getElementById('tokenPreview-' + tokenId);
    i.src = loadImg(data.image);
    i.onload = function(){
      i.width = 200;
      i.classList.remove('previewPreload');
    }
  }
}

async function updateTokenInfo(tokenId) {
  let data = await getTokenMetadata(tokenId);
  if (data.from_local) {
    console.log(`Returned JSON payload from locally saved resources`);
  } else {
    console.log(`Returned JSON payload from remote metadata API`);
  }
  if (!data) {
    document.getElementById('tokenTitle').innerHTML = 'Error';
    document.getElementById('tokenDescription').innerHTML = 'Malformed JSON payload';
    document.getElementById('tokenImage').src = '';
    return false
  }
  document.getElementById('tokenTitle').innerHTML = data.name;
  document.getElementById('tokenDescription').innerHTML = data.description;
  document.getElementById('tokenImage').src = loadImg(data.image);
  data.attributes.forEach(function(i){
    let newChild = document.createElement('li');
    newChild.innerHTML = `<span class="tag is-light is-medium"><strong class="pr-1">${i.trait_type}:</strong> ${i.value}</span>`;
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
