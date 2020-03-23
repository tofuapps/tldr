feather.replace();

const Modal = {
  data: function () {
    return {
      title: '',
      url: '',
      bodyContent: ''
    }
  },
  methods: {
    dismiss: function () {
      document.body.removeChild(this.$el);
    }
  },
  template: `
        <div class="modal">
            <div class="content">
                <div class="title">
                  <a class="Link" :href=url>{{ title }}</a>
                </div>
                <form>
                    <div class="row">
                      <div v-if="bodyContent.length == 0" class="loader-box">
                        <div class="loader"></div>
                        <div class="message">Loading...</div>
                      </div>
                      <div v-else class="row">
                        {{ bodyContent }}
                      </div>
                    </div>
                    <div class="row submit">
                        <input type="button" value="Ok" v-on:click="dismiss()">
                        <input type="button" value="Cancel" v-on:click="dismiss()">
                    </div>
                </form>
            </div>
        </div>
    `
};

var app = new Vue({
  el: '#app',
  data: {
    activetab: 1,
    message: '', //'Hello Vue!',
    newsfeed: [],
  },
  methods: {
    displaySummary: function (article) {
      var url = '/api/newsfeed/get_article_summary?'
      var params = {
        title: article.title,
        link: article.url
      }
      url += new URLSearchParams(params).toString();
      console.log(url);

      var opts = {
        method: 'GET',
        headers: {}
      };

      let modal = makeModal2(null);
      document.body.appendChild(modal.$el)
      modal.title = article.title;
      modal.url = article.url;

      fetch(url, opts)
        .then(response => response.json())
        .then(data => {
          console.log(JSON.stringify(data));
          console.log('displaying summary of article ' + data.summary);
          modal.bodyContent = data.summary;
        });
    }
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

function makeModal2() {
  var ComponentClass = Vue.extend(Modal)
  var instance = new ComponentClass()
  instance.$mount();
  console.log(instance);
  return instance;
}

function makeModal() {
  let sampleModal = `
        <div class="modal">
            <div class="content">
                <div class="title">
                  {{ modalContent.title }}
                </div>
                <form>
                    <div class="row">
                      <div v-if="modalContent.bodyContent.length == 0" class="loader-box">
                        <div class="loader"></div>
                        <div class="message">Loading...</div>
                      </div>
                      <div v-else class="row">
                        {{ modalContent.bodyContent }}
                      </div>
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
});
