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
    activetab: 0,
    message: '', //'Hello Vue!',
    newsfeed: [],
    searchQuery: ''
  },
  methods: {
    displaySummary: function (articles) {
      let modal = makeModal2(null);
      document.body.appendChild(modal.$el)
      modal.title = articles[0].title;
      //modal.url = article.url;

      console.log('posting articles ' + JSON.stringify(articles))
      // REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
      //let xhr = new XMLHttpRequest();
      //xhr.open('POST', '/api/v1.0/newsfeed/get_article_summary');
      //xhr.setRequestHeader('Content-Type', 'application/json');
      ////xhr.send(JSON.stringify({articles: articles}));
      //xhr.send(JSON.stringify({"articles": articles}));

      //xhr.onload = function() {
      //  alert(`Loaded: ${xhr.status} ${xhr.response}`);
      //  let data = JSON.parse(xhr.response);
      //  console.log(data);
      //  console.log(JSON.stringify(data));
      //  console.log('displaying summary of article ' + data.summary);
      //  modal.bodyContent = data.summary;
      //};

      //xhr.onerror = function() { // only triggers if the request couldn't be made at all
      //  alert(`Network Error`);
      //};

      fetch('/api/v1.0/newsfeed/get_article_summary', {
        method: 'POST',
        //make sure to serialize your JSON body
        body: JSON.stringify({
          articles: articles
        }),
        headers: {
          //'Accept': 'application/json',
          'content-type': 'application/json;',
        }
      })
      .then(response => {
        if (!response.ok) {                                  // ***
          throw new Error("HTTP error " + response.status);  // ***
        }                                                    // ***
        console.log(response.json);
        return response.json()
      })
      .then(data => {
        //if (response.error || !response.success) {
        //  throw new Error(response.error);  // ***
        //}
        // ...use `response.json`, `response.text`, etc. here
        //let data = response.json();
        console.log(data);
        console.log(JSON.stringify(data));
        console.log('displaying summary of article ' + data.summary);
        modal.bodyContent = data.summary;
      })
      .catch(error => {
        // ...handle/report error
        console.log(error);
      });
    },

    handleSubmit: function () {
      let url = '/api/v1.0/newsfeed/get_query_summary?'
      var params = {
        query: app.searchQuery.trim()
      }
      url += new URLSearchParams(params).toString();
      console.log(url);
      let opts = {
        method: 'GET',
        headers: {}
      } 

      let modal = makeModal2(null);
      document.body.appendChild(modal.$el)
      modal.title = `Related to "${app.searchQuery}"`;
      modal.url = '#';

      fetch(url, opts)
        .then(response => response.json())
        .then(data => {
          console.log(JSON.stringify(data));
          console.log('displaying summary of query ' + data.summary);
          modal.bodyContent = data.summary;
        })
        .catch(err => {
          console.error(err);
          modal.bodyContent = "An error has occurred."
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

  fetch('/api/v1.0/newsfeed/get', opts)
    .then(response => { console.log(response); return response.json() })
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
