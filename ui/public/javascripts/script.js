feather.replace();

var app = new Vue({
  el: '#app',
  data: {
    activetab: 0,
    newsfeed: [],
    searchQuery: ''
  },
  methods: {
    summariseArticles: function (articles) {
      let modal = makeModal();
      document.body.appendChild(modal.$el)
      modal.title = articles[0].title;

      let url = '/api/v1.0/newsfeed/get_article_summary';
      let opts = {
        method: 'POST',
        body: JSON.stringify({
          articles: articles
        }),
        headers: {
          'content-type': 'application/json;',
        }
      };

      console.log('Summarising articles...');
      fetch(url, opts)
        .then(response => {
          if (!response.ok || response.success === false) {
            throw new Error("HTTP error " + response.status);
          }
          return response.json()
        })
        .then(data => {
          console.log('Fetched summary.');
          modal.bodyContent = data.summary;
        })
        .catch(error => {
          console.log('Error fetching summary: ' + error);
          modal.bodyContent = 'An error has occurred. Please try again.';
        });
    },

    summariseQuery: function () {
      let modal = makeModal();
      document.body.appendChild(modal.$el)
      modal.title = `Related to "${app.searchQuery}"`;

      let url = '/api/v1.0/newsfeed/get_query_summary?'
      let params = {
        query: app.searchQuery.trim()
      }
      url += new URLSearchParams(params).toString();
      console.log(url);
      let opts = {
        method: 'GET',
        headers: {}
      } 

      console.log('Summarising articles...');
      fetch(url, opts)
        .then(response => {
          if (!response.ok || response.success === false) {
            throw new Error("HTTP error " + response.status);
          }
          return response.json()
        })
        .then(data => {
          console.log(JSON.stringify(data));
          console.log('displaying summary of query ' + data.summary);
          modal.bodyContent = data.summary;
        })
        .catch(error => {
          console.error('Error summarising query: ' + error);
          modal.bodyContent = "An error has occurred. Please try again."
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

function makeModal() {
  let ComponentClass = Vue.extend(Modal)
  let instance = new ComponentClass()
  instance.$mount();
  console.log(instance);
  return instance;
}

docReady(() => {
  let url = '/api/v1.0/newsfeed/get';
  let opts = {
    method: 'GET',
    headers: {}
  };

  fetch(url, opts)
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
                  {{ title }}
                  <!--<a class="animated link" :href=url>{{ title }}</a>-->
                </div>
                <form>
                    <div class="row">
                      <div v-if="bodyContent.length == 0" class="loader-box">
                        <div class="loader"></div>
                        <div class="message">Loading...</div>
                      </div>
                      <div v-else class="row content-text">
                        {{ bodyContent }}
                      </div>
                    </div>
                    <div class="row submit">
                        <input class="button" type="button" value="Dismiss" v-on:click="dismiss()">
                    </div>
                </form>
            </div>
        </div>
    `
};
