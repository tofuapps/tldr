feather.replace();

var app = new Vue({
  el: '#app',
  data: {
    activetab: 0,
    message: '', //'Hello Vue!',
    newsfeed: []
  }
})

function docReady(fn) {
  // see if DOM is already available
  if (document.readyState === "complete" || document.readyState === "interactive") {
    // call on next available tick
    setTimeout(fn, 1);
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

function makeModal(article) {
  let sampleModal = `
        <div class="modal">
            <div class="content">
                <div class="title">
                </div>
                <form>
                    <div class="row">
                    </div>
                    <div class="row submit">
                        <input type="button" value="Ok">
                        <input type="button" value="Cancel">
                    </div>
                </form>
            </div>
        </div>
    `;

  let modal = document.createElement('div');
  modal.innerHTML = sampleModal;

  modal.querySelector('input[value="Ok"]').addEventListener('click', () => {
    document.body.removeChild(modal);
  });

  modal.querySelector('input[value="Cancel"]').addEventListener('click', () => {
    document.body.removeChild(modal);
  });
  return modal;
}

docReady(() => {
  var opts = {
    method: 'GET',
    headers: {}
  };
  fetch('/api/newsfeed/get', opts)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      console.log(JSON.stringify(data));
      //data[0].articles.forEach(e => {
      //  e.keywords
      //});
      app.newsfeed = data;
      //for (let i = 0; i < data[0].articles.length; ++i) {
      //  newsfeed.articles.push(data[0].articles[i]);
      //}
    });

  document.querySelector('#headlines-container').addEventListener('click', e => {
    console.log(e.target);
    if (e.target.classList.contains('single-summary-btn')) {
      document.body.appendChild(makeModal(null));
    }
  });
  document.body.appendChild(makeModal(null));

  //document.getElementById('summarise-btn').onclick = () => {
  //  let modal = document.createElement('div');
  //  modal.innerHTML = sampleModal;

  //  modal.querySelector('input[value="Ok"]').addEventListener('click', () => {
  //    document.body.removeChild(modal);
  //  });

  //  modal.querySelector('input[value="Cancel"]').addEventListener('click', () => {
  //    document.body.removeChild(modal);
  //  });

  //  document.body.appendChild(modal);
  //};

});
